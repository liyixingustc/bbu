/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        bootstrap_table_export = require('bootstrap-table-export'),
        bootstrap_table = require('bootstrap-table');


    var $table_container_id = $("#WorkWorkersPanel1Table1ContainerId"),
        $table_id = $("#WorkWorkersPanel1Table1");

    function run(){
      init();
    }

    function init(){
        $table_id.bootstrapTable({
            height:700,
            pagination:true,
            // filterControl:true,
            url:"Panel1/Table1/Create/",
            columns:[
                {
                    field: 'name',
                    title: 'name',
                    sortable: true,
                    searchable: true,
                    editable: true,
                    align: 'center'
                },
                {
                    field: 'company',
                    title: 'company',
                    sortable: true,
                    searchable: true,
                    editable: true,
                    align: 'center'
                }
             ]
        });
    }

    return run;

});
