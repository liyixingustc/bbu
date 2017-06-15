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
        // bootstrap table extensions
        bootstrap_table_export = require('bootstrap-table-export'),
        tableExport = require('tableExport'),
        bootstrap_table_editable = require('bootstrap-table-editable'),
        x_editable = require('x-editable'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort');

    function run() {
        var $table_container_id = $("#"+WorkScheduler_Panel2_Table1_container_id),
            $table_id = $("#"+WorkScheduler_Panel2_Table1_id);
        init($table_container_id,$table_id);
        event($table_id);
    }

    function init($table_container_id,$table_id_) {

        // $table_container_id.html('<div class="row">' +
        //     '<div class="col-md-2 col-md-offset-5">' +
        //         '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>' +
        //     '</div>' +
        //  '</div>');
        // $table_container_id.load('Panel2/Table1/create/',function () {
        //
        // });
        $table_id_.bootstrapTable();
        $table_container_id.show()
    }

    function event($table_id) {

        //editable events
        $table_id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            $.post(WorkScheduler_Panel2_Table1_url_edit,{'name':row['name'],'duration':row[field],'date':field},function () {

            })
        });
        $table_id.on('editable-hidden.bs.table',function (field, row, $el, reason) {

        });
    }

    return run

});