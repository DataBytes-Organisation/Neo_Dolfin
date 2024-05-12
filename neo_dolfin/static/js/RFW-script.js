function onlyOneCheckbox(checkbox, groupName) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"][name="' + groupName + '"]');
    checkboxes.forEach((item) => {
        if (item !== checkbox) item.checked = false;
    });
}

// Function to calculate and save the score to local storage
function saveScore(score) {
    localStorage.setItem('financialWellbeingScore', score);
}

// Function to redirect to the dashboard
function redirectToDashboard() {
    window.location.href = '/dash';
}

document.getElementById('calculateButton').addEventListener('click', function() {
    var totalQuestions = 10;
    var allRowsSelected = true;

    for (var i = 1; i <= totalQuestions; i++) {
        var checkboxes = document.querySelectorAll('input[type="checkbox"][name="q' + i + '"]');
        var isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

        if (!isChecked) {
            allRowsSelected = false;
            alert('Please select at least one option for question ' + i);
            break;
        }
    }

    if (allRowsSelected) {
        calculateSum(); 
    }
});

function calculateSum() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    var sum = 0;
    checkboxes.forEach(function(checkbox) {
        sum += parseInt(checkbox.value, 10);
    });
    sum=parseFloat(sum)*2.5
    alert("Your financial wellbeing score is " + sum);

    saveScore(sum);
    redirectToDashboard();
}