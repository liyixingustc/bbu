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
        scheduler = require('scheduler'),
		nprogress = require('nprogress'),
        progressbar = require('bootstrap-progressbar'),
    	PNotify = require('pnotify'),
		PNotify_buttons = require('pnotify-buttons'),
		PNotify_nonblock = require('pnotify-nonblock'),
		PNotify_animate = require('pnotify-animate'),
		qTip2 = require('qTip2'),
		screenfull = require('screenfull');

    var fullDate = new Date();
    //convert month to 2 digits
    var twoDigitMonth = ((fullDate.getMonth().length+1) === 1)? (fullDate.getMonth()+1) : '0' + (fullDate.getMonth()+1);
    var currentDate = fullDate.getFullYear() + "-" + twoDigitMonth + "-" + fullDate.getDate();
	var $WorkScheduler_Panel1_Timeline1 = $('#WorkScheduler_Panel1_Timeline1');
	var WorkSchedulerPanel1Modal1Choice = false,
		WorkSchedulerPanel1Modal2Choice = false;
	var select_data_global = 1, event_data_global = 1;

    function run() {

		init();
        event();

		var $fc_icon_fullscreen = $(".fc-icon-fullscreen");
		$fc_icon_fullscreen.parent().html(
			'<span class="glyphicon glyphicon-fullscreen" aria-hidden="true"></span>'
		);
		$fc_icon_fullscreen.qtip({
			content: "full screen"
		});

    }

    function init() {

    	external_drag_init();

        /* initialize the external events
		-----------------------------------------------------------------*/
        function external_drag_init() {
			$('#WorkSchedulerPanel2Table1TableId').children('tbody').children('tr').each(function() {
				// store data so the calendar knows to render an event upon drop
				$(this).data('event', {
					'title': $.trim($(this).children('td').eq(1).text()), // use the element's text as the event title
					// stick: true, // maintain when user navigates (see docs on the renderEvent method)
					'constraint': 'WorkerAvail',
					'duration':'05:00',
					// color: '#257e4a',
					// parameters
					'taskId': $.trim($(this).children('td').eq(1).text())
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
			firstDay:6,
			editable: true,
			droppable: true,
			aspectRatio: 1.8,
			scrollTime: '00:00',
			customButtons: {
				fullscreen: {
					text: 'full screen',
					icon: 'fullscreen glyphicon glyphicon-fullscreen',
					click: function(event) {
						if (screenfull.enabled) {
							screenfull.toggle($WorkScheduler_Panel1_Timeline1[0]);
						}
					}
				}
			},
			header: {
				left: 'today prev,next   fullscreen',
				center: 'title',
				right: 'timelineCustomDay,timelineCustomWeek,month'
			},
			defaultView: 'timelineCustomDay',
			views: {
				timelineCustomDay: {
					type: 'timeline',
					duration: { days: 1},
					minTime: '-01:00:00',
					maxTime: '25:00:00',
					slotDuration:'00:30:00',
					slotLabelFormat: [
					'ddd M/D',
					'ha'
					],
					columnFormat: 'ddd D.M'
				},
				timelineCustomWeek: {
					type: 'timeline',
					duration: { weeks: 1},
					minTime: '-01:00:00',
					maxTime: '25:00:00',
					slotDuration:'00:30:00'
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
				// if(event.rendering !== 'background'){
				// 	element.find(".fc-content").prepend("<span class='closeon'>X</span>");
				// 	element.find(".closeon").on('click', function() {
				// 		$WorkScheduler_Panel1_Timeline1.fullCalendar('removeEvents',event._id);
				// 		console.log('delete');
				// 	});
				// }

				if(event.rendering !== 'background'){
					var color = 'grey';
					switch (event.priority){
						case 'S':color = 'yellow';break;
						case 'U':color = 'red';break;
						case '1':color = 'green';break;
						case '2':color = 'blue';break;
						case '3':color = 'tan';break;
						case undefined:color = 'grey';break;
					}
					// <span class="fc-title" style="position: relative; top: 0px; left: 0px;">17004298</span>

					var html_content =
					    '<div class="progress" style="height: 36px">\
						  <div class="progress-bar progress-bar-striped active progress-bar-'+color+'" role="progressbar"\
						  aria-valuenow="'+event.percent*100+'" aria-valuemin="0" aria-valuemax="100" style="width:100%">\
							<span>\
								'+event.taskId+'</br>' +
						        'complete: '+Math.round(event.percent*100)+'%\
						    </span>\
						  </div>\
						 </div>';

					element.find('.fc-content').html(html_content);
					element.css({'margin':'0','padding':'0','border':'0','background-color':'transparent'});
					element.find('.progress').css({'margin':'0','padding':'0','border':'0'});
					element.find('.progress .progress-bar').css({'margin':'0','padding':'0','border':'0','position':'static'});
					// console.log(element)
				}
			},
			eventAfterRender:function( event, element, view ) {
            	// console.log(element)
				if(event.rendering !== 'background'){
					// element.find('.progress .progress-bar').progressbar({display_text: 'center', use_percentage: false});
					var qtip_html =
						'Complete: ' + Math.round(event.percent*100)+ '%<br/>\
						Task description:' + event.description
						;
					element.qtip({
						content: qtip_html
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

            	select_data_global = {
            		'start': start.format(),
					'end': end.format(),
					'resourceId': resource.id
				};

				return false;
			},
			eventReceive: function(event) { // called when a proper external event is dropped
				console.log('eventReceive', event);

				var eventData = {
					'resourceId': event.resourceId,
					'taskId': event.taskId,
					'start': event.start.format()
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
			eventClick:function(event, jsEvent, view){
            	$('#WorkSchedulerPanel1Modal2Create').click();
				event_data_global = {
					resourceId: event.resourceId,
					taskId: event.taskId,
					workerscheduledId: event.workerscheduledId,
					deduction: event.deduction,
					start: event.start.format(),
					end: event.end.format()
				};

				$("#Deduction").val(event.deduction);

				return false;
			},
            eventMouseover:function (event, jsEvent, view) {
				// var tooltip = '<div class="tooltipevent" style="width:100px;height:100px;background:#ccc;position:absolute;z-index:10001;">' + event.description + '</div>';
				// console.log(event)
				// $("body").append(tooltip);
				// $(this).mouseover(function(e) {
				// 	$(this).css('z-index', 10000);
				// 	$('.tooltipevent').fadeIn('500');
				// 	$('.tooltipevent').fadeTo('10', 1.9);
				// }).mousemove(function(e) {
				// 	$('.tooltipevent').css('top', e.pageY + 10);
				// 	$('.tooltipevent').css('left', e.pageX + 20);
				// });
            },
			eventMouseout: function(calEvent, jsEvent) {
				 // $(this).css('z-index', 8);
				 // $('.tooltipevent').remove();
			},
			loading: function (isLoading, view) {

            	if (isLoading === false){
            		var start = view.start.format(),
						end = view.end.format();

					KPI_board_update(start,end)
				}
            }
		});
    }

    function event() {

    	// extend worker available events
		$('#WorkSchedulerPanel1Modal1FormId').submit(function (e) {
			WorkSchedulerPanel1Modal1Choice = true;
			var form_data = $(this).serializeObject();
			if(WorkSchedulerPanel1Modal1Choice){
				var eventData = $.extend({}, form_data, select_data_global);

                $.get('Panel1/Modal1/select_submit/',eventData,function () {
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchEvents');
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchResources');

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
                });

				WorkSchedulerPanel1Modal1Choice = false
			}
			$WorkScheduler_Panel1_Timeline1.fullCalendar('unselect');

			$('#WorkSchedulerPanel1Modal1No').click();
			return false
		});

		$('#WorkSchedulerPanel1Modal2FormId').submit(function (e) {
			WorkSchedulerPanel1Modal2Choice = true;
			var form_data = $(this).serializeObject();
			if(WorkSchedulerPanel1Modal2Choice){
				var eventData = $.extend({}, form_data, event_data_global);

                $.get('Panel1/Modal2/tasks_submit/',eventData,function () {
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchEvents');
					$WorkScheduler_Panel1_Timeline1.fullCalendar('refetchResources');

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
                });

				WorkSchedulerPanel1Modal2Choice = false
			}
			$WorkScheduler_Panel1_Timeline1.fullCalendar('unselect');

			$('#WorkSchedulerPanel1Modal2No').click();
			return false
		});

		// full screen the timeline table
		$("#WorkSchedulerPanel1TimeLine1Button1").click(function () {
			if (screenfull.enabled) {
				screenfull.toggle($WorkScheduler_Panel1_Timeline1[0]);
			}
        });
    }

	function KPI_board_update(start, end) {
    	var data = {'start':start,
					'end':end};
		$.get('Panel3/KPIBoard/update/', data, function (result) {

			var scheduled = result['scheduled'],
				avail = result['avail'],
				avail_remain = result['avail_remain'],
				task_remain = result['task_remain'],
				tasks_count = result['tasks_count'],
				percent1 = 0,
				percent2 = 0,
				$WorkSchedulerPanle3KPIBoard1Stats1 = $("#WorkSchedulerPanle3KPIBoard1Stats1"),
				$WorkSchedulerPanle3KPIBoard1Stats2 = $("#WorkSchedulerPanle3KPIBoard1Stats2"),
				$WorkSchedulerPanle3KPIBoard2Stats1 = $("#WorkSchedulerPanle3KPIBoard2Stats1"),
				$WorkSchedulerPanle3KPIBoard2Stats2 = $("#WorkSchedulerPanle3KPIBoard2Stats2"),
				$WorkSchedulerPanle3KPIBoard3Stats1 = $("#WorkSchedulerPanle3KPIBoard3Stats1");


			// KPIboard 1 setting
			if(avail===0){percent1=0}
			else if(avail>0){percent1=scheduled/avail}

			$WorkSchedulerPanle3KPIBoard1Stats1.text(Math.round(scheduled)+"/"+ Math.round(avail)+" hrs");
			$WorkSchedulerPanle3KPIBoard1Stats2.text(Math.round(percent1*100)+"%");
			if(percent1<1){
				$WorkSchedulerPanle3KPIBoard1Stats2.attr('class','green')
			}
			else if(percent1>=1){
				$WorkSchedulerPanle3KPIBoard1Stats2.attr('class','red')
			}

			// KPIboard 2 setting
			if(task_remain===0){percent2=0}
			else if(task_remain>0){percent2=avail_remain/task_remain}

			$WorkSchedulerPanle3KPIBoard2Stats1.text(Math.round(avail_remain) +"/"+ Math.round(task_remain)+" hrs");
			$WorkSchedulerPanle3KPIBoard2Stats2.text(Math.round(percent2*100)+"%");
			if(percent2>=1){
				$WorkSchedulerPanle3KPIBoard2Stats2.attr('class','green')
			}
			else if(percent2<1){
				$WorkSchedulerPanle3KPIBoard2Stats2.attr('class','red')
			}

			$WorkSchedulerPanle3KPIBoard3Stats1.text(tasks_count)

        });
    }

    // $(function () {
    // 	$('.progress .progress-bar').progressbar();
    // });

    return run
});