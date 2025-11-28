// API Configuration
const API_BASE_URL = window.location.origin;

// Chat history storage
let chatMessages = [];

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeChatInterface();
    initializeFileUpload();
    checkAPIStatus();
    loadBooks();
    
    // Set API URL in sidebar
    document.getElementById('api-url').textContent = API_BASE_URL;
    
    // Refresh API status every 30 seconds
    setInterval(checkAPIStatus, 30000);
});

// ==================== TAB MANAGEMENT ====================
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update button states
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load data when switching to books tab
    if (tabName === 'books') {
        loadBooks();
    }
}

// ==================== CHAT INTERFACE ====================
function initializeChatInterface() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    // Send message on button click
    sendButton.addEventListener('click', sendMessage);
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const query = input.value.trim();
    
    if (!query) return;
    
    // Clear input and disable button
    input.value = '';
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    // Add user message to chat
    addMessageToChat('user', query);
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
            timeout: 30000
        });
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        if (response.ok) {
            const data = await response.json();
            const answer = data.answer || 'No response generated.';
            const fileNames = data.file_names || [];
            const numResults = data.num_results || 0;
            
            // Add assistant response
            addMessageToChat('assistant', answer, fileNames);
        } else {
            addMessageToChat('assistant', `Error: API returned status ${response.status}`, []);
        }
    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessageToChat('assistant', `Error: ${error.message}`, []);
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
        input.focus();
    }
}

function addMessageToChat(role, content, sources = null) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message message-${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    // Add sources if available (for assistant messages)
    if (role === 'assistant' && sources && sources.length > 0) {
        const sourcesExpander = document.createElement('details');
        sourcesExpander.className = 'sources-expander';
        
        const summary = document.createElement('summary');
        summary.textContent = '📄 Sources';
        
        const sourcesContent = document.createElement('div');
        sourcesContent.className = 'sources-content';
        
        const sourcesList = document.createElement('ul');
        sources.forEach(source => {
            const li = document.createElement('li');
            li.textContent = `- ${source}`;
            sourcesList.appendChild(li);
        });
        
        sourcesContent.appendChild(sourcesList);
        sourcesExpander.appendChild(summary);
        sourcesExpander.appendChild(sourcesContent);
        contentDiv.appendChild(sourcesExpander);
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Store in chat history
    chatMessages.push({ role, content, sources });
}

function addLoadingMessage() {
    const chatContainer = document.getElementById('chat-container');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message message-assistant';
    loadingDiv.id = `loading-${Date.now()}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Searching and generating response...</p></div>';
    
    loadingDiv.appendChild(avatar);
    loadingDiv.appendChild(contentDiv);
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return loadingDiv.id;
}

function removeLoadingMessage(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// ==================== BOOKS TAB ====================
async function loadBooks() {
    const loadingSpinner = document.getElementById('books-loading');
    const booksList = document.getElementById('books-list');
    
    loadingSpinner.style.display = 'flex';
    booksList.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/status`, {
            timeout: 10000
        });
        
        if (response.ok) {
            const data = await response.json();
            const embeddedFiles = data.embedded_files || [];
            const totalFiles = data.total_files || 0;
            
            // Update statistics
            document.getElementById('total-books').textContent = totalFiles;
            document.getElementById('status').textContent = 'Running';
            document.getElementById('last-updated').textContent = 'Now';
            
            // Display books
            if (embeddedFiles.length > 0) {
                booksList.innerHTML = `<h3>Embedded Books (${embeddedFiles.length})</h3>`;
                
                embeddedFiles.forEach((fileName, index) => {
                    const bookItem = document.createElement('div');
                    bookItem.className = 'book-item';
                    
                    const bookName = document.createElement('div');
                    bookName.className = 'book-name';
                    bookName.textContent = `${index + 1}. ${fileName}`;
                    
                    const bookStatus = document.createElement('div');
                    bookStatus.className = 'book-status';
                    bookStatus.textContent = '✓ Embedded';
                    
                    bookItem.appendChild(bookName);
                    bookItem.appendChild(bookStatus);
                    booksList.appendChild(bookItem);
                });
            } else {
                booksList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No books embedded yet. Upload a PDF to get started!</p>
                    </div>
                `;
            }
        } else {
            booksList.innerHTML = `
                <div class="empty-state">
                    <p>Could not fetch book list from API</p>
                </div>
            `;
        }
    } catch (error) {
        booksList.innerHTML = `
            <div class="empty-state">
                <p>Error fetching books: ${error.message}</p>
            </div>
        `;
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

// ==================== FILE UPLOAD ====================
function initializeFileUpload() {
    const fileInput = document.getElementById('pdf-file');
    const uploadButton = document.getElementById('upload-button');
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            displayFileInfo(file);
            uploadButton.disabled = false;
        } else {
            hideFileInfo();
            uploadButton.disabled = true;
        }
    });
    
    uploadButton.addEventListener('click', uploadFile);
}

function displayFileInfo(file) {
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    fileName.textContent = file.name;
    fileSize.textContent = (file.size / 1024).toFixed(2);
    fileInfo.style.display = 'block';
}

function hideFileInfo() {
    document.getElementById('file-info').style.display = 'none';
}

async function uploadFile() {
    const fileInput = document.getElementById('pdf-file');
    const uploadButton = document.getElementById('upload-button');
    const uploadMessage = document.getElementById('upload-message');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    // Disable button and show loading
    uploadButton.disabled = true;
    uploadButton.textContent = `📤 Processing ${file.name}...`;
    uploadMessage.style.display = 'none';
    
    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('pdf_file', file);
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
            timeout: 120000
        });
        
        if (response.ok) {
            const result = await response.json();
            showUploadMessage(`✅ ${file.name} uploaded and processed successfully!`, 'success');
            
            // Reset form
            fileInput.value = '';
            hideFileInfo();
            
            // Refresh books list if on books tab
            const booksTab = document.getElementById('books-tab');
            if (booksTab.classList.contains('active')) {
                loadBooks();
            }
        } else {
            const error = await response.json();
            showUploadMessage(`❌ ${error.message || 'Failed to process PDF'}`, 'error');
        }
    } catch (error) {
        showUploadMessage(`❌ Error uploading file: ${error.message}`, 'error');
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = '📤 Upload and Process';
    }
}

function showUploadMessage(message, type) {
    const uploadMessage = document.getElementById('upload-message');
    uploadMessage.textContent = message;
    uploadMessage.className = `upload-message ${type}`;
    uploadMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            uploadMessage.style.display = 'none';
        }, 5000);
    }
}

// ==================== API STATUS ====================
async function checkAPIStatus() {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('api-status-text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/status`, {
            timeout: 5000
        });
        
        if (response.ok) {
            statusIndicator.classList.add('connected');
            statusIndicator.classList.remove('error');
            statusText.textContent = '✅ Backend Connected';
        } else {
            statusIndicator.classList.add('error');
            statusIndicator.classList.remove('connected');
            statusText.textContent = '⚠️ Backend Error';
        }
    } catch (error) {
        statusIndicator.classList.add('error');
        statusIndicator.classList.remove('connected');
        statusText.textContent = '❌ Backend Offline';
    }
}

// ==================== UTILITY FUNCTIONS ====================
// Timeout wrapper for fetch
const fetchWithTimeout = async (url, options = {}) => {
    const { timeout = 8000 } = options;
    
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
};