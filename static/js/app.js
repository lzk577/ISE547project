// Global variables
let currentSessionId = null;
let uploadedFile = null;
let selectedModel = 'gpt-4'; // Default model

// DOM elements
const newChatBtn = document.getElementById('newChatBtn');
const searchInput = document.getElementById('searchInput');
const chatList = document.getElementById('chatList');
const messages = document.getElementById('messages');
const welcomeMessage = document.getElementById('welcomeMessage');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFileBtn');
const modelSelect = document.getElementById('modelSelect');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChatSessions();
    setupEventListeners();
    autoResizeTextarea();
});

// Setup event listeners
function setupEventListeners() {
    newChatBtn.addEventListener('click', createNewChat);
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    removeFileBtn.addEventListener('click', removeFile);
    searchInput.addEventListener('input', filterChatSessions);
    modelSelect.addEventListener('change', (e) => {
        selectedModel = e.target.value;
        console.log('Model changed to:', selectedModel);
    });
}

// Auto-resize textarea height
function autoResizeTextarea() {
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
}

// Create new chat
async function createNewChat() {
    try {
        const response = await fetch('/api/new-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        currentSessionId = data.session_id;
        clearMessages();
        loadChatSessions();
        removeFile();
    } catch (error) {
        console.error('Failed to create new chat:', error);
        alert('Failed to create new chat. Please try again.');
    }
}

// Load chat sessions list
async function loadChatSessions() {
    try {
        const response = await fetch('/api/chat-sessions');
        const sessions = await response.json();
        renderChatList(sessions);
    } catch (error) {
        console.error('Failed to load chat sessions:', error);
    }
}

// Render chat list
function renderChatList(sessions) {
    chatList.innerHTML = '';
    if (sessions.length === 0) {
        chatList.innerHTML = '<div style="padding: 12px; color: #6b7280; font-size: 14px;">No chat history</div>';
        return;
    }
    
    sessions.forEach(session => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        if (session.id === currentSessionId) {
            chatItem.classList.add('active');
        }
        chatItem.innerHTML = `
            <span class="chat-item-title" title="${escapeHtml(session.title)}">${escapeHtml(session.title)}</span>
            <button class="delete-chat-btn" data-session-id="${session.id}" title="Delete chat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="m19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        `;
        
        // Click title to load chat
        const titleSpan = chatItem.querySelector('.chat-item-title');
        titleSpan.addEventListener('click', (e) => {
            e.stopPropagation();
            loadChat(session.id);
        });
        
        // Click delete button
        const deleteBtn = chatItem.querySelector('.delete-chat-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChat(session.id);
        });
        
        chatList.appendChild(chatItem);
    });
}

// Delete chat session
async function deleteChat(sessionId) {
    if (!confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/chat/${sessionId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            // If deleting current session, clear display
            if (sessionId === currentSessionId) {
                currentSessionId = null;
                clearMessages();
            }
            // Reload chat list
            loadChatSessions();
        } else {
            alert('Failed to delete chat: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Failed to delete chat:', error);
        alert('Failed to delete chat. Please try again.');
    }
}

// Load chat history
async function loadChat(sessionId) {
    try {
        const response = await fetch(`/api/chat/${sessionId}`);
        const chat = await response.json();
        currentSessionId = sessionId;
        clearMessages();
        welcomeMessage.style.display = 'none';
        
        if (chat.messages && chat.messages.length > 0) {
            chat.messages.forEach(msg => {
                addMessageToUI(msg);
            });
        } else {
            welcomeMessage.style.display = 'block';
        }
        
        loadChatSessions();
        scrollToBottom();
    } catch (error) {
        console.error('Failed to load chat:', error);
        alert('Failed to load chat. Please try again.');
    }
}

// Send message
async function sendMessage() {
    const question = messageInput.value.trim();
    if (!question) return;
    
    // Disable send button
    sendBtn.disabled = true;
    
    // Add user message to UI
    const userMessage = {
        type: 'user',
        content: question,
        timestamp: new Date().toISOString()
    };
    addMessageToUI(userMessage);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    welcomeMessage.style.display = 'none';
    scrollToBottom();
    
    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                file: uploadedFile ? uploadedFile.name : null,
                model: selectedModel
            })
        });
        
        const data = await response.json();
        console.log('Backend response:', data); // Debug log
        
        if (data.success) {
            // Add AI response to UI
            addMessageToUI(data.ai_message);
            loadChatSessions(); // Update chat list (title may have changed)
        } else {
            // Handle error response
            const errorMsg = data.error || data.ai_message?.content || 'Failed to send message';
            console.error('Error from backend:', errorMsg);
            addMessageToUI({
                type: 'assistant',
                content: typeof errorMsg === 'string' ? errorMsg : `Error processing request: ${JSON.stringify(errorMsg)}`,
                timestamp: new Date().toISOString()
            });
        }
    } catch (error) {
        console.error('Failed to send message:', error);
        addMessageToUI({
            type: 'assistant',
            content: `Sorry, an error occurred while sending the message: ${error.message}`,
            timestamp: new Date().toISOString()
        });
    } finally {
        sendBtn.disabled = false;
        scrollToBottom();
    }
}

