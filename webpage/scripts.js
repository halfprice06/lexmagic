async function submitQuery() {
    const question = document.getElementById('question').value;
    const askButton = document.querySelector('.ask_button button');
    const progressBar = document.getElementById('progress-bar');
    const socket = new WebSocket('ws://localhost:8000/ws');
    
    askButton.classList.add('button-loading');  // Add loading animation
    progressBar.style.display = 'block';  // Show progress bar

    let progress = 0;
    const intervalId = setInterval(() => {
        progress += 5;
        if (progress > 99) {
            clearInterval(intervalId);
        }
        progressBar.style.width = `${progress}%`;
    }, 1500);  // Update progress every 150ms

    socket.onopen = async function(e) {
        socket.send(JSON.stringify({ text: question }));
    };
    
    socket.onmessage = function(event) {
        clearInterval(intervalId);
        progressBar.style.width = '100%';  // Set progress to 100%
        const data = JSON.parse(event.data);
        if (data.response === "NEED_MORE_INFO") {
            // Handle the case where the bot needs more information
        } else {
            document.getElementById('output').innerText = data.response;
            document.getElementById('directory').innerText = data.documents.join('\n');  // Display the top 10 results
        }
        askButton.classList.remove('button-loading');  // Remove loading animation
        progressBar.style.display = 'none';  // Hide progress bar
    };
    
    socket.onerror = function(error) {
        clearInterval(intervalId);
        document.getElementById('output').innerText = 'An error occurred while processing your request.';
        document.getElementById('documents').innerText = '';
        askButton.classList.remove('button-loading');  // Remove loading animation
        progressBar.style.display = 'none';  // Hide progress bar
    };
}

function thumbsUp() {
    // Placeholder for thumbs up action
    console.log("Thumbs up clicked");
}

function thumbsDown() {
    // Placeholder for thumbs down action
    console.log("Thumbs down clicked");
}

document.getElementById('toggleButton').addEventListener('click', function() {
    var directory = document.querySelector('.directory-section');
    var container = document.querySelector('.container');
    directory.classList.toggle('open');
    container.classList.toggle('with-directory');
});