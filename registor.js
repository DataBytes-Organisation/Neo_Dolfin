// Function to check the uniqueness of characters in the password
function checkPasswordStrength(password) {
    // Regular expressions to check for sequences of characters or numbers
    const sequentialChars = /(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)/i;
    const sequentialNumbers = /(123|234|345|456|567|678|789|890)/;

    // Check for sequential characters or numbers
    if (sequentialChars.test(password) || sequentialNumbers.test(password)) {
        return "weak"; // If found, password is weak
    } else if (password.length >= 8) {
        return "strong"; // If length >= 8 and no sequential, password is strong
    } else {
        return "medium"; // Otherwise, password is medium
    }
}

// Function to update the strength bar color based on password strength
function updateStrengthBar(password) {
    const strengthBar = document.getElementById('strength-bar');
    const strengthLabel = document.getElementById('strength-label');
    const strength = checkPasswordStrength(password);

    // Update strength label
    strengthLabel.textContent = "Strength: " + strength;

    // Update strength bar color
    if (strength === "weak") {
        strengthBar.style.backgroundColor = "red"; // Weak password
    } else if (strength === "medium") {
        strengthBar.style.backgroundColor = "yellow"; // Medium password
    } else {
        strengthBar.style.backgroundColor = "green"; // Strong password
    }
}
