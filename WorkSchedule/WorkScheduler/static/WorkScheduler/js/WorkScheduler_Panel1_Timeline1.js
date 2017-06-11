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
        fullcalendar = require('fullcalendar'),
        scheduler = require('scheduler');


    function run() {

        init();
    }

    function init() {
		$('#WorkScheduler_Panel1_Timeline1').fullCalendar({
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
			now: '2017-05-07',
			editable: true,
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
			eventOverlap: false, // will cause the event to take up entire resource height
			resourceAreaWidth: '15%',
			resourceLabelText: 'Workers',
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
			}
		});
    }

    return run

});