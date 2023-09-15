filterSelection("all")

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