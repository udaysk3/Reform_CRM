// login.js

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const forgotPasswordLink = document.querySelector('.forgot-password');
    const backToLoginLinks = document.querySelectorAll('.back-to-login');
    const loginFormContainer = document.getElementById('login-form');
    const passwordResetContainer = document.getElementById('password-reset-form');
    const passwordResetConfirmation = document.getElementById('password-reset-confirmation');
    const passwordResetForm = document.querySelector('.password-reset-form');

    // Show Password Reset Form
    forgotPasswordLink.addEventListener('click', function(e) {
        e.preventDefault();
        loginFormContainer.style.display = 'none';
        loginFormContainer.setAttribute('aria-hidden', 'true');

        passwordResetContainer.style.display = 'block';
        passwordResetContainer.setAttribute('aria-hidden', 'false');

        // Set focus to the email input field
        document.getElementById('reset-email').focus();
    });

    // Show Login Form
    backToLoginLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            passwordResetContainer.style.display = 'none';
            passwordResetContainer.setAttribute('aria-hidden', 'true');

            passwordResetConfirmation.style.display = 'none';
            passwordResetConfirmation.setAttribute('aria-hidden', 'true');

            loginFormContainer.style.display = 'block';
            loginFormContainer.setAttribute('aria-hidden', 'false');

            // Set focus to the username input field
            document.getElementById('username').focus();
        });
    });

    // Handle Password Reset Form Submission
    passwordResetForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Optionally, send form data via AJAX here

        // Hide the password reset form
        passwordResetContainer.style.display = 'none';
        passwordResetContainer.setAttribute('aria-hidden', 'true');

        // Show the confirmation message
        passwordResetConfirmation.style.display = 'block';
        passwordResetConfirmation.setAttribute('aria-hidden', 'false');

        // Optionally, reset the form fields
        passwordResetForm.reset();

        // Set focus to the back to login link
        passwordResetConfirmation.querySelector('.back-to-login').focus();
    });
});
