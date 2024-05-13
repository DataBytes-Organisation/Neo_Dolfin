// Function to toggle password visibility
function togglePasswordVisibility(inputId) {
    const passwordInput = document.getElementById(inputId);
    const toggleBtn = document.getElementById(inputId + '-toggle');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = 'Hide';
    } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = 'Show';
    }
}

// Event listeners for toggle buttons
document.getElementById('togglePasswordBtn').addEventListener('click', function() {
    togglePasswordVisibility('password-input');
});

document.getElementById('toggleConfirmPasswordBtn').addEventListener('click', function() {
    togglePasswordVisibility('confirm_password_input');
});