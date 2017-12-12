/**
 * Created by caliburn on 17-5-28.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        bootstraptable =  require('bootstrap-table'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        moment = require('moment'),
        jqueryUI = require('jquery-ui'),
        fullcalendar = require('fullcalendar'),
        scheduler = require('scheduler'),
        PNotify = require('pnotify'),
		PNotify_buttons = require('pnotify-buttons'),
		PNotify_nonblock = require('pnotify-nonblock'),
		PNotify_animate = require('pnotify-animate'),
        // bootstrap table extensions
        bootstrap_table_export = require('bootstrap-table-export'),
        // tableExport = require('tableExport'),
        bootstrap_table_editable = require('bootstrap-table-editable'),
        x_editable = require('x-editable'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort'),
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');

    var $table_container_id = $("#WorkSchedulerPanel2Table1ContainerId"),
        $table_id = $("#WorkSchedulerPanel2Table1TableId");

    function run(callback) {

        init();
        event();
        if(typeof callback === "function"){
            // $.when(init()).done(function (promise) {
                callback()
            // })
        }
    }

    function init() {

        // $table_container_id.html('<div class="row">' +
        //     '<div class="col-md-2 col-md-offset-5">' +
        //         '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>' +
        //     '</div>' +
        //  '</div>');

        $table_id.bootstrapTable({
            height:700,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            // filterControl:true,
            filter:true,
            url:"Panel2/Table1/create/",
            columns:[
                // {
                //     field: 'line',
                //     title: 'Line',
                //     sortable: true,
                //     searchable: true,
                //     // editable: true,
                //     align: 'center'
                //     // filterControl: 'select'
                // },
                {
                    field: 'work_order',
                    title: 'WO',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'description',
                    title: 'description',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'balance_hour',
                    title: 'BAL',
                    sortable: false,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'estimate_hour',
                    title: 'EST',
                    sortable: true,
                    editable: true,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'AOR',
                    title: 'AOR',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'work_type',
                    title: 'type',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'select',
                        data:[
                              'CM', 'PM', 'EM', 'EV'
                        ]
                    }
                },
                {
                    field: 'priority',
                    title: 'priority',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'select',
                        data:[
                              'S','U','1','2','3','4'
                        ]
                    }
                },
                {
                    field: 'OLD',
                    title: 'OLD',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'current_status',
                    title: 'status',
                    sortable: true,
                    // editable: true,
                    align: 'center',
                    filter:{
                        type:'select',
                        data:[
                              'Work Request',
                              'Approved',
                              'Wait For Parts',
                              'Scheduled',
                              'Complete',
                              'Canceled',
                              'Denied'
                        ]
                    }
                },
            ],
            rowStyle: function (row, index) {
                var color = null,
                    bal = row['balance_hour'],
                    est = row['estimate_hour'],
                    status = row['current_status'];

                if(bal===0 && status === 'Scheduled'){
                    color = 'green'
                }
                else if (bal<est && bal>0 ){
                    color = '#eec700'
                }
                else if(bal<0){
                    color = 'red'
                }

                if(color){
                    return {
                        classes: '',
                        css: {'background-color': color, 'color':'white'}
                    }
                }
                else {
                    return {
                        classes: '',
                        css: {}
                    }
                }
            },
            rowAttributes:function (row, index) {

            },
        });
        // $table_container_id.show()
    }

    function event() {

        //external_drag_init
        $table_id.on('all.bs.table', function (data) {
            external_drag_init()
        });

        //editable events
        $table_id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            $.get('Panel2/Table1/edit/',row,function () {
                $table_id.bootstrapTable('refresh');
                var notice = new PNotify({
                                    title: 'Success!',
                                    text: 'You have successfully extended the worker available hours',
                                    type: 'success',
                                    sound: false,
                                    animate_speed: 'fast',
                                    styling: 'bootstrap3',
                                    nonblock: {
                                        nonblock: true
                                    }
                                });
                notice.get().click(function() {
                    notice.remove();
                });
            })
        });
        $table_id.on('editable-hidden.bs.table',function (field, row, $el, reason) {
        });

    }

    function external_drag_init() {
		$('#WorkSchedulerPanel2Table1TableId').children('tbody').children('tr').each(function() {
			// store data so the calendar knows to render an event upon drop
			var duration = $.trim($(this).children('td').eq(3).text()),
				duration_hours = duration.split('.')[0],
				duration_mins = duration.split('.')[1]*6;
				if(duration_hours<0){duration_hours=0}
				if(!duration_mins || duration_mins<0){duration_mins=0}

			$(this).data('event', {
				'title': $.trim($(this).children('td').eq(0).text()), // use the element's text as the event title
				// stick: true, // maintain when user navigates (see docs on the renderEvent method)
				'constraint': 'WorkerAvail',
				'duration': moment({hour: duration_hours,minute:duration_mins}).format("HH:mm"),
				// color: '#257e4a',
				// parameters
				'taskId': $.trim($(this).children('td').eq(0).text())
			});

			// make the event draggable using jQuery UI
			$(this).draggable({
				zIndex: 999,
				revert: true,      // will cause the event to go back to its
				revertDuration: 0  //  original position after the drag
			});
		});
	}

    return run

});