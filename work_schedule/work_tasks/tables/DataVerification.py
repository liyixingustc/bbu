import simplejson
from common.Errors import ProcessingError
from common.Types import DataVerificationType
from common.HTNGConstants import HtngConstants
from common.Types import ResourceOriginTypes
from processing.Classes import ReservationDuplicateInfo
from dao.ReservationDAO import ReservationDAO
from dao.AggregateDAO import AggregateDAO
from dao.PropertyDAO import PropertyDAO
from dao.GroupDAO import GroupDAO
from processing.Requests import DataVerificationResult
from managers.DataManager import DataManager
from managers.ConnectionManager import ConnectionManager
from managers.QueueManager import (InboundQueueManager, OutboundQueueManager)
from schemas.OperaRezRecordSchema import OperaRezRecordSchema
from managers.TraceManager import trace
from util.UData import UData
from util.UDate import UDate
from util.UList import UList
from util.UString import UString
from util.UCollection import UCollection
from util.UFile import default_json_serializer


class DataVerification(object):

    def __init__(self):
        self.__reservation_dao = ReservationDAO()
        self.__aggregate_dao = AggregateDAO()
        self.__property_dao = PropertyDAO()
        self.__group_dao = GroupDAO()

    def __load_aggregates(self, property_id, as_of_date):
        as_of_date = UDate.dateTimeToDate(as_of_date)
        documents = UCollection.aggregate(
            collection=self.__aggregate_dao.collection,
            pipeline=[
                {
                    "$match": {
                        'property_id': property_id,
                        'as_of_date': as_of_date,
                        'stay_date': {'$gte': as_of_date}
                    }
                },
                {
                    "$group": {
                        "_id": {"asOf": "$as_of_date", "stay_date": "$stay_date"},
                        "rooms": {"$sum": '$rooms'},
                        'revenue': {"$sum": '$revenue'}
                     }
                }
            ])
        result = {}
        for item in documents:
            stay_date = UDate.dateToStr(item['_id']['stay_date'])
            result[stay_date] = {
                'rooms': item['rooms'],
                'revenue': item['revenue']
            }
        return result

    def __load_reservations(self, property_id, as_of_date=None, days=366):
        if as_of_date is None:
            as_of_date = DataManager.get_property_local_date(property_id)
        result = {}
        date_range = UDate.getDaysList(as_of_date, UDate.next(as_of_date, days))
        for stay_date in date_range:
            stay_date_str = UDate.dateToStr(stay_date)
            count = self.__reservation_dao.get_stays_count(property_id, stay_date, ['RESERVED','CHECKED IN','CHECKED OUT','DUE IN','DUE OUT','Reserved'])
            trace("Stay date {0}: {1} reservation(s) found".format(stay_date_str, count))
            result[stay_date_str] = count
        return result

    def __load_groups_data(self, property_id, as_of_date):
        documents = UCollection.aggregate(
            collection=self.__group_dao.collection,
            pipeline=[
                {
                    '$match': {
                        'property_id': property_id,
                        'cutoff_date': {'$gte': as_of_date}
                    }
                },
                {
                    '$group': {
                        '_id': {'stay_date': '$stay_date'},
                        'rooms_count': {'$sum': '$rooms_count'},
                        'rooms_pickup': {'$sum': '$pickup'},
                        'rooms_avail': {'$sum': '$avail'},
                        'rooms_allotted': {'$sum': '$allotted'}
                    }
                },
                {
                    '$sort': {
                        '_id.stay_date': 1
                    }
                }
            ])
        result = {}
        if UList.any(documents):
            for item in documents:
                date = item['_id']['stay_date']
                stayDate = UDate.dateToStr(date)
                result[stayDate] = {
                    'rooms_count': item['rooms_count'],
                    'rooms_pickup': item['rooms_pickup'],
                    'rooms_avail': item['rooms_avail'],
                    'rooms_allotted': item['rooms_allotted']
                }
        return result

    def __search_transient_duplicated_reservations(self, property_id, stay_date, reservation_statuses=None):
        stay_date = UDate.dateTimeToDate(stay_date)
        match_query = {
            'property_id': property_id,
            'arrival_date': {'$lte': UDate.dateToStr(stay_date)},
            'departure_date': {'$gte': UDate.dateToStr(UDate.next(stay_date))},
            'block_code': {'$eq': None}
        }
        if UList.any(reservation_statuses):
            match_query['reservation_status'] = {'$in': reservation_statuses}
        documents = UCollection.aggregate(
            collection=self.__reservation_dao.collection,
            pipeline=[
                {
                    "$match": match_query
                },
                {
                    "$group": {
                        "_id": {
                            "property_id": "$property_id",
                            "market_code": "$market_code",
                            "arrival_date": "$arrival_date",
                            "departure_date": "$departure_date",
                            "booking_date": "$booking_date",
                            "room_type": "$room_type",
                            "rate_code": "$rate_code",
                            "rate_amount": "$rate_amount"
                        },
                        "count": {"$sum": 1}
                     }
                }
            ])
        result = []
        for item in documents:
            key = item['_id']
            count = item['count']
            if count > 1:
                info = ReservationDuplicateInfo()
                info.count = count
                info.property_id = key["property_id"]
                info.booking_date = key["booking_date"]
                info.arrival_date = key["arrival_date"]
                info.departure_date = key["departure_date"]
                info.market_code = key["market_code"]
                info.room_type = key["room_type"]
                info.rate_code = key["rate_code"]
                info.rate_amount = key["rate_amount"]
                result.append(info)
        return result

    def __process_forecast_check(self, request):
        prp = self.__property_dao.find(request.property_id)
        if prp is None:
            raise Exception("Property '{0}' was not found".format(request.property_id))
        if UString.is_none_or_empty(request.file_path):
            request.file_path = "{0} - {1}".format(request.verification_type, request.property_id)
        lines = []
        line = UString.combine([
            'Property Id',
            'As Of Date',
            'Stay Date',
            'Reservations',
            'Aggregated Rooms',
            'Aggregated Revenue',
            'Difference (rooms)',
            'Group Rooms Count',
            'Group Rooms Pickup',
            'Group Rooms Avail',
            'Group Rooms Allotted'])
        lines.append(line)
        groups = self.__load_groups_data(request.property_id, request.as_of_date)
        as_of_date_str = UDate.dateToStr(request.as_of_date)
        trace("As of date: {0}..\n".format(as_of_date_str))
        aggregates = self.__load_aggregates(request.property_id, request.as_of_date)
        reservations = self.__load_reservations(request.property_id, request.as_of_date)
        for stay_date, reservations_rooms in reservations.iteritems():
            aggregates_stay_date = aggregates.get(stay_date)
            aggregates_rooms = 0
            aggregates_revenue = 0.0
            if aggregates_stay_date is not None:
                aggregates_rooms = aggregates_stay_date['rooms']
                aggregates_revenue = aggregates_stay_date['revenue']
            room_diff = reservations_rooms - aggregates_rooms
            group_rooms_count = 0
            group_rooms_pickup = 0
            group_rooms_avail = 0
            group_rooms_allotted = 0
            group = groups.get(stay_date)
            if group is not None:
                if 'rooms_count' in group:
                    group_rooms_count = group['rooms_count']
                if 'rooms_pickup' in group:
                    group_rooms_pickup = group['rooms_pickup']
                if 'rooms_avail' in group:
                    group_rooms_avail = group['rooms_avail']
                if 'rooms_allotted' in group:
                    group_rooms_allotted = group['rooms_allotted']
            line = UString.combine([
                request.property_id,
                as_of_date_str,
                stay_date,
                reservations_rooms,
                aggregates_rooms,
                UData.money_to_str(aggregates_revenue),
                room_diff,
                group_rooms_count,
                group_rooms_pickup,
                group_rooms_avail,
                group_rooms_allotted])
            lines.append(line)
        return UString.combine(lines, '\n')

    def __process_actuals_check(self, request):
        prp = self.__property_dao.find(request.property_id)
        if prp is None:
            raise Exception("Property '{0}' was not found".format(request.property_id))
        property_date = prp.get_local_date()
        if UString.is_none_or_empty(request.file_path):
            request.file_path = "{0} - {1}".format(request.verification_type, request.property_id)
        lines = []
        line = UString.combine([
            'Stay Date',
            'Total',
            'Reserved',
            'No-show',
            'Current',
            'Actualized'])
        lines.append(line)
        from_date = UDate.dateTimeToDate(self.__reservation_dao.get_min_arrival_date(request.property_id))
        end_date = UDate.dateTimeToDate(UDate.previous(property_date))
        date_range = UDate.getDaysList(from_date, end_date)
        for stay_date in date_range:
            stay_date_str = UDate.dateToStr(stay_date)
            reserved_count = self.__reservation_dao.get_stays_count(
                property_id=request.property_id,
                stay_date=stay_date,
                reservation_statuses=[HtngConstants.ResStatus.Reserved])
            noshow_count = self.__reservation_dao.get_arrivals_count(
                property_id=request.property_id,
                stay_date=stay_date,
                reservation_statuses=[HtngConstants.ResStatus.NoShow])
            total_count = reserved_count + noshow_count
            aggregates_result = {
                -1: {'value': None, 'difference': None},
                0: {'value': None, 'difference': None}
            }
            aggregates = self.__aggregate_dao.get_actuals(
                property_id=request.property_id,
                as_of_date=stay_date,
                days_out_list=[0, -1])
            if UList.any(aggregates):
                for aggregate in aggregates:
                    days_out = aggregate['_id']['days_out']
                    aggregate_result = aggregates_result[aggregate['_id']['days_out']]
                    aggregate_result['value'] = aggregate['rooms']
                    if days_out == 0:
                        aggregate_result['difference'] = aggregate['rooms'] - total_count

            aggregates_current = aggregates_result[0]
            aggregates_actual = aggregates_result[-1]

            current_aggregates = 'N/A'
            if aggregates_current['value'] is not None:
                current_aggregates = UData.value_to_str(aggregates_current['value'])
                difference = aggregates_current['difference']
                if difference != 0:
                    current_aggregates += " ({0}{1})".format(UString.if_then(difference > 0, "+", "-"), abs(difference))
            trace("{0} - total: {1}, reserved: {2}, no-show: {3}, aggregates: {4}".format(
                stay_date_str,
                total_count,
                reserved_count,
                noshow_count,
                current_aggregates,
                aggregates_actual['value']))
            line = UString.combine([
                stay_date_str,
                total_count,
                reserved_count,
                noshow_count,
                current_aggregates,
                aggregates_actual['value']])
            lines.append(line)
        return UString.combine(lines, '\n')

    def __process_stay_check(self, request):
        prp = self.__property_dao.find(request.property_id)
        if prp is None:
            raise Exception("Property '{0}' was not found".format(request.property_id))
        if UString.is_none_or_empty(request.file_path):
            request.file_path = "{0} - {1}".format(request.verification_type, request.property_id)
        lines = []
        line = UString.combine([
            'Stay Date',
            'Rooms by reservations',
            'Rooms by reservation stays',
            'Diff'])
        lines.append(line)
        from_date = self.__reservation_dao.get_min_arrival_date(request.property_id)
        through_date = self.__reservation_dao.get_max_departure_date(request.property_id)
        date_range = UDate.getDaysList(from_date, through_date)
        for stay_date in date_range:
            stay_date_str = UDate.dateToStr(stay_date)
            reservations = self.__reservation_dao.get_reservations_stayed_on(
                property_id=request.property_id,
                stay_date=stay_date)
            reservations_rooms = len(reservations)
            reservations_stays = 0
            for reservation in reservations:
                len_count = len(reservation.room_stays)
                diff = reservation.num_nights - len_count
                if diff != 0:
                    trace(
                        "\tWarning: Reservation {0}: arrival: {1}, departure: {2}, nights: {3}, stays: {4} ({5})".format(
                            reservation.reservation_id,
                            reservation.arrival_date,
                            reservation.departure_date,
                            reservation.num_nights,
                            len_count,
                            diff))
                for stay in reservation.room_stays:
                    if stay['stay_date'] == stay_date_str:
                        reservations_stays += 1
            trace("Stay date: {0} - res. rooms: {1}, res. stays: {2} ({3})..".format(
                stay_date_str,
                reservations_rooms,
                reservations_stays,
                (reservations_rooms-reservations_stays),
            ))
            line = UString.combine([
                stay_date_str,
                reservations_rooms,
                reservations_stays,
                (reservations_rooms-reservations_stays)])
            lines.append(line)
        return UString.combine(lines, '\n')

    def __process_duplicated_reservations_check(self, request):
        prp = self.__property_dao.find(request.property_id)
        if prp is None:
            raise Exception("Property '{0}' was not found".format(request.property_id))
        if UString.is_none_or_empty(request.file_path):
            request.file_path = "{0} - {1}".format(request.verification_type, request.property_id)
        lines = []
        line = UString.combine([
            'Stay Date',
            'Count',
            'Booking Date',
            'Arrival Date',
            'Departure Date',
            'Market Code',
            'Room Type',
            'Rate Code',
            'Rate Amount'])
        lines.append(line)
        from_date = self.__reservation_dao.get_min_arrival_date(request.property_id)
        through_date = self.__reservation_dao.get_max_departure_date(request.property_id)
        date_range = UDate.getDaysList(from_date, through_date)
        for stay_date in date_range:
            stay_date_str = UDate.dateToStr(stay_date)
            infos = self.__search_transient_duplicated_reservations(
                property_id=request.property_id,
                stay_date=stay_date)
            if UList.any(infos):
                line = UString.combine([
                    stay_date_str,
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    ''
                ])
                lines.append(line)
                for info in infos:
                    trace(
                        "{0} - {1} reservation(s): booked: {2}, stay: {3} / {4}, market code: {5}, room type: {6}, rate plan: {7}".format(
                            stay_date_str,
                            UData.value_to_str(info.count),
                            info.booking_date,
                            info.arrival_date,
                            info.departure_date,
                            info.market_code,
                            info.room_type,
                            info.rate_code,
                            UData.money_to_str(info.rate_amount)))
                    line = UString.combine([
                        '',
                        UData.value_to_str(info.count),
                        info.booking_date,
                        info.arrival_date,
                        info.departure_date,
                        UString.if_then(UString.is_none_or_empty(info.market_code), '', info.market_code),
                        UString.if_then(UString.is_none_or_empty(info.room_type), '', info.room_type),
                        UString.if_then(UString.is_none_or_empty(info.rate_code), '', info.rate_code),
                        UData.money_to_str(info.rate_amount)])
                    lines.append(line)
        return UString.combine(lines, '\n')

    def __process_daily_revenue(self, request):
        stay_date = UDate.dateTimeToDate(request.stay_date)
        stay_date_str = UDate.dateToStr(stay_date)
        prp = self.__property_dao.find(request.property_id)
        if prp is None:
            raise Exception("Property '{0}' was not found".format(request.property_id))
        if UString.is_none_or_empty(request.file_path):
            request.file_path = "{0} - {1}".format(request.verification_type, request.property_id)
        market_codes = []
        if not UString.is_none_or_empty(request.market_code):
            market_codes = request.market_code.split(';')
        lines = []
        line = UString.combine([
            'Entity',
            'Id',
            'Stay Date',
            'Market Code',
            'Room Revenue',
            'Room Count',
            'Rate Plan Code',
            'Room Type Code',
            'Group Block Code'])
        lines.append(line)
        stay_throught_reservations = self.__reservation_dao.get_many(
            query={
                'property_id': request.property_id,
                'reservation_status': HtngConstants.ResStatus.Reserved,
                'arrival_date': {'$lte': stay_date_str},
                'departure_date': {'$gt': stay_date_str}
            })
        one_day_reservations = self.__reservation_dao.get_many(
            query={
                'property_id': request.property_id,
                'reservation_status': HtngConstants.ResStatus.Reserved,
                'arrival_date': {'$eq': stay_date_str},
                'departure_date': {'$eq': stay_date_str}
            })
        reservations = UList.combine(stay_throught_reservations, one_day_reservations)
        if UList.any(reservations):
            for reservation in reservations:
                found = False
                for room_stay in reservation.room_stays:
                    if UString.equals(room_stay.get('stay_date'), stay_date_str):
                        found = True
                        if UList.any(market_codes) and not UString.includes(room_stay['market_code'], market_codes):
                            continue
                        rate_plan_code = room_stay.get('rate_code')
                        room_type_code = room_stay.get('room_type')
                        line = UString.combine([
                            'Reservation',
                            reservation.reservation_id,
                            room_stay['stay_date'],
                            room_stay['market_code'],
                            room_stay['rate_amount'],
                            OperaRezRecordSchema.get_room_count(room_stay),
                            UString.if_then(UString.is_none_or_empty(rate_plan_code), '', rate_plan_code),
                            UString.if_then(UString.is_none_or_empty(room_type_code), '', room_type_code),
                            UString.if_then(UString.is_none_or_empty(reservation.block_code), '', reservation.block_code)])
                        lines.append(line)
                if not found:
                    line = UString.combine([
                        'Reservation',
                        reservation.reservation_id,
                        stay_date_str,
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        'n/a',
                        UString.if_then(UString.is_none_or_empty(reservation.block_code), '', reservation.block_code)])
                    lines.append(line)

        group_blocks = self.__group_dao.find_active_group_blocks(
            property_id=request.property_id,
            cutof_date=request.as_of_date)
        if UList.any(group_blocks):
            for group_block in group_blocks:
                if UDate.equals(group_block.stay_date, stay_date):
                    if UList.any(market_codes) and not UString.includes(group_block.market_code, market_codes):
                        continue
                    rooms = group_block.get_rooms_count()
                    line = UString.combine([
                        'Group',
                        group_block.inv_block_code,
                        UDate.dateToStr(group_block.stay_date),
                        group_block.market_code,
                        group_block.rate_pax1 * rooms,
                        rooms,
                        group_block.rate_plan,
                        group_block.room_type,
                        group_block.inv_block_code])
                    lines.append(line)
        return UString.combine(lines, '\n')

    def __process_reservation_trace(self, request):

        prp = self.__property_dao.find(request.property_id)
        if prp is None:
            raise Exception("Property '{0}' was not found".format(request.property_id))

        reservation = self.__reservation_dao.find_reservation(
            property_id=request.property_id,
            reservation_id=request.entity_id)

        if reservation is None:
            raise Exception("Reservation was not found - property_id: {0}, reservation_id: {1}".format(request.property_id, request.entity_id))

        lines = []
        lines.append("Reservation {0}, property {0} ({1})".format(
            request.entity_id,
            prp.property_id,
            prp.property_name))
        lines.append("")
        lines.append("")
        lines.append("JSON object:")
        lines.append("")
        lines.append(simplejson.dumps(reservation.schema, default=default_json_serializer))
        lines.append("")

        if not UString.is_none_or_empty(reservation.data_source_name):
            partner_code = reservation.data_source_name
            correlation_ids = []
            if UString.equals(reservation.file_resource_location, ResourceOriginTypes.CorrelationId):
                correlation_ids.append(reservation.file_resource_name)
            versions = reservation.get_versions()
            if UList.any(versions):
                for version in versions:
                    if UString.equals(version.file_resource_location, ResourceOriginTypes.CorrelationId):
                        correlation_ids.append(version.file_resource_name)
            if UList.any(correlation_ids):
                # load inbound messages
                queue_manager = InboundQueueManager()
                queues = []
                for correlation_id in correlation_ids:
                    queue = queue_manager.load_queue_by_message_query(
                        query={
                            'partner': partner_code,
                            'correlation_id': correlation_id
                        })
                    if queue is not None:
                        queues.append(queue)
                if UList.any(queues):
                    queues.sort(cmp=None, key=lambda i: i.created_on)
                    for queue in queues:
                        if queue is not None:
                            lines.append("")
                            lines.append("")
                            lines.append("Inbound {0}, created on '{1}'".format(queue.message.message_type, UDate.dateTimeToStr(queue.message.created_on)))
                            lines.append("")
                            trace = queue.message.trace
                            if UList.any(trace):
                                for entries in trace:
                                    for entry_name in entries:
                                        lines.append(entry_name)
                                        lines.append("")
                                        data = entries[entry_name]
                                        if not UString.is_none_or_empty(data):
                                            #data = UString.replace(data, '\"', '')
                                            lines.append(data)
                                            lines.append("")

                # load outbound messages
                queues = []
                queue_manager = OutboundQueueManager()
                for correlation_id in correlation_ids:
                    queue = queue_manager.load_queue_by_message_query(
                        query={
                            'partner': partner_code,
                            'relates_to_correlation_id': correlation_id
                        })
                    if queue is not None:
                        queues.append(queue)

                if UList.any(queues):
                    queues.sort(cmp=None, key=lambda i: i.created_on)
                    for queue in queues:
                        if queue is not None:
                            lines.append("")
                            lines.append("")
                            lines.append("Outbound {0}, created on '{1}'".format(queue.message.message_type, UDate.dateTimeToStr(queue.message.created_on)))
                            lines.append("")
                            trace = queue.message.trace
                            if UList.any(trace):
                                for entries in trace:
                                    for entry_name in entries:
                                        lines.append(entry_name)
                                        lines.append("")
                                        data = entries[entry_name]
                                        if not UString.is_none_or_empty(data):
                                            data = UString.replace(data, '\"', '')
                                            lines.append(data)
                                            lines.append("")

        return UString.combine(lines, '\n')

    def process(self, request):
        if request.as_of_date is None:
            request.as_of_date = DataManager.get_property_local_date(request.property_id)
        if UString.is_none_or_empty(request.file_path):
            request.file_path = "{0} - {1} - {2} (4).csv".format(
                request.verification_type,
                request.property_id,
                request.as_of_date,
                UDate.get_time_stamp())
        result = DataVerificationResult("Collecting data and saving into '{0}' (type: '{1}')".format(
            request.file_path,
            request.verification_type))
        result.start()
        try:
            if UString.equals(request.verification_type, DataVerificationType.ForecastCheck):
                result.data = self.__process_forecast_check(request)
            elif UString.equals(request.verification_type, DataVerificationType.ActualsCheck):
                result.data = self.__process_actuals_check(request)
            elif UString.equals(request.verification_type, DataVerificationType.StayCheck):
                result.data = self.__process_stay_check(request)
            elif UString.equals(request.verification_type, DataVerificationType.DuplicatedReservationsCheck):
                result.data = self.__process_duplicated_reservations_check(request)
            elif UString.equals(request.verification_type, DataVerificationType.DailyRevenue):
                result.data = self.__process_daily_revenue(request)
            elif UString.equals(request.verification_type, DataVerificationType.ReservationTrace):
                result.data = self.__process_reservation_trace(request)
            else:
                raise Exception("Unspecified verification type: {0}".format(request.verification_type))
            result.stop()
            trace(result.report())
            return result
        except Exception as e:
            raise ProcessingError(
                "Unable to process report '{0}' (type: '{1}'). {2}".format(
                    request.file_path,
                    request.verification_type,
                    e.message))
