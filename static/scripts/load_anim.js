function LoadAnimDelay(start=0.5, between=0.75) {
    var elements = document.querySelectorAll('.load-animated')
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        var delay = start + between*i;
        element.style.animationDelay = delay + 's';
        console.log(element, delay, element.style.animationDelay, element.style)
    }
}

//var start = 0.5;
//var between = 0.75;
//var elements = document.querySelectorAll('.load-animated')
//for (var i = 0; i < elements.length; i++) {
//    var element = elements[i];
//    var delay = start + between*i;
//    element.style.animationDelay = delay + 's';
//    console.log(element, delay, element.style.animationDelay, element.style)
//}