
// Configuration settings
const config = {
    QUERY_ENDPOINT: "http://127.0.0.1:8000/query",
    COMPARE_ENDPOINT: "http://127.0.0.1:8000/compare",
    PROCESSDOCS_ENDPOINT: "http://127.0.0.1:8000/processdocs",
    DATA_DIRECTORY: '../data/TCA/'
};

// State to hold file content and filename
let attachedFileContent = '';
let attachedFileName = '';

// Function to add a message to the chat container
function addMessage(message, type, model) {
    const chatMessages = document.querySelector('.chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(type);

    if (type === "bot-message" && model === "compare-both") {
        messageDiv.classList.add('compare-results');

        ['llama3.1', 'gpt-3.5-turbo'].forEach(modelKey => {
            const modelMessageDiv = document.createElement('div');
            modelMessageDiv.classList.add('compare-card');
            modelMessageDiv.innerHTML = `<strong>${modelKey.replace('.', ' ')}:</strong><br>${formatMessage(message[modelKey].answer)}`;
            
            const referencesHTML = getReferencesHTML(message[modelKey]);
            if (referencesHTML) {
                const referencesDiv = document.createElement('div');
                referencesDiv.classList.add('references');
                referencesDiv.innerHTML = referencesHTML;
                modelMessageDiv.appendChild(referencesDiv);
            }
            if(message[modelKey].time_taken)
                appendTimeDiv(modelMessageDiv, message[modelKey].time_taken);
            messageDiv.appendChild(modelMessageDiv);
        });
    } else {
        messageDiv.innerHTML = formatMessage(message.answer);
        
        const referencesHTML = getReferencesHTML(message);
        if (referencesHTML) {
            const referencesDiv = document.createElement('div');
            referencesDiv.classList.add('references');
            referencesDiv.innerHTML = referencesHTML;
            messageDiv.appendChild(referencesDiv);
        }
        if(message.time_taken)
            appendTimeDiv(messageDiv, message.time_taken);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    addReferenceLinkListeners(messageDiv);
}

function appendTimeDiv(parentDiv, timeTaken) {
    const timeDiv = document.createElement('div');
    timeDiv.classList.add('time');
    timeDiv.innerText = `Time: ${Math.abs(timeTaken)} s`;
    parentDiv.appendChild(timeDiv);
}

// Function to format the message
function formatMessage(message) {
    if (typeof message !== 'string') {
        console.error('Expected a string message, but received:', message);
        return '';
    }

    let formatted = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    const lines = formatted.split(/\n+/);

    let result = '';
    let isList = false;
    lines.forEach(line => {
        if (/^\d+\./.test(line)) {
            if (!isList) {
                result += '<ol>';
                isList = true;
            }
            result += line.replace(/^(\d+)\.\s*(.+)$/, '<li>$2</li>');
        } else {
            if (isList) {
                result += '</ol>';
                isList = false;
            }
            result += line + '<br>';
        }
    });

    if (isList) result += '</ol>';

    return result;
}

// Function to get references HTML
function getReferencesHTML(message) {
    const references = message.references || [];
    if (references.length === 0) return '';

    let referencesHTML = '<br/><br/><strong>References:</strong><ul>';
    references.forEach(ref => {
        const url = `${config.DATA_DIRECTORY}${ref.filename}#page=${ref.page_num}`;
        referencesHTML += `<li><a href="${url}" target="_blank">${ref.filename} - Page ${ref.page_num}</a></li>`;
    });
    referencesHTML += '</ul>';

    return referencesHTML;
}

// Function to add event listeners to reference links
function addReferenceLinkListeners(container) {
    container.querySelectorAll('a[href^="' + config.DATA_DIRECTORY + '"]').forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const url = link.getAttribute('href');
            window.open(url, '_blank');
        });
    });
}

