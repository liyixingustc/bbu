/**
 * Created by caliburn on 17-3-13.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap');

    $("#login-form").submit(function (e) {

        $.post('/login/',$(this).serialize(),function (data) {
            if(data.status === 1){
                window.location.href = data.url
             }
             else{
                console.log(data.message);

            }
        });

        return false;
    })

});