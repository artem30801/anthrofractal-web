var animationDuration = 7000; // in milliseconds

function randomDuration() {
    return (-1 * Math.floor(Math.random() * animationDuration)) + 'ms';
}

var elements = document.querySelectorAll('.glitch')

// Set the animationDelay of each element to a random value
// between 0 and animationDuration:
for (var i = 0; i < elements.length; i++) {
    var element = elements[i];
    var hidden_text = element.getAttribute("data-text") || element.innerText;
    // var hidden_text = element.innerText;

    // insert span elements with fake text
    var before = document.createElement("span");
    before.innerHTML = hidden_text;
    before.classList.add("layers-before");
    before.classList.add("glitch-before");
    element.appendChild(before);

    var after = document.createElement("span");
    after.innerHTML = hidden_text;
    after.classList.add("layers-after");
    after.classList.add("glitch-after");
    element.appendChild(after);

    // apply random delay
    var duration = randomDuration();
    element.style.animationDelay = duration;
    before.style.animationDelay = duration;
    after.style.animationDelay = duration;
}