// Function to handle the submission of a user query
async function handleQuery() {
    const userQuery = document.getElementById('user-query').value.trim();

    if (!userQuery && !attachedFileContent.trim()) {
        showAlert('Please enter a query or attach a file.', 'danger');
        return;
    }

    if (userQuery) {
        const combinedQuery = userQuery + (attachedFileContent ? `\n\nFile Content:\n${attachedFileContent}` : '');
        addMessage({ answer: userQuery, references: [] }, 'user-query'); 
        document.getElementById('user-query').value = '';
        showTypingIndicator();
        try {
            const selectedModel = document.getElementById('model-select').value;
            const endpoint = selectedModel === 'compare-both' ? config.COMPARE_ENDPOINT : config.QUERY_ENDPOINT;
            const response = await axios.post(endpoint, { query: combinedQuery, model: selectedModel });
            addMessage(response.data, 'bot-message', selectedModel === 'compare-both' ? 'compare-both' : '');
        } catch (error) {
            showAlert(`Error: ${error}`, 'danger');
        }
        $('#sample-prompts').hide();
        hideTypingIndicator();
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

// Function to show typing indicator
function showTypingIndicator() {
    const chatMessages = document.querySelector('.chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.classList.add('bot-message');
    typingDiv.innerHTML = "Typing...";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to hide typing indicator
function hideTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) typingDiv.remove();
}

// Function to extract text from PDF
async function extractTextFromPDF(file) {
    const fileReader = new FileReader();
    return new Promise((resolve, reject) => {
        fileReader.onload = async function(e) {
            try {
                const typedarray = new Uint8Array(e.target.result);
                const pdf = await pdfjsLib.getDocument(typedarray).promise;
                let text = '';

                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                    const page = await pdf.getPage(pageNum);
                    const content = await page.getTextContent();
                    text += content.items.map(item => item.str).join(' ') + '\n';
                }

                text = text.replace(/\n\s*\n/g, '\n').trim();
                resolve(text);
            } catch (error) {
                reject(error);
            }
        };

        fileReader.onerror = function() {
            reject(new Error('Failed to read file'));
        };

        fileReader.readAsArrayBuffer(file);
    });
}

// Event listener for file input
document.getElementById('file-upload').addEventListener('change', async function(event) {
    const file = event.target.files[0];
    if (file) {
        if (file.type === 'application/pdf') {
            try {
                attachedFileContent = await extractTextFromPDF(file);
                attachedFileName = file.name;
                displayAttachedFile();
            } catch (error) {
                showAlert(`Error extracting text from PDF: ${error.message}`, 'danger');
            }
        } else if (file.type === 'text/plain') {
            const reader = new FileReader();
            reader.onload = function(e) {
                attachedFileContent = e.target.result.trim();
                attachedFileName = file.name;
                displayAttachedFile();
            };
            reader.readAsText(file);
        } else {
            showAlert('Unsupported file type. Please upload a text or PDF file.', 'danger');
        }
    }
});

// Function to display attached file information
function displayAttachedFile() {
    let fileInfoDiv = document.getElementById('file-info');
    if (!fileInfoDiv) {
        fileInfoDiv = document.createElement('div');
        fileInfoDiv.id = 'file-info';
        document.querySelector('.chat-messages').appendChild(fileInfoDiv);
    }
    fileInfoDiv.innerHTML = `<strong style="color: red;">Attached File:</strong> ${attachedFileName}`;
}

// Sample prompts event listeners
document.querySelectorAll('.sample-prompt').forEach(prompt => {
    prompt.addEventListener('click', function() {
        document.getElementById('user-query').value = this.getAttribute('data-query');
        handleQuery();
    });
});

// Event listeners
document.getElementById('submit-btn').addEventListener('click', handleQuery);
document.getElementById('user-query').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') handleQuery();
});
document.getElementById('sync-docs-btn').addEventListener('click', async () => {
    try {
        await axios.post(config.PROCESSDOCS_ENDPOINT);
        showAlert('Documents synchronized successfully!', 'success');
    } catch (error) {
        showAlert(`Error: ${error}`, 'danger');
    }
});
document.getElementById('attachment-icon').addEventListener('click', () => {
    document.getElementById('file-upload').click();
});
