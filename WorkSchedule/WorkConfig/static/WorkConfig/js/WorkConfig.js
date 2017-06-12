/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        fileinput = require('bootstrap-fileinput'),
        gentelella = require('gentelella'),
        select2 = require('select2');


    $(function () {
        $("#FileUpload").fileinput({
            uploadUrl: 'Panel1/Form1/FileUpload/',
            maxFilePreviewSize: 10240,
            browseOnZoneClick: true,
            uploadExtraData: {'csrfmiddlewaretoken': csrf_token}
        });

        $("#WorkConfigDataUpload-form").submit(function (e) {

            var data = $(this).serialize();
            $("#WorkConfigDataUploadSubmit").html("Refreshing...");
            $.get('Panel1/Form1/Submit/',data,function () {
                $("#WorkConfigDataUploadSubmit").html("Refresh");
            });

            return false
        });
    });
});
