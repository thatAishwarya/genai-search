const QUERY_ENDPOINT = "http://127.0.0.1:8000/query";
const PROCESSDOCS_ENDPOINT = "http://127.0.0.1:8000/processdocs";

// Function to add a message to the chat container
function addMessage(message, type) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(type);
    messageDiv.innerHTML = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to the bottom
}

// Function to show typing indicator
function showTypingIndicator() {
    const chatContainer = document.getElementById('chat-container');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.classList.add('bot-message');
    typingDiv.innerHTML = "Typing...";
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to the bottom
}

// Function to hide typing indicator
function hideTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Sync Documents button event
document.getElementById('sync-docs-btn').addEventListener('click', async () => {
    try {
        const response = await axios.post(PROCESSDOCS_ENDPOINT);
        if (response.status === 200) {
            addMessage("Documents processed and embeddings updated.", "bot-message");
        } else {
            addMessage(`Failed to process documents: ${response.data}`, "bot-message");
        }
    } catch (error) {
        addMessage(`Error: ${error}`, "bot-message");
    }
});

// Submit button event
document.getElementById('submit-btn').addEventListener('click', async () => {
    const userQueryInput = document.getElementById('user-query');
    const userQuery = userQueryInput.value;
    if (userQuery) {
        addMessage(userQuery, "user-query");
        userQueryInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await axios.post(QUERY_ENDPOINT, { query: userQuery });
            const responseData = response.data;

            // Hide typing indicator
            hideTypingIndicator();

            // Format bot response
            let botMessage = `**Answer:** ${responseData.answer || "No answer found."}\n\n`;
            if (responseData.referees && responseData.referees.length > 0) {
                botMessage += `**Referees:** ${responseData.referees.join(', ')}\n\n`;
            } else {
                botMessage += "No referees found.\n\n";
            }
            if (responseData.suggestions && responseData.suggestions.length > 0) {
                botMessage += `**Suggested Queries:** ${responseData.suggestions.join(', ')}`;
            } else {
                botMessage += "No suggestions available.";
            }

            addMessage(botMessage, "bot-message");
        } catch (error) {
            // Hide typing indicator
            hideTypingIndicator();
            addMessage(`Error: ${error}`, "bot-message");
        }
    } else {
        alert("Please enter a query.");
    }
});
