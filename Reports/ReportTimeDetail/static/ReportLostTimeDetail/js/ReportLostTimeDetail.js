/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        fileinput = require('bootstrap-fileinput'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        moment = require('moment'),
        Highcharts = require('Highcharts'),
        HighchartsMore = require('Highcharts-more'),
        HighchartsExporting = require('Highcharts-exporting'),
        screenfull = require('screenfull');

    var product_name_global, cause_name_global;
    var is_fullscreen = false;
    var div_chart_height_originial, div_chart_width_originial;

    var $ReportLostTimeDetailPanel2ChartContainer = $('#ReportLostTimeDetailPanel2ChartContainer');


    $(function () {
        init();
        event()
    });

    function init() {
        $("#StartDate").datepicker("update", moment().subtract(1, 'days').format('YYYY-MM-DD'));
        $("#EndDate").datepicker("update", moment().add(30, 'days').format('YYYY-MM-DD'));
    }

    function event() {

        screenfull.onchange(function () {
			is_fullscreen = !is_fullscreen;

			if(is_fullscreen){
				var screen_height = screen.availHeight,
                    screen_width = screen.availWidth;

				div_chart_height_originial = $ReportLostTimeDetailPanel2ChartContainer.height();
				div_chart_width_originial = $ReportLostTimeDetailPanel2ChartContainer.width();

				$ReportLostTimeDetailPanel2ChartContainer.height(screen_height);
                $ReportLostTimeDetailPanel2ChartContainer.width(screen_width);

			}
			else{
                $ReportLostTimeDetailPanel2ChartContainer.height(div_chart_height_originial);
                $ReportLostTimeDetailPanel2ChartContainer.width(div_chart_width_originial);

			}
        });

        $("#ReportLostTimeDetailPanel1Form1FormId").submit(function (e) {

            var data = $(this).serialize();
            $("#ReportLostTimeDetailPanel1Form1Submit").html("Running...");
            $.get('Panel1/Form1/Submit/',data,function (bar_data) {
                var GroupBy = $('#GroupBy').val(),
                    target_id = 'ReportLostTimeDetailPanel2Chart1';

                switch (GroupBy){
                    case 'Product':target_id = 'ReportLostTimeDetailPanel2Chart1';break;
                    case 'Cause':target_id = 'ReportLostTimeDetailPanel2Chart2';break;
                    case 'Comments':target_id = 'ReportLostTimeDetailPanel2Chart3';break;
                }

                $('#ReportLostTimeDetailPanel2Chart1').html('');
                $('#ReportLostTimeDetailPanel2Chart2').html('');
                $('#ReportLostTimeDetailPanel2Chart3').html('');

                create_waterfall(target_id, bar_data);
                $("#ReportLostTimeDetailPanel1Form1Submit").html("Finished");
            });

            return false
        });
    }

    function create_waterfall(id,data) {
        Highcharts.chart(id, {
            chart: {
                type: 'waterfall'
            },

            title: {
                text: 'Waterfall Reports'
            },

            xAxis: {
                type: 'category'
            },

            yAxis: {
                title: {
                    text: 'Min'
                },
                floor: 0,
            },

            legend: {
                enabled: false
            },

            tooltip: {
                pointFormatter: function () {
                    return '<b>Mins: '+ Math.abs(this.y).toFixed(1) +'</b><br/>' +
                           '<b>Hrs: '+ Math.abs(this.y/60).toFixed(1) +'</b><br/>'+
                           '<b>Occ: '+ this.count +'</b>'
                }
            },
            series: [{
                data: data,
                dataLabels: {
                    enabled: true,
                    formatter: function () {
                        return Math.abs(this.y).toFixed(1) + ' (' + this.point.count + ')'+
                               '<br/>'+ Math.abs(this.y/60).toFixed(1) +'Hrs<br/>';
                    },
                    style: {
                        fontWeight: 'bold'
                    }
                },
                pointPadding: 0
            }],
            plotOptions: {
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function (event) {
                                var id = this.series.chart.renderTo.id,
                                    target_id = this.series.chart.renderTo.id;

                                switch (id){
                                    case 'ReportLostTimeDetailPanel2Chart1':target_id = 'ReportLostTimeDetailPanel2Chart2';product_name_global=this.name;break;
                                    case 'ReportLostTimeDetailPanel2Chart2':target_id = 'ReportLostTimeDetailPanel2Chart3';cause_name_global=this.name;break;
                                    case 'ReportLostTimeDetailPanel2Chart3':target_id = 'ReportLostTimeDetailPanel2Chart3';break;
                                }

                                var data = {
                                        'StartDate':$("#StartDate").val(),
                                        'EndDate':$("#EndDate").val(),
                                        'StartShift':$("#StartShift").val(),
                                        'EndShift':$("#EndShift").val(),
                                        'Line':$("#Line").val(),
                                        'GroupBy':$("#GroupBy").val(),
                                        'product_name': product_name_global,
                                        'cause_name': cause_name_global,
                                        'div_id': id
                                    };

                                if (id !== 'ReportLostTimeDetailPanel2Chart3' &&
                                    product_name_global!== 'Total' &&
                                    cause_name_global!== 'Total'){
                                    $.get('Panel1/Form1/Submit/',data,function (data) {
                                        create_waterfall(target_id, data);
                                    });
                                }

                                if(!is_fullscreen){
                                    div_chart_height_originial = $ReportLostTimeDetailPanel2ChartContainer.height();
                                    div_chart_width_originial = $ReportLostTimeDetailPanel2ChartContainer.width();
                                }
                                else {
                                }

                            }
                        }
                    }
                }
            },

            exporting: {
                buttons: {
                    FullScreenButton: {
                        _titleKey: 'Full Screen',
                        text:'Full Screen',
                        onclick: function () {
                            screenfull.toggle($ReportLostTimeDetailPanel2ChartContainer[0]);
                        }
                    }
                }
            }
        });
    }
});
