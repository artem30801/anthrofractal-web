function CountDownTimer(expire_date, id) {
    var end = new Date(expire_date);

    var _second = 1000;
    var _minute = _second * 60;
    var _hour = _minute * 60;
    var _day = _hour * 24;

    var timer;

    var display = document.getElementById(id);
    var days_display = display.querySelector('[data-type="days"]');
    var hours_display = display.querySelector('[data-type="hours"]');
    var minutes_display = display.querySelector('[data-type="minutes"]');
    var seconds_display = display.querySelector('[data-type="seconds"]');


    function showRemaining(reload = true) {
        var now = new Date();
        var delta = end - now;

        if (delta < 0) {
            // Timer has expired
            clearInterval(timer);
            display.innerHTML = 'Update inbound!';
            if (reload){
                window.location.reload(); // don't reload the page on initial countdown render
            }
            return true;
        }

        var days = Math.floor(delta / _day);
        var hours = Math.floor((delta % _day) / _hour);
        var minutes = Math.floor((delta % _hour) / _minute);
        var seconds = Math.floor((delta % _minute) / _second);

        if (days > 0){
            days_display.innerHTML = days + ' ' + (days > 1 ? 'days' : 'day') + ' | '; 
        }
        if (hours > 0){
            hours_display.innerHTML = hours + ' '+ (hours > 1 ? 'hours' : 'hour') + ' | ';
        }
        if (minutes > 0){
            minutes_display.innerHTML = minutes + ' ' + (minutes > 1 ? 'minutes' : 'minute') + ' | ';
        }
        
        seconds_display.innerHTML = seconds + ' ' + (seconds != 1 ? 'seconds' : 'second');

        return false;
    }

    var expired = showRemaining(false); // show countdown immediately first time
    if (!expired){ // if timer already expired - don't start new
        timer = setInterval(showRemaining, 1000);
    }
}