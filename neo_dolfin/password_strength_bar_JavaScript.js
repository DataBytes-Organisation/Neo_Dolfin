

function checkPasswordStrength(password) {
  var strengthBar = document.getElementById("strengthBar");
  var strengthText = document.getElementById("strengthText");
  var strength = 0;

  // Check for sequential characters
  if (/^(?!.*(.)\1{1})(?!.*(123|234|345|456|567|678|789|890|098|987|876|765|654|543|432|321|210))/.test(password)) {
    strength++;
  }

  // Check for uppercase and lowercase letters
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
    strength++;
  }

  // Check for numbers
  if (/\d/.test(password)) {
    strength++;
  }

  // Check for special characters
  if (/[$&+,:;=?@#|'<>.^*()%!-]/.test(password)) {
    strength++;
  }

  // Check for length
  if (password.length >= 8) {
    strength++;
  }
  if (password.length >= 12) {
    strength++;
  }

  switch (strength) {
    case 0:
      strengthBar.style.width = "0%";
      strengthBar.className = "progress-bar bg-danger";
      strengthText.textContent = "Very Weak";
      break;
    case 1:
      strengthBar.style.width = "20%";
      strengthBar.className = "progress-bar bg-danger";
      strengthText.textContent = "Weak";
      break;
    case 2:
      strengthBar.style.width = "40%";
      strengthBar.className = "progress-bar bg-warning";
      strengthText.textContent = "Fair";
      break;
    case 3:
      strengthBar.style.width = "60%";
      strengthBar.className = "progress-bar bg-info";
      strengthText.textContent = "Good";
      break;
    case 4:
      strengthBar.style.width = "80%";
      strengthBar.className = "progress-bar bg-primary";
      strengthText.textContent = "Strong";
      break;
    case 5:
      strengthBar.style.width = "100%";
      strengthBar.className = "progress-bar bg-success";
      strengthText.textContent = "Very Strong";
      break;
  }
}
