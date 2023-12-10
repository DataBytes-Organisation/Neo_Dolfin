filterSelection("all")

// Makes the clicked button stand out by moving it slightly above the others
// Get the button container and all buttons
const buttonContainer = document.getElementById('navbarNav');
const buttons = buttonContainer.querySelectorAll('.btn');

// Add a click event listener to each button
buttons.forEach(button => {
  button.addEventListener('click', function() {
    // Remove the pressed class from all buttons
    buttons.forEach(btn => btn.classList.remove('pressed-btn'));

    // Add the pressed class to the clicked button
    this.classList.add('pressed-btn');
  });
});


function filterSelection(month) {
    var card_elements, i;
    // console.log(c)
    card_elements = document.getElementsByClassName("card");

    for (i = 0; i < card_elements.length; i++) {

    if (month == "all") {
        card_elements[i].classList.remove("hide-card-default");
        card_elements[i].classList.add("show-card")
    }
    else if ($(card_elements[i]).attr("data-category") == month) {

        card_elements[i].classList.remove("hide-card-default");
        card_elements[i].classList.add("show-card")

    }
    else {
        card_elements[i].classList.add("hide-card-default");
        card_elements[i].classList.remove("show-card");

    }
    }

}