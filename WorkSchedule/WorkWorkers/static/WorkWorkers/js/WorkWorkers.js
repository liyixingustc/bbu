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
        bootstrap_table = require('bootstrap-table'),
        bootstrap_table_editable = require('bootstrap-table-editable');

    var $table_container_id = $("#WorkWorkersPanel1Table1ContainerId"),
        $table = $("#WorkWorkersPanel1Table1"),
        $remove = $('#remove'),
        //$create = $('#create'),
        selections = [];

    function run(){
      init();
    }

    function init(){
        $table.bootstrapTable({
            search: true,
            height:getHeight(),
            columns:[

                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    field: 'id',
                    title: 'id',
                    sortable: true,
                    searchable: true,
                    editable: true,
                    align: 'center'
                },
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

        $table.on('check.bs.table uncheck.bs.table ' +
                'check-all.bs.table uncheck-all.bs.table', function () {
            $remove.prop('disabled', !$table.bootstrapTable('getSelections').length);
            // save your data, here just save the current page
            selections = getIdSelections();
            // push or splice the selections if you want to save all data selections
        });
        $table.on('expand-row.bs.table', function (e, index, row, $detail) {
                $detail.html('Loading from ajax request...');

                $.get('Panel1/Table1/Create/', function (res) {
                    //$detail.html(res.replace(/\n/g, '<br>'));
                    console.log(res)
                    $detail.html(res.total)
                });


        });
        $table.on('all.bs.table', function (e, name, args) {
        });

        $table.on("click-row.bs.table", function(e, row, $tr) {
          console.log("Clicked on: " + $(e.target).attr('class'), [e, row, $tr]);
          if ($tr.next().is('tr.detail-view')) {
            $table.bootstrapTable('collapseRow', $tr.data('index'));
          } else {
            $table.bootstrapTable('expandRow', $tr.data('index'));
          }
        });

        $remove.click(function () {

          var ids = $.map($table.bootstrapTable('getSelections'), function (row) {
              console.log(row.id)
              return row.id;
          });

          var url = 'Panel1/Table1/Delete/';
          var data = ids.join(',');
          console.log(data)

          idsjs = {}
          idsjs["ids"] = data;

          $.ajax({
              url: url,
              type: 'POST',
              data: idsjs,
              cache: false,
              error: function (e) {
                  alert(e);
              },
              success: function () {
                  $table.bootstrapTable('remove', {
                      field: 'id',
                      values: ids
                  });
              }
          });
          $(window).resize(function () {
              $table.bootstrapTable('resetView', {
                  height: getHeight()
              });
          });
        });

        $(document).ready(function(){
            $("#create").click(function(){
                $("#create_user").modal({backdrop:'static'});
            });
        });

/*
          $("#Addworker-form").submit(function (e) {

              var data = $("#Addworker-form").serialize(),
                  $tables_data =  $("#tables_data");

              $("#Addworker").html("Refreshing...");
              $.post('Panel1/Form1/Submit/',data,function (data) {})
                .done(function() { window.alert("Successfully submitted!"); })
                .fail(function() { window.alert("Submission failed!"); });
                  //$table.bootstrapTable('refresh');

              return false
        });
        */

        $("#Addworker").click( function() {
            $.post( 'Panel1/Form1/Submit/', $("#Addworker-form").serialize(), function(data) {
               },
               'json' // I expect a JSON response
            )
            .done(function() { window.alert("Successfully submitted!"); })
            .fail(function() { window.alert("Submission failed!"); });
        });

        $(document).ready(function(){
               $.get('Panel1/Form1/Get_Company/',function(result){

                    console.log("Getting company!")
                    console.log(result);
                    $("#company option").remove();
                    for (var i = 0; i < result.length; i++) {
                        $("#company").append('<option>'+ result[i].business_name +'</option>');
                    };

                 })
        });


/*
        $("#Addworker").submit(function() {
            $.post("Panel1/Form1/Submit/", $("#Addworker").serialize())
                .done(function() { window.alert("Successfully submitted!"); })
                .fail(function() { window.alert("Submission failed!"); });
            $table.bootstrapTable('refresh')
        });
        */

    }

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row.id
        });
    }

    function detailFormatter(index, row) {
        var html = [];
        $.each(row, function (key, value) {
            html.push('<p><b>' + key + ':</b> ' + value + '</p>');
        });
        return html.join('');
    }

    function getHeight() {
        return $(window).height();
    }

    return run;

});
