function showHideTextArea(radioButtonId, containerId) {
    var noRadioButton = document.getElementById(radioButtonId);
    var textAreaContainer = document.getElementById(containerId);

    if (noRadioButton.checked) {
        textAreaContainer.style.display = 'block';
    } else {
        textAreaContainer.style.display = 'none';
    }
}

function changeColor(element, questionId, satisfactionLevel) {
    console.log('Question ID: ' + questionId);
    console.log('Selected satisfaction level: ' + satisfactionLevel);

    var faces = document.querySelectorAll('#' + questionId + ' .face');

    // Remove 'selected' class from all faces in the container
    faces.forEach(function (face) {
        face.classList.remove('selected');
        face.style.backgroundColor = '';  // Reset background color
    });

    // Add 'selected' class to the clicked face
    element.classList.add('selected');

    // Change background color for the selected face
    element.style.backgroundColor = 'rgba(225, 225, 225, 0.5)';
}


function countWords(textboxClass, wordCountId) {
    var textarea = document.querySelector('.' + textboxClass);
    var wordCountElement = document.getElementById(wordCountId);
    var text = textarea.value.trim();
    var words = text.split(/\s+/);

    if (words.length > 100) {
        var truncatedText = words.slice(0, 100).join(' ');
        textarea.value = truncatedText;
        words = truncatedText.split(/\s+/);
    }

    wordCountElement.textContent = words.length + ' words';
}

function submitForm() {
    // Get values for question 1
    var question1_yes = document.getElementById('dashboard-question-yes1') ? document.getElementById('dashboard-question-yes1').checked : null;
    var question1_no = document.getElementById('dashboard-question-no1') ? document.getElementById('dashboard-question-no1').checked : null;
    var text_box_1 = document.getElementById('text-box-1') ? document.getElementById('text-box-1').value : null;

    // Get value for question 2 (satisfaction faces)
    var satisfaction_value = getSelectedFaceValue('faces2');

    // Get values for question 3
    var ease_of_access_value = getSelectedFaceValue('faces3');

    // Get values for question 4
    var helpful_features_yes = document.getElementById('dashboard-question-yes2') ? document.getElementById('dashboard-question-yes2').checked : null;
    var helpful_features_no = document.getElementById('dashboard-question-no2') ? document.getElementById('dashboard-question-no2').checked : null;
    var text_box_2 = document.getElementById('text-box-2') ? document.getElementById('text-box-2').value : null;

    // Get values for question 5
    var challenges_yes = document.getElementById('dashboard-question-yes3') ? document.getElementById('dashboard-question-yes3').checked : null;
    var challenges_no = document.getElementById('dashboard-question-no3') ? document.getElementById('dashboard-question-no3').checked : null;
    var text_box_3 = document.getElementById('text-box-3') ? document.getElementById('text-box-3').value : null;

    // Get value for question 6 (frequency faces)
    var frequency_value = getSelectedFaceValue('faces4');

    // Get values for additional features (question 7)
    var additional_features = document.getElementById('text-box-4') ? document.getElementById('text-box-4').value : null;

    // Get values for privacy and security concerns (question 8)
    var privacy_security_concerns = document.getElementById('text-box-5') ? document.getElementById('text-box-5').value : null;

    // Get value for question 9 (frequency faces)
    var feelings_questions = getSelectedFaceValue('faces1');

    // Create the surveyData object
    var surveyData = {
        "question_1_yes": question1_yes,
        "question_1_no": question1_no,
        "text_box_1": text_box_1,
        "satisfaction_value": satisfaction_value,
        "ease_of_access_value": ease_of_access_value,
        "helpful_features_yes": helpful_features_yes,
        "helpful_features_no": helpful_features_no,
        "text_box_2": text_box_2,
        "challenges_yes": challenges_yes,
        "challenges_no": challenges_no,
        "text_box_3": text_box_3,
        "frequency_value": frequency_value,
        "additional_features": additional_features,
        "privacy_security_concerns": privacy_security_concerns,
        "feelings_question":feelings_questions
    };

    // Convert surveyData object to JSON
    var jsonData = JSON.stringify(surveyData);

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: jsonData,
    })
    .then(response => response.text())
    .then(data => {
        console.log(data);  // Log the response from the server
    })
    .catch((error) => {
        console.error('Error:', error);
    });

}

// function getSelectedFaceValue(containerId) {
//     var facesContainer = document.getElementById(containerId);
//     var selectedFace = facesContainer.querySelector('.selected');
//     return selectedFace ? parseInt(selectedFace.textContent) : null;
// }
function getSelectedFaceValue(containerId) {
    var facesContainer = document.getElementById(containerId);
    var selectedFace = facesContainer.querySelector('.selected');
    
    if (selectedFace) {
        var selectedValue = parseInt(selectedFace.textContent);

        // Check if the parsed value is a valid number
        if (!isNaN(selectedValue)) {
            return selectedValue;
        } else {
            console.error('Invalid face value:', selectedFace.textContent);
        }
    } else {
        console.error('No face selected in container:', containerId);
    }

    return null;
}



