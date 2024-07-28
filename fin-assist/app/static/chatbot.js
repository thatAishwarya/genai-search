const QUERY_ENDPOINT = "http://127.0.0.1:8000/query";
const COMPARE_ENDPOINT = "http://127.0.0.1:8000/compare";
const PROCESSDOCS_ENDPOINT = "http://127.0.0.1:8000/processdocs";

// Function to add a message to the chat container
function addMessage(message, type, model) {
    const chatMessages = document.querySelector('.chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(type);

    if (type === "bot-message" && model === "compare-both") {
        messageDiv.classList.add('compare-results');
        const llamaMessageDiv = document.createElement('div');
        llamaMessageDiv.classList.add('compare-card');
        llamaMessageDiv.innerHTML = `<strong>Llama 3.1:</strong><br>${formatMessage(message["llama3.1"].answer)}`;

        const gptMessageDiv = document.createElement('div');
        gptMessageDiv.classList.add('compare-card');
        gptMessageDiv.innerHTML = `<strong>GPT 3.5 Turbo:</strong><br>${formatMessage(message["gpt-3.5-turbo"].answer)}`;

        messageDiv.appendChild(llamaMessageDiv);
        messageDiv.appendChild(gptMessageDiv);
    } else {
        messageDiv.innerHTML = formatMessage(message);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to format the message
function formatMessage(message) {
    if (typeof message !== 'string') {
        console.error('Expected a string message, but received:', message);
        return '';
    }
    
    // Replace bold text indicators with <strong> tags
    let formatted = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Split the message into lines
    const lines = formatted.split(/\n+/);

    // Process each line
    let result = '';
    let isList = false;
    lines.forEach(line => {
        if (/^\d+\./.test(line)) {
            // Start or continue a list
            if (!isList) {
                result += '<ul>';
                isList = true;
            }
            // Format list items
            const listItem = line.replace(/^(\d+)\.\s(.+?):\s(.+)$/, '<li><strong>$2</strong>: $3</li>');
            result += listItem;
        } else {
            // End the list if we encounter non-list text
            if (isList) {
                result += '</ul>';
                isList = false;
            }
            // Add non-list text with line breaks
            result += line + '<br>';
        }
    });

    // Close the list if it was open
    if (isList) {
        result += '</ul>';
    }

    return result;
}

// Function to handle the submission of a user query
async function handleQuery() {
    const userQuery = document.getElementById('user-query').value;
    const selectedModel = document.getElementById('model-select').value;
    
    if (!userQuery.trim()) {
        showAlert('Please enter a query.', 'danger');
        return;
    }
    
    // Add the user's query to the chat
    addMessage(userQuery, 'user-query');
    document.getElementById('user-query').value = '';

    try {
        if (selectedModel === 'compare-both') {
            const response = await axios.post(COMPARE_ENDPOINT, { query: userQuery });
            addMessage(response.data, 'bot-message', 'compare-both');
        } else {
            const response = await axios.post(QUERY_ENDPOINT, { query: userQuery, model: selectedModel });
            addMessage(response.data.answer, 'bot-message');
        }
    } catch (error) {
        showAlert(`Error: ${error}`, 'danger');
    }
}

// Function to show alerts
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.appendChild(document.createTextNode(message));
    document.body.appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

// Event listeners
document.getElementById('submit-btn').addEventListener('click', handleQuery);
document.getElementById('user-query').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        handleQuery();
    }
});
document.getElementById('sync-docs-btn').addEventListener('click', async () => {
    try {
        await axios.post(PROCESSDOCS_ENDPOINT);
        showAlert('Documents synchronized successfully!', 'success');
    } catch (error) {
        showAlert(`Error: ${error}`, 'danger');
    }
});

// Sample prompts event listeners
document.querySelectorAll('.sample-prompt').forEach(prompt => {
    prompt.addEventListener('click', function() {
        document.getElementById('user-query').value = this.getAttribute('data-query');
        handleQuery();
        $('.sample-prompts').hide()
    });
});
