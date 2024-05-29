// Get references to DOM elements
const currentConversation = document.getElementById('current-conversation');
const citationHistory = document.getElementById('citation-history');
const queryInput = document.getElementById('query-input');
const sendButton = document.getElementById('send-button');
const clearButton = document.getElementById('clear-button');
const nextButton = document.getElementById('next-button');

// Event listener for send button click
sendButton.addEventListener('click', sendQuery);

// Event listener for clear button click
clearButton.addEventListener('click', clearChat);

// Add state-related stuff
let currentPage = 0;
let lastQuery = '';

// Event listener for next-button click
nextButton.addEventListener('click', fetchNextPage);

// Function to send user query to the backend
function sendQuery() {
    const query = queryInput.value.trim();
    if (query !== '') {
        // Store the last query
        lastQuery = query;

        // Reset the current page
        currentPage = 0;

        // Display user query in the current conversation
        const userQueryElement = document.createElement('div');
        userQueryElement.classList.add('user-message');
        userQueryElement.innerHTML = `<strong>You:</strong> ${query}`;
        currentConversation.appendChild(userQueryElement);

        // Display loading message in the current conversation
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('loading-message');

        // Create the loader element with custom animation
        const loader = document.createElement('div');
        loader.className = 'loader --9';

        // Add loader to the loading message container
        loadingElement.appendChild(loader);

        // Optional: Add text message if needed
        const textNode = document.createElement('span');
        textNode.textContent = ' Retrieving response...';
        loadingElement.appendChild(textNode);

        // Append the loading message to the conversation
        currentConversation.appendChild(loadingElement);

        // Send POST request to the backend API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query, clear_history: true })
        })
        .then(response => response.json())
        .then(data => {
            // Remove the loading message from the current conversation
            currentConversation.removeChild(loadingElement);

            // Display the response in the current conversation
            const responseElement = document.createElement('div');
            responseElement.classList.add('assistant-message');
            responseElement.innerHTML = `<strong>Cobwebb:</strong><br>${formatResponse(data.response)}`;
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
            errorElement.classList.add('error-message');
            errorElement.textContent = 'Cobwebb is having trouble at the moment. Please try again later.';
            currentConversation.appendChild(errorElement);
        });
    }
}

// Function to fetch the next page of responses
function fetchNextPage() {
    const query = lastQuery; // Use the last query stored

    if (query !== '') {
        // Display loading message in the current conversation
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('loading-message');

        // Create the loader element with custom animation
        const loader = document.createElement('div');
        loader.className = 'loader --9';

        // Add loader to the loading message container
        loadingElement.appendChild(loader);

        // Optional: Add text message if needed
        const textNode = document.createElement('span');
        textNode.textContent = ' Retrieving response...';
        loadingElement.appendChild(textNode);

        // Append the loading message to the conversation
        currentConversation.appendChild(loadingElement);

        // Send POST request to the backend API
        fetch('/api/next', {
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
            responseElement.innerHTML = `<strong>Cobwebb:</strong><br>${formatResponse(data.response)}`;
            currentConversation.appendChild(responseElement);

            // Display the citations in the citation history
            const citationsElement = document.createElement('div');
            citationsElement.classList.add('citation-item');
            citationsElement.innerHTML = `<strong>Citations:</strong><br>${formatCitations(data.citations)}`;
            citationHistory.appendChild(citationsElement);
        })
        .catch(error => {
            console.error('Error:', error);
            // Remove the loading message from the current conversation on error
            currentConversation.removeChild(loadingElement);
            // Display error message in the current conversation
            const errorElement = document.createElement('div');
            errorElement.classList.add('error-message');
            errorElement.textContent = 'Cobwebb is having trouble at the moment. Please try again later.';
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