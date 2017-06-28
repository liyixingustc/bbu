/**
 * Created by caliburn on 17-5-28.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        // bootstrap table extensions
        moment = require('moment'),
        jqueryUI = require('jquery-ui'),
        fullcalendar = require('fullcalendar'),
        scheduler = require('scheduler');

    var fullDate = new Date();
    //convert month to 2 digits
    var twoDigitMonth = ((fullDate.getMonth().length+1) === 1)? (fullDate.getMonth()+1) : '0' + (fullDate.getMonth()+1);
    var currentDate = fullDate.getFullYear() + "-" + twoDigitMonth + "-" + fullDate.getDate();
	var $WorkScheduler_Panel1_Timeline1 = $('#WorkScheduler_Panel1_Timeline1');
	var WorkSchedulerPanel1Modal1Choice = false;
	var start_global, end_global, resource_global;

    function run() {

		init();
        event();
    }

    function init() {

    	external_drag_init();

        /* initialize the external events
		-----------------------------------------------------------------*/
        function external_drag_init() {
			$('#WorkSchedulerPanel2Table1TableId').children('tbody').children('tr').each(function() {
				// store data so the calendar knows to render an event upon drop
				$(this).data('event', {
					title: $.trim($(this).children('td').eq(1).text()), // use the element's text as the event title
					stick: true, // maintain when user navigates (see docs on the renderEvent method)
					constraint: 'WorkerAvail',
					color: '#257e4a',
					// parameters
					taskId: $.trim($(this).children('td').eq(1).text())
				});

				// make the event draggable using jQuery UI
				$(this).draggable({
					zIndex: 999,
					revert: true,      // will cause the event to go back to its
					revertDuration: 0  //  original position after the drag
				});
			});
        }

		$("#WorkSchedulerPanel2Table1TableId").on('page-change.bs.table',function (num,size) {
            external_drag_init()
        });


		/* initialize the calendar
		-----------------------------------------------------------------*/
		$WorkScheduler_Panel1_Timeline1.fullCalendar({
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
			now: currentDate,
			selectable: true,
			selectHelper: true,
			// selectOverlap: function(event) {
			// 	return event.rendering === 'background';
			// },
			editable: true,
			droppable: true,
			aspectRatio: 1.8,
			scrollTime: '00:00',
			header: {
				left: 'today prev,next',
				center: 'title',
				right: 'timelineDay,timelineWeek,month'
			},
			defaultView: 'timelineDay',
			views: {
				timelineCustomDay: {
					type: 'timeline',
					duration: { days: 2},
					minTime: '-02:00:00'
				}
			},
			// eventOverlap: false, // will cause the event to take up entire resource height
			resourceAreaWidth: '25%',
			// resourceLabelText: 'Workers',
            refetchResourcesOnNavigate: true,
			resourceColumns: [
				{
					labelText: 'Workers',
					field: 'title',
					width: "80%"
				},
				{
					labelText: 'Hrs',
					field: 'Avail',
					width: "20%",
					render: function(resource, el) {

						if (resource.Avail>0) {
							el.css({
								"color": "black",
							    "background-color" : "LightGreen"
    						});
						}
						else if(resource.Avail===0){
							el.css({
								"color": "black",
							    "background-color" : "Azure"
    						});
						}
						else if(resource.Avail<0){
							el.css({
								"color": "white",
							    "background-color" : "Red"
    						});
						}
					}
				}
			],
			resources: { // you can also specify a plain string like 'json/resources.json'
				url: 'Panel1/TimeLine1/resources/',
				error: function() {
					$('#script-warning').show();
				}
			},
			events: { // you can also specify a plain string like 'json/events.json'
				url: 'Panel1/TimeLine1/events/',
				error: function() {
					$('#script-warning').show();
				}
			},

			// events callback
			eventRender: function(event, element) {
				if(event.rendering !== 'background'){
					element.find(".fc-content").prepend("<span class='closeon'>X</span>");
					element.find(".closeon").on('click', function() {
						$WorkScheduler_Panel1_Timeline1.fullCalendar('removeEvents',event._id);
						console.log('delete');
					});
				}
			},
            drop: function(date, jsEvent, ui, resourceId) {
				console.log('drop', date.format(), resourceId);

                // if so, remove the element from the "Draggable Events" list
                // $(this).remove();
			},
			select: function( start, end, jsEvent, view, resource) {

            	$('#WorkSchedulerPanel1Modal1Create').click();

            	start_global = start;
            	end_global = end;
            	resource_global = resource;

				return false;
			},
			eventReceive: function(event) { // called when a proper external event is dropped
				console.log('eventReceive', event);

				var eventData = {
					resourceId: event.resourceId,
					taskId: event.taskId,
					start: event.start.format()
					// end: event.end.format()
				};

				$.get('Panel1/TimeLine1/event_create/',eventData,function () {

					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchEvents');
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchResources');
					$("#WorkSchedulerPanel2Table1TableId").bootstrapTable('refresh');
					setTimeout(function () {
						external_drag_init()
					},500)
                });
			},
			eventDrop: function(event) { // called when an event (already on the calendar) is moved
				console.log('eventDrop', event);

				var eventData = {
					resourceId: event.resourceId,
					taskId: event.taskId,
					workerscheduledId: event.workerscheduledId,
					start: event.start.format(),
					end: event.end.format()
				};

                $.get('Panel1/TimeLine1/event_update/',eventData,function () {
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchEvents');
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchResources');
					$("#WorkSchedulerPanel2Table1TableId").bootstrapTable('refresh');
					setTimeout(function () {
						external_drag_init()
					},500)
                });
            },
			eventResize: function(event, delta, revertFunc) {

				console.log(event,delta,revertFunc);

				var eventData = {
					resourceId: event.resourceId,
					taskId: event.taskId,
					workerscheduledId: event.workerscheduledId,
					start: event.start.format(),
					end: event.end.format()
				};

				$.get('Panel1/TimeLine1/event_update/',eventData,function () {
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchEvents');
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchResources');
					$("#WorkSchedulerPanel2Table1TableId").bootstrapTable('refresh');
					setTimeout(function () {
						external_drag_init()
					},500)
                });
			},
			loading: function (isLoading, view) {

            	if (isLoading === false){
            		var start = view.currentRange.start.format(),
						end = view.currentRange.end.format();
					KPI_board_update(start,end)
				}
            }
		});
    }

    function event() {

    	// extend worker available events
		$('#WorkSchedulerPanel1Modal1Yes').on('click',function () {
			WorkSchedulerPanel1Modal1Choice = true;
			var eventData;
			if(WorkSchedulerPanel1Modal1Choice){
				eventData = {
					title: 'WorkerAvail',
					resourceId: resource_global.id,
					start: start_global.format(),
					end: end_global.format(),
					rendering: 'background',
					color: 'light green',
					overlap: true
				};
                $.post('Panel1/Modal1/extend_worker_avail/',eventData,function () {

                });
				$WorkScheduler_Panel1_Timeline1.fullCalendar('renderEvent', eventData, true); // stick? = true
				WorkSchedulerPanel1Modal1Choice = false
			}
			$WorkScheduler_Panel1_Timeline1.fullCalendar('unselect');

			$('#WorkSchedulerPanel1Modal1No').click();
		});
    }

	function KPI_board_update(start, end) {
    	var data = {'start':start,
					'end':end};
		$.get('Panel3/KPIBoard/update/', data, function (result) {

			var scheduled = result['scheduled'],
				avail = result['avail'],
				percent = 0,
				$WorkSchedulerPanle3KPIBoard1Stats1 = $("#WorkSchedulerPanle3KPIBoard1Stats1"),
				$WorkSchedulerPanle3KPIBoard1Stats2 = $("#WorkSchedulerPanle3KPIBoard1Stats2");

			if(avail===0){percent=0}
			else if(avail>0){percent=scheduled/avail}

			$WorkSchedulerPanle3KPIBoard1Stats1.text(scheduled +"/"+ avail);
			$WorkSchedulerPanle3KPIBoard1Stats2.text(Math.round(percent*100)+"%");
			if(percent>=0.5){
				$WorkSchedulerPanle3KPIBoard1Stats2.attr('class','red')
			}
			else if(percent<0.5){
				$WorkSchedulerPanle3KPIBoard1Stats2.attr('class','green')
			}
        });
    }

    return run
});