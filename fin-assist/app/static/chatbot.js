const QUERY_ENDPOINT = "http://127.0.0.1:8000/query";
const PROCESSDOCS_ENDPOINT = "http://127.0.0.1:8000/processdocs";

// Function to add a message to the chat container
function addMessage(message, type) {
    const chatMessages = document.querySelector('.chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(type);
    messageDiv.innerHTML = message; // Ensure HTML is correctly rendered
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
}

// Function to show typing indicator
function showTypingIndicator() {
    const chatMessages = document.querySelector('.chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.classList.add('bot-message');
    typingDiv.innerHTML = "Typing...";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
}

// Function to hide typing indicator
function hideTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Function to handle sample prompt click
async function handleSamplePromptClick(event) {
    const userQuery = event.target.getAttribute('data-query');
    if (userQuery) {
        addMessage(userQuery, "user-query");

        // Hide sample prompts after the first query is made
        document.getElementById('sample-prompts').style.display = 'none';

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await axios.post(QUERY_ENDPOINT, { query: userQuery });
            const responseData = response.data;

            // Hide typing indicator
            hideTypingIndicator();

            // Format bot response as HTML
            let botMessage = `<strong>Answer:</strong> ${responseData.answer || "No answer found."}<br><br>`;

            if (responseData.referees && responseData.referees.length > 0) {
                botMessage += `<strong>Referees:</strong><ul>`;
                responseData.referees.forEach(referee => {
                    botMessage += `<li>${referee}</li>`;
                });
                botMessage += `</ul><br>`;
            } else {
                botMessage += `No referees found.<br><br>`;
            }

            // if (responseData.suggestions && responseData.suggestions.length > 0) {
            //     botMessage += `<strong>Suggested Queries:</strong><ul>`;
            //     responseData.suggestions.forEach(suggestion => {
            //         botMessage += `<li>${suggestion}</li>`;
            //     });
            //     botMessage += `</ul>`;
            // } else {
            //     botMessage += `No suggestions available.`;
            // }

            addMessage(botMessage, "bot-message");
        } catch (error) {
            // Hide typing indicator
            hideTypingIndicator();
            showAlert(`Error: ${error}`, 'danger');
        }
    }
}

// Sync Documents button event
document.getElementById('sync-docs-btn').addEventListener('click', async () => {
    try {
        const response = await axios.post(PROCESSDOCS_ENDPOINT);
        if (response.status === 200) {
            showAlert("Success: Documents processed and embeddings updated.", 'success');
        } else {
            showAlert(`Failed to process documents: ${response.data}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error}`, 'danger');
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

            // Format bot response as HTML
            let botMessage = `<strong>Answer:</strong> ${responseData.answer || "No answer found."}<br><br>`;

            if (responseData.referees && responseData.referees.length > 0) {
                botMessage += `<strong>Referees:</strong><ul>`;
                responseData.referees.forEach(referee => {
                    botMessage += `<li>${referee}</li>`;
                });
                botMessage += `</ul><br>`;
            } else {
                botMessage += `No referees found.<br><br>`;
            }

            if (responseData.suggestions && responseData.suggestions.length > 0) {
                botMessage += `<strong>Suggested Queries:</strong><ul>`;
                responseData.suggestions.forEach(suggestion => {
                    botMessage += `<li>${suggestion}</li>`;
                });
                botMessage += `</ul>`;
            } else {
                botMessage += `No suggestions available.`;
            }

            addMessage(botMessage, "bot-message");
        } catch (error) {
            // Hide typing indicator
            hideTypingIndicator();
            showAlert(`Error: ${error}`, 'danger');
        }
    } else {
        alert("Please enter a query.");
    }
});

// Attach click event listeners to sample prompts
document.querySelectorAll('.sample-prompt').forEach(prompt => {
    prompt.addEventListener('click', handleSamplePromptClick);
});
