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

    var $FileUpload = $('#FileUpload');

    $(function () {
        init();
        event()
    });

    function init() {
        $FileUpload.fileinput({
            uploadUrl: 'Panel1/Form1/FileUpload/',
            maxFilePreviewSize: 10240,
            browseOnZoneClick: true,
            uploadExtraData: {'csrfmiddlewaretoken': csrf_token}
        });
    }

    function event() {
        $("#FileType").on('change',function () {
            $FileUpload.fileinput('clear')
        });

        $("#WorkConfigDataUpload-form").submit(function (e) {

            var data = $(this).serialize();
            $("#WorkConfigDataUploadSubmit").html("Loading...");
            $.get('Panel1/Form1/Submit/',data,function () {
                $("#WorkConfigDataUploadSubmit").html("Loaded");
            });

            return false
        });
    }
});
