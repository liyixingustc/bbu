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
        // tableExport = require('tableExport'),
        // bootstrap_table_editable = require('bootstrap-table-editable'),
        // x_editable = require('x-editable'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort'),
        filter_control = require('filter-control');

    var $table_container_id = $("#WorkSchedulerPanel2Table1ContainerId"),
        $table_id = $("#WorkSchedulerPanel2Table1TableId");

    function run(callback) {

        init();
        event();
        if(typeof callback === "function"){
            // $.when(init()).done(function (promise) {
                callback()
            // })
        }
    }

    function init() {

        // $table_container_id.html('<div class="row">' +
        //     '<div class="col-md-2 col-md-offset-5">' +
        //         '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>' +
        //     '</div>' +
        //  '</div>');

        $table_id.bootstrapTable({
            height:700,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            // filterControl:true,
            url:"Panel2/Table1/create/",
            columns:[
                {
                    field: 'line',
                    title: 'Line',
                    sortable: true,
                    searchable: true,
                    editable: true,
                    align: 'center'
                    // filterControl: 'select'
                },
                {
                    field: 'work_order',
                    title: 'WO',
                    sortable: true,
                    editable: true,
                    align: 'center'
                },
                {
                    field: 'description',
                    title: 'description',
                    sortable: true,
                    editable: true,
                    align: 'center'
                },
                {
                    field: 'estimate_hour',
                    title: 'EST',
                    sortable: true,
                    editable: true,
                    align: 'center'
                },
                {
                    field: 'work_type',
                    title: 'type',
                    sortable: true,
                    editable: true,
                    align: 'center'
                },
                {
                    field: 'priority',
                    title: 'priority',
                    sortable: true,
                    editable: true,
                    align: 'center'
                },
                {
                    field: 'OLD',
                    title: 'OLD',
                    sortable: true,
                    editable: true,
                    align: 'center'
                }
            ]
        });
        // $table_container_id.show()
    }

    function event() {


        //editable events
        // $table_id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {
        //
        //     $.post(WorkScheduler_Panel2_Table1_url_edit,{'name':row['name'],'duration':row[field],'date':field},function () {
        //
        //     })
        // });
        // $table_id.on('editable-hidden.bs.table',function (field, row, $el, reason) {
        //
        // });
    }

    return run

});