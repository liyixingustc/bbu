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
            case 'Tasks': Processor = 'TasksLoadProcessor';break;
            case 'WorkerAvail':Processor = 'WorkerAvailProcessor';break;

        }

        $FileUpload.fileinput({
            uploadUrl: 'Panel1/Form1/FileUpload/',
            maxFilePreviewSize: 10240,
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
            case 'Tasks': Processor = 'TasksLoadProcessor';break;
            case 'WorkerAvail':Processor = 'WorkerAvailProcessor';break;

        }

        });

        $Processor.change(function () {
            Processor = $(this).val();
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
