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

        parent_col_sm = card_elements[i].parentElement

        column_col_elems = parent_col_sm.querySelectorAll('.card')
        // console.log(column_col_elems)
        column_col_elems.forEach((item) => {
        empty_elements = 0
        if (item.style.display == '') {
            console.log("cool")
            empty_elements++
        }

        });
        console.log(empty_elements)
        console.log(column_col_elems.length)
        if (empty_elements == column_col_elems.length) {

        // parent_col_sm.previousElementSibling.style.cssText += "display: none"

        // var emptyCol = document.createElement('div');
        // emptyCol.className = "col-sm";

        // parent_col_sm.appendChild(emptyCol);

        }


    }
    else {
        card_elements[i].classList.add("hide-card-default");
        card_elements[i].classList.remove("show-card");

    }
    }

}