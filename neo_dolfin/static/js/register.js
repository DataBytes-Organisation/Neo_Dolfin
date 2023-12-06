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