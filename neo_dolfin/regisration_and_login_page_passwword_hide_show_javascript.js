document.addEventListener("DOMContentLoaded", function() {
  const togglePasswordBtn = document.getElementById("togglePasswordBtn");
  const passwordInput = document.getElementById("password");
  togglePasswordBtn.addEventListener("click", function() {
    togglePasswordVisibility(passwordInput);
  });

  const toggleLoginPasswordBtn = document.getElementById("toggleLoginPasswordBtn");
  const loginPasswordInput = document.getElementById("loginPassword");
  toggleLoginPasswordBtn.addEventListener("click", function() {
    togglePasswordVisibility(loginPasswordInput);
  });
});

function togglePasswordVisibility(inputField) {
  if (inputField.type === "password") {
    inputField.type = "text";
    inputField.nextElementSibling.textContent = "Hide";
  } else {
    inputField.type = "password";
    inputField.nextElementSibling.textContent = "Show";
  }
}
