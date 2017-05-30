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
        filter_control = require('filter-control'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort');

    function run() {
        var $table_container_id = $("#"+table2a_container_id),
            $table_id = $("#"+table2a_id);

        init($table_container_id,$table_id);
        event($table_id)
    }

    function init($table_container_id,$table_id_) {
        $table_id_.bootstrapTable();
        $table_container_id.show()
    }

    function event($table_id) {

    }

    return run

});