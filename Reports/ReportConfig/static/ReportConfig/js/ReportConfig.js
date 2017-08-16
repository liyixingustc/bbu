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

    var $FileType = $('#FileType'),
        $FileUpload = $('#FileUpload'),
        $Processor = $('#Processor'),

        FileType = $FileType.val() ,
        Processor = $Processor.val();


    $(function () {
        init();
        event()
    });

    function init() {

        switch (FileType){
            case 'ReportTimeDetail': Processor = 'ReportTimeDetailProcessor';break;

        }

        $FileUpload.fileinput({
            uploadUrl: 'Panel1/Form1/FileUpload/',
            maxFilePreviewSize: 10240,
            minFileCount: 1,
            // maxFileCount: 1,
            uploadAsync: false,
            browseOnZoneClick: true,
            uploadExtraData: function (previewId, index){
                return {
                    'csrfmiddlewaretoken': csrf_token,
                    'FileType':FileType,
                    'Processor':Processor
                };
            }
        });
    }

    function event() {
        $FileType.change(function () {
            $FileUpload.fileinput('clear');
            FileType = $(this).val();

            switch (FileType){
                case 'ReportTimeDetail': Processor = 'ReportTimeDetailProcessor';break;

            }
        });

        $Processor.change(function () {
            Processor = $(this).val();
        });

        $("#ReportConfigDataUpload-form").submit(function (e) {

            var data = $(this).serialize();
            $("#ReportConfigDataUploadSubmit").html("Loading...");
            $.get('Panel1/Form1/Submit/',data,function () {
                $("#ReportConfigDataUploadSubmit").html("Loaded");
            });

            return false
        });
    }
});
