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
        'bootstrap-datepicker':['/static/bootstrap-datepicker/dist/js/bootstrap-datepicker.min'],
        'gentelella' : ['/static/gentelella/build/js/custom.min'],
        'select2' : ['https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min','/static/select2/dist/js/select2.min']
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
        'bootstrap-datepicker':{
            deps:['jquery','bootstrap']
        },
        'gentelella':{
            deps:['jquery','bootstrap']
        },
        'select2':{
            deps:['jquery','bootstrap']
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

