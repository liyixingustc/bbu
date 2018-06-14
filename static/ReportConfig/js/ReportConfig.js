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
        $SubmitButton = $('#ReportConfigDataUploadSubmit'),

        FileType = $FileType.val() ,
        Processor = $Processor.val(),
        interval = null;


    $(function () {
        init();
        event()
    });

    function init() {

        switch (FileType){
            case 'ReportLostTimeDetail': Processor = 'ReportLostTimeDetailProcessor';break;
            case 'ReportTimeDetail': Processor = 'ReportTimeDetailProcessor';break;

        }

        process_result(FileType);

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

            process_result(FileType);

            switch (FileType){
                case 'ReportLostTimeDetail': Processor = 'ReportLostTimeDetailProcessor';break;
                case 'ReportTimeDetail': Processor = 'ReportTimeDetailProcessor';break;

            }
        });

        $Processor.change(function () {
            Processor = $(this).val();
        });

        $("#ReportConfigDataUpload-form").submit(function (e) {

            var data = $(this).serialize();
            $("#ReportConfigDataUploadSubmit").html("Loading...");
            $.get('Panel1/Form1/Submit/',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    process_result(FileType);
                    // $("#ReportConfigDataUploadSubmit").html("Loaded");
                }else {
                    $("#ReportConfigDataUploadSubmit").html("Try Again");
                    alert(msg)
                }
            });

            return false
        });
    }

    function process_result(file_type) {

        if (interval !== null){
            clearInterval(interval);
        }

        interval = setInterval(function () {
            $.get('Panel1/Form1/Process/', {'FileType': file_type}, function (result) {
                result = result['result'];
                if (result === null){
                    clearInterval(interval);
                    $SubmitButton.prop('disabled', false);
                    $SubmitButton.html("Submit");
                }
                else if (result===1){
                    clearInterval(interval);
                    $SubmitButton.prop('disabled', false);
                    $SubmitButton.html("Loaded");
                }
                else if (result >=0 && result<1){
                    $SubmitButton.prop('disabled', true);
                    $SubmitButton.html(Math.round(result*100)+"%");
                }
            })
        }, 1000)
    }
});
