async function submitQuery() {
    const question = document.getElementById('question').value;
    const socket = new WebSocket('ws://localhost:8000/ws');
    
    socket.onopen = async function(e) {
        socket.send(JSON.stringify({ text: question }));
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.response === "NEED_MORE_INFO") {
            // Handle the case where the bot needs more information
        } else {
            document.getElementById('output').innerText = data.response;
            document.getElementById('directory').innerText = data.documents.join('\n');  // Display the top 10 results
        }
    };
    
    socket.onerror = function(error) {
        document.getElementById('output').innerText = 'An error occurred while processing your request.';
        document.getElementById('documents').innerText = '';
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