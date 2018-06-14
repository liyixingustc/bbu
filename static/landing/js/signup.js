/**
 * Created by caliburn on 17-3-13.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap');

    $("#register-form").submit(function (e) {

        $.post('/signup/',$(this).serialize(),function (data) {
            if(data.status == 1){
                console.log(data.message)
             }
             else{
                console.log(data.message);

            }
        });

        return false;
    })

});