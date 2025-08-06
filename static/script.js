// Multi-User SQL Agent JavaScript

let currentSessionId = null;
let currentUser = null;

// Utility functions
function showStatus(message, type = 'success', duration = 3000) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.classList.remove('hidden');
    
    setTimeout(() => {
        status.classList.add('hidden');
    }, duration);
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

function showAppSections() {
    document.getElementById('appSection').classList.remove('hidden');
    document.getElementById('databaseSetup').classList.remove('hidden');
    document.getElementById('examplesSection').classList.remove('hidden');
}

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const config = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, config);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Authentication functions
async function login() {
    const username = document.getElementById('username').value.trim();
    
    if (!username) {
        showStatus('Please enter a username', 'error');
        return;
    }
    
    try {
        showStatus('Logging in...', 'loading');
        
        const response = await apiCall('/auth/login', 'POST', { username });
        
        currentSessionId = response.session_id;
        currentUser = response.username;
        
        document.getElementById('userWelcome').textContent = `Welcome, ${currentUser}!`;
        
        // Hide login section and show app
        document.getElementById('loginSection').classList.add('hidden');
        showAppSections();
        
        showStatus(response.message, 'success');
        
        // Check if user already has data
        checkDatabaseStatus();
        
    } catch (error) {
        showStatus(`Login failed: ${error.message}`, 'error');
    }
}

async function logout() {
    if (!currentSessionId) return;
    
    try {
        await apiCall(`/auth/logout?session_id=${currentSessionId}`, 'POST');
        
        currentSessionId = null;
        currentUser = null;
        
        // Reset UI
        document.getElementById('loginSection').classList.remove('hidden');
        document.getElementById('appSection').classList.add('hidden');
        document.getElementById('username').value = '';
        document.getElementById('chatHistory').innerHTML = '';
        
        showStatus('Logged out successfully', 'success');
        
    } catch (error) {
        showStatus(`Logout failed: ${error.message}`, 'error');
    }
}

// Database functions
async function checkDatabaseStatus() {
    try {
        const info = await apiCall(`/database/info?session_id=${currentSessionId}`);
        
        if (info.tables && info.tables.length > 0) {
            showDatabaseInfo(info);
            document.getElementById('chatSection').classList.remove('hidden');
        }
    } catch (error) {
        console.log('No existing database found, user needs to set up data');
    }
}

async function createSampleData() {
    if (!currentSessionId) {
        showStatus('Please log in first', 'error');
        return;
    }
    
    try {
        showStatus('Creating sample data...', 'loading');
        
        const response = await apiCall(`/database/sample-data?session_id=${currentSessionId}`, 'POST');
        
        showStatus(response.message, 'success');
        
        // Refresh database info and show chat
        setTimeout(() => {
            checkDatabaseStatus();
        }, 1000);
        
    } catch (error) {
        showStatus(`Failed to create sample data: ${error.message}`, 'error');
    }
}

async function uploadCsv() {
    if (!currentSessionId) {
        showStatus('Please log in first', 'error');
        return;
    }
    
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('Please select a CSV file', 'error');
        return;
    }
    
    if (!file.name.endsWith('.csv')) {
        showStatus('Please select a valid CSV file', 'error');
        return;
    }
    
    try {
        showStatus('Uploading file...', 'loading');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`/database/upload?session_id=${currentSessionId}`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || `HTTP ${response.status}`);
        }
        
        showStatus(result.message, 'success');
        
        // Clear file input
        fileInput.value = '';
        
        // Refresh database info and show chat
        setTimeout(() => {
            checkDatabaseStatus();
        }, 1000);
        
    } catch (error) {
        showStatus(`Upload failed: ${error.message}`, 'error');
    }
}

function showDatabaseInfo(info) {
    const container = document.getElementById('databaseDetails');
    
    if (!info.tables || info.tables.length === 0) {
        container.innerHTML = '<p>No tables found in your database.</p>';
        return;
    }
    
    let html = `<p><strong>Your database contains ${info.tables.length} table(s):</strong></p>`;
    
    for (const table of info.tables) {
        const tableInfo = info.table_info[table];
        html += `
            <div class="database-table">
                <h4>📊 Table: ${table}</h4>
                <div class="table-details">
                    <div class="columns-list">
                        <h5>Columns:</h5>
                        <ul>
                            ${tableInfo.columns.map(col => `<li>${col}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="sample-data">
                        <h5>Sample Data:</h5>
                        <pre>${JSON.stringify(tableInfo.sample_data, null, 2)}</pre>
                    </div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
    document.getElementById('databaseInfo').classList.remove('hidden');
}

// Chat functions
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || !currentSessionId) {
        return;
    }
    
    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="loading-spinner"></span>';
    
    try {
        const response = await apiCall('/chat', 'POST', {
            message: message,
            session_id: currentSessionId
        });
        
        // Add assistant response
        addChatMessage('assistant', response.response, {
            query: response.query_executed,
            results: response.results,
            error: response.error
        });
        
    } catch (error) {
        addChatMessage('assistant', `Sorry, I encountered an error: ${error.message}`, {
            error: error.message
        });
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
        sendBtn.innerHTML = 'Send';
    }
}

function addChatMessage(role, content, meta = null) {
    const chatHistory = document.getElementById('chatHistory');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    let html = `<div class="message-content">${content}</div>`;
    
    if (meta) {
        if (meta.query) {
            html += `<div class="query-details">SQL: ${meta.query}</div>`;
        }
        if (meta.error) {
            html += `<div class="message-meta">Error: ${meta.error}</div>`;
        }
    }
    
    html += `<div class="message-meta">${new Date().toLocaleTimeString()}</div>`;
    
    messageDiv.innerHTML = html;
    chatHistory.appendChild(messageDiv);
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function sendExampleQuery(query) {
    document.getElementById('messageInput').value = query;
    sendMessage();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Focus on username input
    document.getElementById('username').focus();
    
    // Add enter key support for username input
    document.getElementById('username').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            login();
        }
    });
    
    console.log('Multi-User SQL Agent loaded successfully!');
});