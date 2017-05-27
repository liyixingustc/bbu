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

        var $forecast_check = $(".forecast_check"),
            $daily_revenue = $(".daily_revenue"),
            $reservation_trace = $(".reservation_trace");

        EnableForecastCheck();
        $("#ReportType").change(function () {
            var ReportType = $(this).val();
            if ($.inArray(ReportType,['forecast_check','actuals_check','stay_check']) !== -1 ){
                EnableForecastCheck()
            }
            if ($.inArray(ReportType,['daily_revenue']) !== -1 ){
                EnableDailyRevenue()
            }
            if ($.inArray(ReportType,['reservation_trace']) !== -1 ){
                EnableReservationTrace()
            }
        });

        function EnableForecastCheck() {
            $daily_revenue.find(":input").prop( "disabled", true );
            $daily_revenue.hide();
            $reservation_trace.find(":input").prop( "disabled", true );
            $reservation_trace.hide();
            $forecast_check.find(":input").prop( "disabled", false );
            $forecast_check.show();
        }

        function EnableDailyRevenue() {
            $forecast_check.find(":input").prop( "disabled", true );
            $forecast_check.hide();
            $reservation_trace.find(":input").prop( "disabled", true );
            $reservation_trace.hide();
            $daily_revenue.find(":input").prop( "disabled", false );
            $daily_revenue.show();
        }

        function EnableReservationTrace() {
            $forecast_check.find(":input").prop( "disabled", true );
            $forecast_check.hide();
            $daily_revenue.find(":input").prop( "disabled", true );
            $daily_revenue.hide();
            $reservation_trace.find(":input").prop( "disabled", false );
            $reservation_trace.show();
        }

        $("#AdminTool-form").submit(function (e) {

            var data = $(this).serialize();
            $("#AdminToolTableRefresh").html("Refreshing...");
            if ($('#ReportType').val()==='reservation_trace'){
                $.get('/report/AdminTool/table/create_table/',data,function () {
                    window.location.href = 'reservation_trace/download/';
                    $("#AdminToolTableRefresh").html("Refresh");
                })
            }
            else {
                $("#tables_data").load('/report/AdminTool/table/create_table/',data,function () {
                    $("#AdminToolTableRefresh").html("Refresh");
                });
            }
            return false
        });
    });
});
