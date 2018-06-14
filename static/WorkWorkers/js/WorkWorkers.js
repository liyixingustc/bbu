/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        bootstrap_table = require('bootstrap-table');


    $(function () {

        $("#WorkWorkersConfig-form").submit(function (e) {

            var data = $(this).serialize(),
                $tables_data =  $("#tables_id");

            $("#WorkWorkersConfigSubmit").html("Refreshing...");
            $.post('Panel1/Form1/Submit/',data,function () {
                $tables_data.html('<div class="row">' +
                    '<div class="col-md-2 col-md-offset-5">' +
                        '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>' +
                    '</div>' +
                 '</div>');

                 $table_id.bootstrapTable({
                     height:700,
                     striped:true,
                     minimumCountColumns:2,
                     showFooter:false,
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
                             // filterControl: 'select'
                         },
                         {
                             field: 'company',
                             title: 'company',
                             sortable: true,
                             editable: true,
                             align: 'center'
                         }
                      ]
                });

                $("#WorkWorkersConfigSubmit").html("Refresh");
            });

            return false
        });
    });
});
