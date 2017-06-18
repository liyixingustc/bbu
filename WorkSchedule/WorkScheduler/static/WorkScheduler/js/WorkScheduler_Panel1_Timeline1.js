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

        /* initialize the external events
		-----------------------------------------------------------------*/
		$('tbody tr' ).each(function() {
			// store data so the calendar knows to render an event upon drop

			$(this).data('event', {
				title: $.trim($(this).children('td').eq(1).text()), // use the element's text as the event title
				stick: true // maintain when user navigates (see docs on the renderEvent method)
			});

            // make the event draggable using jQuery UI
			$(this).draggable({
				zIndex: 999,
				revert: true,      // will cause the event to go back to its
				revertDuration: 0  //  original position after the drag
			});
		});

		/* initialize the calendar
		-----------------------------------------------------------------*/
		$WorkScheduler_Panel1_Timeline1.fullCalendar({
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
			now: currentDate,
			selectable: true,
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
				right: 'timelineDay,timelineThreeDays,agendaWeek,month'
			},
			defaultView: 'timelineDay',
			views: {
				timelineThreeDays: {
					type: 'timeline',
					duration: { days: 3 }
				}
			},
			// eventOverlap: false, // will cause the event to take up entire resource height
			resourceAreaWidth: '25%',
			resourceLabelText: 'Workers',
            refetchResourcesOnNavigate: true,
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
            drop: function(date, jsEvent, ui, resourceId) {
				console.log('drop', date.format(), resourceId);

                // if so, remove the element from the "Draggable Events" list
                $(this).remove();
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
			},
			eventDrop: function(event) { // called when an event (already on the calendar) is moved
				console.log('eventDrop', event);
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
					start: start_global,
					end: end_global,
					rendering: 'background',
					color: 'light green',
					overlap: true
				};
				$.post('Panel1/Modal1/',eventData,function () {

                });
				$WorkScheduler_Panel1_Timeline1.fullCalendar('renderEvent', eventData, true); // stick? = true
				WorkSchedulerPanel1Modal1Choice = false
			}
			$WorkScheduler_Panel1_Timeline1.fullCalendar('unselect');

			$('#WorkSchedulerPanel1Modal1No').click();
		});
    }

    return run

});