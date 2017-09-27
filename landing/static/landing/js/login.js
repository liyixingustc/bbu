/**
 * Created by caliburn on 17-3-13.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        Cookies = require('js-cookie');

    var $checkbox = $('#checkbox1'),
        $username = $('#username'),
        $password = $('#password');

    var remember = Cookies.get('remember');
    if ( remember === 'true' ) {
        var username = Cookies.get('username');
        var password = Cookies.get('password');
        // autofill the fields
        $checkbox.prop('checked', true);
        $username.val(username);
        $password.val(password);
    }else {
        $checkbox.prop('checked', false);
        $username.val('');
        $password.val('');
    }

    $checkbox.click(function () {
        set_cookies()
    });

    $("#login-form").submit(function (e) {
        set_cookies();
        $.post('/login/',$(this).serialize(),function (data) {
            if(data.status === 1){
                window.location.href = data.url
             }
             else{
                console.log(data.message);

            }
        });

        return false;
    });

    function set_cookies() {
        if ($checkbox.is(':checked')) {
            var username = $username.val();
            var password = $password.val();

            // set cookies to expire
            Cookies.set('username', username, { expires: 365 });
            Cookies.set('password', password, { expires: 365 });
            Cookies.set('remember', true, { expires: 365 });
        } else {
            // reset cookies
            Cookies.remove('username');
            Cookies.remove('password');
            Cookies.remove('remember');
        }
    }

});