async function submitQuery() {
    const question = document.getElementById('question').value;
    
    // Making an API call to the chat endpoint
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: question })
    });
    
    if (response.ok) {
        const data = await response.json();
        document.getElementById('output').innerText = data.response;
        document.getElementById('documents').innerText = data.documents.join('\n');  // Display the top 10 results
    } else {
        document.getElementById('output').innerText = 'An error occurred while processing your request.';
        document.getElementById('documents').innerText = '';
    }
}