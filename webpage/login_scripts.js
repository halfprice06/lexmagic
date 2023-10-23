document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    // Handle login
    console.log(`Login: ${username}, ${password}`);
    // If login is successful, redirect to the main page
    if(username === 'admin' && password === 'admin') { // replace with actual login check
        window.location.href = 'index.html';
    }
});

document.getElementById('signupForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('signupUsername').value;
    const password = document.getElementById('signupPassword').value;
    // Handle signup
    console.log(`Signup: ${username}, ${password}`);
});