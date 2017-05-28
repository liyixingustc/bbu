/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2');


    $(function () {

        $("#WorkWorkersConfig-form").submit(function (e) {

            var data = $(this).serialize();
            $("#WorkWorkersConfigSubmit").html("Refreshing...");
            $.post('Panel1/Form1/Submit/',data,function () {
                $("#WorkWorkersConfigSubmit").html("Refresh");
            });

            return false
        });
    });
});
