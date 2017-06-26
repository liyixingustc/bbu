/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        WorkSchedulerPanel2Table1 = require('/static/WorkScheduler/js/WorkScheduler_Panel2_Table1.js'),
        WorkSchedulerPanel1Timeline1 = require('/static/WorkScheduler/js/WorkScheduler_Panel1_Timeline1.js');

    $(function () {
        // var $tables_data =  $("#tables_data");

        // $tables_data.html(
        //  '<div class="row">' +
        //     '<div class="col-md-2 col-md-offset-5">' +
        //         '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>' +
        //     '</div>' +
        //  '</div>');
        // $tables_data.load('Panel2/Table1/create/',function () {
        //
        // });
        WorkSchedulerPanel2Table1(function () {
            setTimeout(function () {
                WorkSchedulerPanel1Timeline1()
            },500)
        });
    });
});
