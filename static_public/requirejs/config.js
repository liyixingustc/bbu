/**
 * Created by caliburn on 17-3-11.
 */
require.config({

    baseUrl:'static',
    paths : {
        'jquery' : ['/static/gentelella/vendors/jquery/dist/jquery.min'
                    // ,'https://ajax.googleapis.com/ajax/libs/jquery/2.2.3/jquery.min'
                    ],
        'bootstrap' : [
                        // 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min',
                       '/static/gentelella/vendors/bootstrap/dist/js/bootstrap.min'],
        'bootstrap-table' : ['/static/bootstrap-table/dist/bootstrap-table.min'],
        'bootstrap-fileinput' : ['/static/bootstrap-fileinput/js/fileinput.min'],
        'bootstrap-datepicker':['/static/bootstrap-datepicker/dist/js/bootstrap-datepicker.min'],
        'gentelella' : ['/static/gentelella/build/js/custom'],
        'select2' : [
                    // 'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min',
                     '/static/select2/dist/js/select2.min'],
        'moment' : ['/static/fullcalendar-scheduler/lib/moment.min'],
        'jquery-ui' : ['/static/fullcalendar-scheduler/lib/jquery-ui.min'],
        'fullcalendar' : ['/static/fullcalendar/fullcalendar.min'],
        'scheduler' : ['/static/fullcalendar-scheduler/scheduler.min'],
        'qTip2' : ['/static/qTip2/dist/jquery.qtip.min'],
        'pnotify' : ['/static/gentelella/vendors/pnotify/dist/pnotify'],
        'pnotify-buttons' : ['/static/gentelella/vendors/pnotify/dist/pnotify.buttons'],
        'pnotify-nonblock' : ['/static/gentelella/vendors/pnotify/dist/pnotify.nonblock'],
        'pnotify-animate' : ['/static/gentelella/vendors/pnotify/dist/pnotify.animate'],
        // progressbar
        'nprogress' : ['/static/gentelella/vendors/nprogress/nprogress'],
        'bootstrap-progressbar' : [
            '/static/gentelella/vendors/bootstrap-progressbar/bootstrap-progressbar.min',
            // '/static/bootstrap-progressbar/bootstrap-progressbar.min'
        ],
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
        'qTip2':{
            deps:['jquery','bootstrap']
        },
        'pnotify':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-progressbar':{
            deps:['jquery','bootstrap']
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
        $('.select2_single').select2({
            allowClear: true
        });
        $(".select2_multiple").select2({
          // maximumSelectionLength: 4,
          // placeholder: "With Max Selection limit 4",
          allowClear: true
        });
        $(".datepicker").datepicker({
            todayHighlight: true,
            format: "yyyy-mm-dd"
        });
    });
});

