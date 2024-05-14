document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle password visibility
    function togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const toggleButton = document.getElementById('togglePassword');

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleButton.textContent = 'Hide';
        } else {
            passwordInput.type = 'password';
            toggleButton.textContent = 'Show';
        }
    }

    // Event listener for toggle button click
    document.getElementById('togglePassword').addEventListener('click', function() {
        togglePasswordVisibility();
    });
});
