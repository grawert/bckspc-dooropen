$(function() {

    function setCookie(c_name, value, exdays) {
        var exdate = new Date();
        exdate.setDate(exdate.getDate() + exdays);
        var c_value = escape(value) + ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
        document.cookie = c_name + "=" + c_value;
    }

    function getCookie(c_name) {
        var i, x, y, ARRcookies = document.cookie.split(";");
        for (i = 0; i < ARRcookies.length; i++) {
            x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
            y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
            x = x.replace(/^\s+|\s+$/g, "");
            if (x == c_name) {
                return unescape(y);
            }
        }
    }

    var uid = getCookie('uid');
    console.log(uid);
    $('#user-id').val(uid);

    var lock = false;

    $('.pin-submit').click(function() {

        var uid = $('#user-id').val();
        var password = $('#pin-field').val();
        var opentype = $(this).attr('value');

        if(uid == -1) {
            alert("You have to choose an username to open/close the door");
            return false;
        }

        $('.pin-submit').attr('disabled', 'disabled');

        lock = true;
        var timer = setTimeout(function() {
            lock = false;
            $('.pin-submit').removeAttr('disabled');
        }, 3500);

        $.post('/verify', {'uid': uid, 'password': password, 'type': opentype}, function(result) {

            if(!result) {
                alert('Somethings wrong on the interwebz');
                return false;
            }

            if(result.response == false) {
                switch(Math.floor(Math.random()*3)) {
                    default:
                    case 0:
                        alert("One does not simply walk into backspace");
                        break;
                    case 1:
                        alert("None shall pass!");
                        break;
                    case 2:
                        alert("I'm afraid i can't do that");
                        break;
                }

                return false;
            }

            setCookie('uid', uid, 1337);

            if(opentype == 'Buzzer') {
                alert("The buzzer should ring now");
	    } else if(opentype == 'Open') {
                alert("Your door should open now");
            } else {
                alert("Your door should lock now");
            }

        });

        return false;
    });
});
