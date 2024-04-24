// Get references to DOM elements
const currentConversation = document.getElementById('current-conversation');
const citationHistory = document.getElementById('citation-history');
const queryInput = document.getElementById('query-input');
const sendButton = document.getElementById('send-button');
const clearButton = document.getElementById('clear-button');

// Event listener for send button click
sendButton.addEventListener('click', sendQuery);

// Event listener for clear button click
clearButton.addEventListener('click', clearChat);

// Function to send user query to the backend API
function sendQuery() {
    const query = queryInput.value.trim();
    if (query !== '') {
        // Display user query in the current conversation
        const userQueryElement = document.createElement('div');
        userQueryElement.classList.add('user-message');
        userQueryElement.textContent = `User: ${query}`;
        currentConversation.appendChild(userQueryElement);

        // Display loading message in the current conversation
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('loading-message');
        loadingElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Retrieving response...';
        currentConversation.appendChild(loadingElement);

        // Send POST request to the backend API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            // Remove the loading message from the current conversation
            currentConversation.removeChild(loadingElement);

            // Display the response in the current conversation
            const responseElement = document.createElement('div');
            responseElement.classList.add('assistant-message');
            responseElement.innerHTML = `<strong>Assistant:</strong><br>${formatResponse(data.response)}`;
            currentConversation.appendChild(responseElement);

            // Add the current conversation to the conversation history
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');
            historyItem.innerHTML = `
                <strong>User:</strong> ${query}<br>
                <strong>Assistant:</strong><br>${formatResponse(data.response)}
            `;

            // Display the citations in the citation history
            const citationsElement = document.createElement('div');
            citationsElement.classList.add('citation-item');
            citationsElement.innerHTML = `<strong>Citations:</strong><br>${formatCitations(data.citations)}`;
            citationHistory.appendChild(citationsElement);

            // Clear the input field
            queryInput.value = '';
        })
        .catch(error => {
            console.error('Error:', error);
            // Remove the loading message from the current conversation on error
            currentConversation.removeChild(loadingElement);
            // Display error message in the current conversation
            const errorElement = document.createElement('div');
            errorElement.classList.add('error-message');            errorElement.textContent = 'Oops! Something went wrong. Please try again.';
            currentConversation.appendChild(errorElement);
        });
    }
}

// Function to clear the chat
function clearChat() {
    // Clear the current conversation
    currentConversation.innerHTML = '';
  
    // Clear the citation history
    citationHistory.innerHTML = '<h4>Citation History</h4>';
  
    // Clear the input field
    queryInput.value = '';
  
    // Clear the conversation history
    conversation_history.length = 0;
  }

// Function to format the generated response
function formatResponse(response) {
    return response.replace(/\n/g, '<br>');
}

// Function to format the citations
function formatCitations(citations) {
    return citations.replace(/\n/g, '<br>');
}