// Add message to UI
function addMessageToUI(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.type}`;
    
    let contentHtml = '';
    if (message.type === 'user') {
        contentHtml = escapeHtml(message.content);
    } else {
        // AI message may contain structured content
        if (typeof message.content === 'object' && message.content !== null) {
            contentHtml = renderAIResponse(message.content);
        } else {
            contentHtml = escapeHtml(message.content);
        }
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${message.type === 'user' ? 'U' : 'AI'}</div>
        <div class="message-content">${contentHtml}</div>
    `;
    messages.appendChild(messageDiv);
}

// Render AI response (supports code, tables, charts, etc.)
function renderAIResponse(content) {
    let html = '';
    
        if (content.code) {
        html += `<div class="code-block">
            <div class="code-header">Generated Code:</div>
            <pre><code>${escapeHtml(content.code)}</code></pre>
        </div>`;
    }
    
    if (content.result) {
        const result = content.result;
        
        if (result.type === 'number') {
            html += `<div class="result-number">
                <strong>Result:</strong> ${result.data}
            </div>`;
        } else if (result.type === 'table') {
            html += `<div class="result-table">
                <table>
                    <thead>
                        <tr>
                            ${result.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${result.data.slice(0, 100).map(row => `
                            <tr>
                                ${result.columns.map(col => `<td>${escapeHtml(String(row[col] || ''))}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                ${result.data.length > 100 ? `<p class="table-note">Showing first 100 rows of ${result.data.length} total rows</p>` : ''}
            </div>`;
        } else if (result.type === 'chart') {
            html += `<div class="result-chart">
                <img src="${result.data}" alt="Chart" style="max-width: 100%; height: auto;">
            </div>`;
        } else if (result.type === 'error') {
            html += `<div class="result-error">
                <strong>Error:</strong> ${escapeHtml(result.data)}
            </div>`;
        } else {
            html += `<div class="result-text">
                ${escapeHtml(result.data)}
            </div>`;
        }
    }
    
    return html || escapeHtml(JSON.stringify(content));
}

// HTML escape
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Clear messages
function clearMessages() {
    messages.innerHTML = '';
    welcomeMessage.style.display = 'block';
}

// Scroll to bottom
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            uploadedFile = file;
            fileName.textContent = file.name;
            fileInfo.style.display = 'flex';
            
            // Show CSV preview
            if (data.preview) {
                showCSVPreview(data.preview);
            }
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('File upload failed:', error);
        alert('File upload failed. Please try again.');
    }
}

// Show CSV preview
function showCSVPreview(preview) {
    const previewHtml = `
        <div class="csv-preview">
            <h3>CSV File Preview</h3>
            <div class="preview-info">
                <p><strong>Rows:</strong> ${preview.shape.rows} | <strong>Columns:</strong> ${preview.shape.columns}</p>
                <p><strong>Column Names:</strong> ${preview.columns.join(', ')}</p>
            </div>
            <div class="preview-table">
                <table>
                    <thead>
                        <tr>
                            ${preview.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${preview.sample_data.slice(0, 5).map(row => `
                            <tr>
                                ${preview.columns.map(col => `<td>${escapeHtml(String(row[col] || ''))}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Add preview to message area
    const previewDiv = document.createElement('div');
    previewDiv.className = 'message assistant';
    previewDiv.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">${previewHtml}</div>
    `;
    messages.appendChild(previewDiv);
    scrollToBottom();
}

// Remove file
function removeFile() {
    uploadedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
}

// Filter chat sessions
function filterChatSessions() {
    const searchTerm = searchInput.value.toLowerCase();
    const chatItems = chatList.querySelectorAll('.chat-item');
    
    chatItems.forEach(item => {
        const title = item.querySelector('.chat-item-title').textContent.toLowerCase();
        if (title.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

