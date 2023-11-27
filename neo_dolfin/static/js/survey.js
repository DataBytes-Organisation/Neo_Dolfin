function showHideTextArea() {
    var noRadioButton = document.getElementById('dashboard-question-no');
    var textAreaContainer = document.getElementById('textAreaContainer');

    if (noRadioButton.checked) {
        textAreaContainer.style.display = 'block';
    } else {
        textAreaContainer.style.display = 'none';
    }
}

// script.js
function changeColor(element) {
    // Convert HTMLCollection to an array
    var faces = Array.from(document.getElementsByClassName('face'));

    // Reset background color for all elements
    faces.forEach(function (face) {
        face.style.backgroundColor = ''; // Reset to default or you can specify another color
    });

    // Change background color for the clicked element
    element.style.backgroundColor = 'rgba(225, 225, 225, 0.5)';
}

