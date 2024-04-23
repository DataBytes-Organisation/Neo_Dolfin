var currentTab = 0; // Current tab is set to be the first tab (0)
showTab(currentTab); // Display the current tab

function showTab(n) {
  // This function will display the specified tab of the form...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  //... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("previousPage").style.display = "none";
  } else {
    document.getElementById("previousPage").style.display = "inline";
  }
  if (n == (x.length - 1)) {
    document.getElementById("nextPage").innerHTML = "Submit";
  } else {
    document.getElementById("nextPage").innerHTML = "Next";
  }
  //... and run a function that will display the correct step indicator:
  fixStepIndicator(n)
}

function nextPrev(n) {
    console.log("I am here");
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // if you have reached the end of the form...
  if (currentTab >= x.length) {
    // ... the form gets submitted:
    document.getElementById("regForm").submit();
    return false;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

// $("#nextPage").click(nextPrev(1))

// $("#previousPage").click(nextPrev(-1))


function validateForm() {
  // This function deals with validation of the form fields
  var x, y, i, valid = true;
  x = document.getElementsByClassName("tab");
  y = x[currentTab].getElementsByTagName("input");
  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
    // If a field is empty...
    if (y[i].value == "") {
      // add an "invalid" class to the field:
      y[i].className += " invalid";
      // and set the current valid status to false
      valid = false;
    }
  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid) {
    document.getElementsByClassName("step")[currentTab].className += " finish";
  }
  return valid; // return the valid status
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class on the current step:
  x[n].className += " active";
}

//Address AutoComplete/Validation client-side scripts below - using AddressFinder API
document.addEventListener('DOMContentLoaded', function() {
  const validationCheckbox = document.getElementById('validation');
  const addressLine1 = document.getElementById('address1');
  let widget;

// Initialize AddressFinder Widget
function initAddressFinder() {
  widget = new AddressFinder.Widget(
          addressLine1,
          'H9B6JVYDLM4CRNUKA78E',
          'AU', {
              "address_params": {
                  "au_paf": "1",
                  "post_box": "0"
              },
              "empty_content": "No addresses were found. This could be a new address, or you may need to check the spelling. Learn more"
          }
);

widget.on('address:select', function(fullAddress, metaData) {
  let addressLine1 = metaData.address_line_1;
  let addressLine2 = metaData.address_line_2;
          
  if(metaData.address_line_2) {
    addressLine1 = metaData.address_line_2;
    addressLine2 = metaData.address_line_1;
  }
  // Populates form fields with address elements from the selected address that was autocompleted
  document.getElementById('address1').value = addressLine1;
  document.getElementById('address2').value = addressLine2;
  document.getElementById('suburb').value = metaData.locality_name;
  document.getElementById('state').value = metaData.state_territory;
  document.getElementById('postcode').value = metaData.postcode;
  });
}

// Uninitialised AddressFinder - Used when Skip Address Validation checkbox is checked.
function destroyAddressFinder() {
  if (widget) {
    widget.destroy();
    widget = null;
  }
}

// Download the AddressFinder script and initialize.
function downloadAddressFinder() {
  var script = document.createElement('script');
  script.src = 'https://api.addressfinder.io/assets/v3/widget.js';
  script.async = true;
  script.onload = initAddressFinder;
  document.body.appendChild(script);
}

// Event listener for Skip Address Validation checkbox.
// When Validation checkbox is unchecked, download and initialise AddressFinder and update placeholder text
// When Validation checkbox is checked, uninitialise AddressFinder and update placeholder text
validationCheckbox.addEventListener('change', function() {
  if (this.checked) {
    addressLine1.placeholder = "Address Line 1";
    destroyAddressFinder();
  } 
  else {
    addressLine1.placeholder = "Search address here...";
    downloadAddressFinder();
  }
});

// Initial setup of AddressFinder when the page is first loaded
downloadAddressFinder();
});
// End of Scripts related to Address Validation


// SCRIPTS RELATED TO PASSWORD REQUIREMENT VALIDATION  
//function to collect variables -- the <p> you want to be interactive
function collectElements(varname, id) {
  var varname = document.getElementById(id);
  return varname;
}
//function to add to classList 
function correctClassList(id) {
  id.classList.remove("wrong"); 
  id.classList.add("correct"); 
}
//function to remove from classList 
function wrongClassList(id) {
  id.classList.remove("correct"); 
  id.classList.add("wrong");
}
//function for validation of password (userInput, variableCheck) against requirements 
function checkRequirements(input, variableName, id) {
  if (input.value.match(variableName)) {
    correctClassList(id);
  } else {
    wrongClassList(id);
  }
}

//collect variables
var userInput = collectElements(userInput, "pass");
var letter = collectElements(letter, "letter");
var capital = collectElements(capital, "capital");
var number = collectElements(number, "number");
var symbol = collectElements(symbol, "symbol");
var passwordLength = collectElements(passwordLength, "passwordLength");

//FUNCTION TO CREATE AND CHECK FOR INTERNALLY DENIED STRINGS IN PASSWORDS  
const restrictedStrings = ['123','password','admin','qwerty','asdf','abc','letmein','football','iloveyou','welcome','monkey','login','princess','sunshine','starwars','baseball','access','master','databytes','dolfin','abandon','ability','able','about','above','absence','absent','absolute','abuse','abusive','academic','accede','acceptable','acceptance','accident','accolade','accompany','accomplish','accord','account','accurate','accuse','ache','achieve','acknowledge','acquire','acquit','acronym','across','act','action','active','acitivity','actor','actress','actual','actually','adapt','addiction','addition','address','adequate','adjourn','adjust','administration','admiration','admire','adopt','adoption','adult','advance','advantage','adventure','adventurous','advertise','advice','advise','affair','affect','afford','afraid','after','afternoon',
'again']; 

//declaring function to check password , if contains restrictedString, internalListMessage appears
function checkPassword() {
  const password = document.getElementById("pass").value.toLowerCase(); 
  const internalListMessage = document.getElementById("internalList"); 
  if (containsRestrictedString(password)) {
    internalListMessage.classList.remove("hidden"); 
  } else {
    internalListMessage.classList.add("hidden");
  }
}

//checks user input in password input string against strings within restrictedStrings
function containsRestrictedString(password) {
  for (let i = 0; i <restrictedStrings.length; i++) {
    if (password.includes(restrictedStrings[i])) {
      return true;
    }
  }
  return false;
}

//checks for password length against requirements
function checkLength() {
  //checks for password length 
  var maxlength = 20;
  var minlength = 12;
  if (userInput.value.length >= minlength && userInput.value.length <= maxlength) {
    correctClassList(passwordLength);
  } else {
    wrongClassList(passwordLength);
  }
}

//message box show when user clicks on password field
userInput.onfocus = function() {
  document.getElementById("checkField").style.display = "block"; 
};
//message box hidden when user clicks off password field
userInput.onblur = function() {
  document.getElementById("checkField").style.display = "none";
};

//password requirement validation function
userInput.onkeyup = function() {
  //checks for the 1 lowercase letter
  var lowerCaseLetters = /[a-z]/g; 
  checkRequirements(userInput, lowerCaseLetters, letter);

  //checks for the 1 uppercase letter 
  var upperCaseLetters = /[A-Z]/g;
  checkRequirements(userInput, upperCaseLetters, capital);
  
  //checks for the 1 digit 
  var numbers = /[0-9]/g; 
  checkRequirements(userInput, numbers, number);
  
  //checks for the symbol 
  var symbols = /\W/g;
  checkRequirements(userInput, symbols, symbol);

  //check length requirements
  checkLength();

  //check if password contains any denied strings
  checkPassword();
  
}
//END OF SCRIPTS RELATED TO PASSWORD REQUIREMENT FEATURE
