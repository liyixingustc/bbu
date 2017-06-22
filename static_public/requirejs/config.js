/**
 * Created by caliburn on 17-3-11.
 */
require.config({

    baseUrl:'static',
    paths : {
        'jquery' : ['https://ajax.googleapis.com/ajax/libs/jquery/2.2.3/jquery.min'],
        'bootstrap' : ['https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min',
                       'static/gentelella/vendors/bootstrap/dist/css/bootstrap.min.css'],
        'bootstrap-table' : ['/static/bootstrap-table/dist/bootstrap-table.min'],
        'bootstrap-fileinput' : ['/static/bootstrap-fileinput/js/fileinput.min'],
        'bootstrap-datepicker':['/static/bootstrap-datepicker/dist/js/bootstrap-datepicker.min'],
        'gentelella' : ['/static/gentelella/build/js/custom.min'],
        'select2' : ['https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min','/static/select2/dist/js/select2.min'],
        'moment' : ['/static/fullcalendar-scheduler/lib/moment.min'],
        'jquery-ui' : ['/static/fullcalendar-scheduler/lib/jquery-ui.min'],
        'fullcalendar' : ['/static/full calendar/dist/fullcalendar.min'],
        'scheduler' : ['/static/fullcalendar-scheduler/scheduler.min'],
        // bootstrap table extensions
        'bootstrap-table-export' : ['/static/bootstrap-table/dist/extensions/export/bootstrap-table-export.min'],
        'tableExport' : ['http://rawgit.com/hhurz/tableExport.jquery.plugin/master/tableExport'],
        'bootstrap-table-editable' : ['/static/bootstrap-table/dist/extensions/editable/bootstrap-table-editable.min'],
        'x-editable' : ['http://rawgit.com/vitalets/x-editable/master/dist/bootstrap3-editable/js/bootstrap-editable'],
        'filter-control' : ['/static/bootstrap-table/dist/extensions/filter-control/bootstrap-table-filter-control.min'],
        'flat-json' : ['/static/bootstrap-table/dist/extensions/flat-json/bootstrap-table-flat-json.min'],
        'multiple-sort' : ['/static/bootstrap-table/dist/extensions/multiple-sort/bootstrap-table-multiple-sort.min']

    },
    shim:{

        'jquery':{
            exports:'jquery'
        },
        'bootstrap':{
            deps:['jquery'],
            exports: 'bootstrap'
        },
        'bootstrap-table':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-fileinput':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-datepicker':{
            deps:['jquery','bootstrap']
        },
        'gentelella':{
            deps:['jquery','bootstrap']
        },
        'select2':{
            deps:['jquery','bootstrap']
        },
        'moment':{
            deps:[]
        },
        'jquery-ui':{
            deps:['jquery']
        },
        'fullcalendar':{
            deps:['jquery','moment']
        },
        'scheduler':{
            deps:['jquery','moment','fullcalendar']
        },
        // bootstrap table extensions
        'bootstrap-table-export':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'tableExport':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-table-editable':{
            deps:['jquery','bootstrap','bootstrap-table','x-editable']
        },
        'x-editable':{
            deps:['jquery','bootstrap']
        },
        'filter-control':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'flat-json':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'multiple-sort':{
            deps:['jquery','bootstrap','bootstrap-table']
        }
    }
});

define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2');

    $(function () {
        $('.select2_single').select2();
        $(".datepicker").datepicker({
            todayHighlight: true,
            format: "yyyy-mm-dd"
        });
    });
});

