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
        Highcharts = require('Highcharts'),
        HighchartsMore = require('Highcharts-more'),
        HighchartsExporting = require('Highcharts-exporting');


    $(function () {
        init();
        event()
    });

    function init() {

    }

    function event() {

        $("#ReportTimeDetailPanel1Form1FormId").submit(function (e) {

            var data = $(this).serialize();
            $("#ReportTimeDetailPanel1Form1Submit").html("Running...");
            $.get('Panel1/Form1/Submit/',data,function (data) {
                create_waterfall(data);
                $("#ReportTimeDetailPanel1Form1Submit").html("Finished");
            });

            return false
        });
    }

    function create_waterfall(data) {
        Highcharts.chart('ReportTimeDetailPanel2Chart1', {
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
                           '<b>Occ: '+ this.count +'</b>'
                }
            },

            series: [{
                data: data,
                // data: [ {
                //     name: 'Product Revenue',
                //     y: 569000,
                //     colorIndex: 8
                // }, {
                //     name: 'Service Revenue',
                //     y: 231000,
                //     colorIndex: 11
                // }, {
                //     name: 'Fixed Costs',
                //     y: -2000,
                //     colorIndex: 8
                // }, {
                //     name: 'Variable Costs',
                //     y: -233000,
                //     colorIndex: 9
                // }, {
                //     name: 'Total',
                //     isSum: true,
                //     colorIndex: 10
                // }],
                dataLabels: {
                    enabled: true,
                    formatter: function () {
                        return Math.abs(this.y).toFixed(1) + ' (' + this.point.count + ')';
                    },
                    style: {
                        fontWeight: 'bold'
                    }
                },
                pointPadding: 0
            }]
        });
    }
});
