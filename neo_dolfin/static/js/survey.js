responses=[]

function showHideTextArea(radioButtonId, containerId) {
    responses.push({radioButtonId:radioButtonId});
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
    faces.forEach(function (face) {
        face.style.backgroundColor = '';
    });

    element.style.backgroundColor = 'rgba(225, 225, 225, 0.5)';
}
var wordCountElement = document.getElementById(wordCountId);

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




function submitsurvey() {
    
    
    console.log(responses);
    
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
       
        body: JSON.stringify(responses)
    }).then(function (response) {
        if (response.ok) {
            return response.json();
        } else {
            return Promise.reject(new Error('Failed to load'));
        }
    }).then(function (data) {
        console.log(data);
    }).catch(function (error) {
        console.log('Error: ', error);
    });
}