async function submitQuery() {
    const question = document.getElementById('question').value;
    const askButton = document.getElementById('askButton');
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
    }, 1500);  // Update progress every 1500ms

    socket.onopen = async function(e) {
        socket.send(JSON.stringify({ text: question }));
    };

   
    socket.onmessage = function(event) {
        clearInterval(intervalId);
        progressBar.style.width = '100%';  // Set progress to 100%
        const data = JSON.parse(event.data);
        if (data.documents === "NEED_MORE_INFO") {
            askButton.classList.remove('button-loading');
            // Prompt the user for more information
            document.getElementById('output').innerText = data.response;
            // Send the updated question to the server
            socket.send(JSON.stringify({ text: question }));
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


document.getElementById('openArticles').addEventListener('click', function() {
    var directory = document.querySelector('.directory-section');
    directory.classList.toggle('open');
});

document.getElementById('closeArticles').addEventListener('click', function() {
    var directory = document.querySelector('.directory-section');
    directory.classList.toggle('open');
});

document.getElementById('openLawSelector').addEventListener('click', function() {
    var lawSelector = document.querySelector('.law-section');
    lawSelector.classList.toggle('open');
});

document.getElementById('closeLawSelector').addEventListener('click', function() {
    var lawSelector = document.querySelector('.law-section');
    lawSelector.classList.toggle('open');
});
