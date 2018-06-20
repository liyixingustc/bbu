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
        selections = [];

    function run(){
      init();
    }

    function init(){
        $table.bootstrapTable({
            height:getHeight(),
            pagination:true,
            // filterControl:true,
            url:"Panel1/Table1/Create/",
            columns:[

                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
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
            if (index % 2 == 1) {
                $detail.html('Loading from ajax request...');
                $.get('LICENSE', function (res) {
                    $detail.html(res.replace(/\n/g, '<br>'));
                });
            }
        });
        $table.on('all.bs.table', function (e, name, args) {
            console.log(name, args);
        });

        $table.on("click-row.bs.table", function(e, row, $tr) {
          console.log("Clicked on: " + $(e.target).attr('class'), [e, row, $tr]);
          if ($tr.next().is('tr.detail-view')) {
            $table.bootstrapTable('collapseRow', $tr.data('index'));
          } else {
            $table.bootstrapTable('expandRow', $tr.data('index'));
          }
        });

        /*
        $remove.click(function () {
            var names = $.map($table.bootstrapTable('getSelections'), function (row) {
                console.log(row.name)
                return row.name;
            });
            $table.bootstrapTable('remove', {
                field: 'name',
                values: names
            });
            $remove.prop('disabled', true);

        });
        $(window).resize(function () {
            $table.bootstrapTable('resetView', {
                height: getHeight()
            });
        });
        */


        $remove.click(function () {

          var selects = $('#users-table').bootstrapTable('getSelections');
              ids = $.map(selects, function (row) {
                  return row.id;
              });

          var url = 'url:"Panel1/Table1/Delete/"';
          var data = 'userID=' + ids.join(',');

          $.ajax({
              url: url,
              data: data,
              cache: false,
              error: function (e) {
                  alert(e);
              },
              success: function () {
                  $('#users-table').bootstrapTable('remove', {
                      field: 'id',
                      values: ids
                  });
              }
          });
        });

    }

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row.name
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
