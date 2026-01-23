document.getElementById('authForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Here you can add your authentication logic (e.g., API call)
    console.log('Username:', username);
    console.log('Password:', password);

    // You can then submit the form data to your server
    // For example, using fetch() to send a POST request
});
