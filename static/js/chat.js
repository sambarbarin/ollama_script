// Multi-conversation Ollama Chat Application
class OllamaChatApp {
    constructor() {
        this.socket = null;
        this.currentConversationId = null;
        this.selectedModel = '';
        this.isConnected = false;
        this.isStreaming = false;
        this.currentStreamingMessage = null;
        this.currentStreamingRawText = '';
        this.conversations = [];
        this.contextMenuTarget = null;

        // DOM elements
        this.messagesContainer = null;
        this.messageInput = null;
        this.sendButton = null;
        this.modelSelect = null;
        this.statusIndicator = null;
        this.statusDot = null;
        this.statusText = null;
        this.clearButton = null;
        this.typingIndicator = null;
        this.errorToast = null;
        this.errorMessage = null;

        // Sidebar elements
        this.sidebar = null;
        this.conversationsList = null;
        this.conversationsLoading = null;
        this.conversationsEmpty = null;
        this.newChatBtn = null;
        this.toggleSidebarBtn = null;
        this.toggleSidebarMobile = null;
        this.currentConversationTitle = null;

        // Modal elements
        this.contextMenu = null;
        this.renameModal = null;
        this.renameInput = null;

        // Initialize the app
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp());
        } else {
            this.initializeApp();
        }
    }
    
    initializeApp() {
        console.log('Initializing Ollama Multi-Chat App');

        // Configure markdown renderer
        this.configureMarkdown();

        // Get DOM elements
        this.getDOMElements();

        // Initialize theme
        this.initializeTheme();

        // Setup event listeners
        this.setupEventListeners();

        // Initialize Socket.IO connection
        this.initializeSocket();

        // Load available models
        this.loadModels();

        // Load conversations
        this.loadConversations();

        // Restore sidebar state
        this.restoreSidebarState();

        console.log('Ollama Multi-Chat App initialized');
    }

    initializeTheme() {
        // Load saved theme preference or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // Update icon
        if (this.themeIcon) {
            this.themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    restoreSidebarState() {
        // Restore sidebar collapsed state on desktop
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed && window.innerWidth > 768) {
            this.sidebar.classList.add('collapsed');
            this.toggleSidebarBtn.textContent = '▶';
            this.floatingSidebarToggle.style.display = 'block';
        }
    }

    configureMarkdown() {
        // Configure marked.js with highlight.js integration
        if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.error('Highlight error:', err);
                        }
                    }
                    return hljs.highlightAuto(code).value;
                },
                breaks: true,
                gfm: true
            });
        }
    }

    renderMarkdown(text) {
        if (typeof marked !== 'undefined') {
            return marked.parse(text);
        }
        // Fallback: escape HTML and preserve line breaks
        return this.escapeHtml(text).replace(/\n/g, '<br>');
    }
    
    getDOMElements() {
        // Main elements
        this.messagesContainer = document.getElementById('messages-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.modelSelect = document.getElementById('model-select');
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusDot = this.statusIndicator.querySelector('.status-dot');
        this.statusText = this.statusIndicator.querySelector('.status-text');
        this.clearButton = document.getElementById('clear-chat');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.errorToast = document.getElementById('error-toast');
        this.errorMessage = document.getElementById('error-message');
        this.themeToggle = document.getElementById('theme-toggle');
        this.themeIcon = document.getElementById('theme-icon');

        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarOverlay = document.getElementById('sidebar-overlay');
        this.conversationsList = document.getElementById('conversations-list');
        this.conversationsLoading = document.getElementById('conversations-loading');
        this.conversationsEmpty = document.getElementById('conversations-empty');
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
        this.toggleSidebarMobile = document.getElementById('toggle-sidebar-mobile');
        this.floatingSidebarToggle = document.getElementById('floating-sidebar-toggle');
        this.currentConversationTitle = document.getElementById('current-conversation-title');

        // Modal elements
        this.contextMenu = document.getElementById('conversation-context-menu');
        this.renameModal = document.getElementById('rename-modal-overlay');
        this.renameInput = document.getElementById('rename-input');
    }
    
    setupEventListeners() {
        // Send button and input
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => this.handleInputKeydown(e));
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());

        // Model selection
        this.modelSelect.addEventListener('change', (e) => {
            this.selectedModel = e.target.value;
            console.log('Model selected:', this.selectedModel);
        });

        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());

        // Clear chat
        this.clearButton.addEventListener('click', () => this.clearCurrentConversation());

        // Sidebar controls
        this.newChatBtn.addEventListener('click', () => this.createNewConversation());
        this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
        this.toggleSidebarMobile.addEventListener('click', () => this.toggleSidebarMobile());
        this.floatingSidebarToggle.addEventListener('click', () => this.toggleSidebar());
        this.sidebarOverlay.addEventListener('click', () => this.closeSidebarMobile());

        // Context menu
        document.addEventListener('click', (e) => this.hideContextMenu());
        document.getElementById('rename-conversation').addEventListener('click', () => this.showRenameModal());
        document.getElementById('delete-conversation').addEventListener('click', () => this.deleteConversation());
        
        // Rename modal
        document.getElementById('rename-modal-close').addEventListener('click', () => this.hideRenameModal());
        document.getElementById('rename-cancel').addEventListener('click', () => this.hideRenameModal());
        document.getElementById('rename-confirm').addEventListener('click', () => this.confirmRename());
        this.renameInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.confirmRename();
            if (e.key === 'Escape') this.hideRenameModal();
        });
        
        // Modal overlay clicks
        this.renameModal.addEventListener('click', (e) => {
            if (e.target === this.renameModal) this.hideRenameModal();
        });

        // Window resize handler
        window.addEventListener('resize', () => this.handleWindowResize());
    }

    handleWindowResize() {
        const isCollapsed = this.sidebar.classList.contains('collapsed');

        // Hide floating button on mobile, show on desktop if sidebar is collapsed
        if (window.innerWidth <= 768) {
            this.floatingSidebarToggle.style.display = 'none';
        } else if (isCollapsed) {
            this.floatingSidebarToggle.style.display = 'block';
        }
    }
    
    initializeSocket() {
        this.socket = io();
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.isConnected = true;
            this.updateStatus('connected', 'Connected');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.isConnected = false;
            this.updateStatus('error', 'Disconnected');
        });
        
        // Chat events
        this.socket.on('message_received', (data) => {
            this.addMessage(data.role, data.content);
        });
        
        this.socket.on('response_start', (data) => {
            if (data.conversation_id === this.currentConversationId) {
                this.isStreaming = true;
                this.showTypingIndicator();
                this.currentStreamingRawText = '';
                this.currentStreamingMessage = this.addMessage('assistant', '', true);
            }
        });
        
        this.socket.on('response_chunk', (data) => {
            if (data.conversation_id === this.currentConversationId && this.currentStreamingMessage) {
                this.appendToStreamingMessage(data.chunk);
            }
        });
        
        this.socket.on('response_complete', (data) => {
            if (data.conversation_id === this.currentConversationId) {
                this.isStreaming = false;
                this.hideTypingIndicator();
                this.currentStreamingMessage = null;
                this.currentStreamingRawText = '';
                this.scrollToBottom();

                // Add copy button to completed message
                this.addCopyButtonToMessage(this.messagesContainer.lastElementChild);

                // Refresh conversations list to update timestamps
                this.loadConversations();
            }
        });
        
        this.socket.on('conversation_loaded', (data) => {
            this.displayConversation(data);
        });
        
        this.socket.on('conversation_cleared', (data) => {
            if (data.conversation_id === this.currentConversationId) {
                this.clearMessages();
                this.loadConversations();
            }
        });
        
        this.socket.on('conversation_title_updated', (data) => {
            if (data.conversation_id === this.currentConversationId) {
                this.currentConversationTitle.textContent = data.title;
            }
            this.loadConversations();
        });
        
        this.socket.on('error', (data) => {
            console.error('Chat error:', data.message);
            this.showError(data.message);
            this.isStreaming = false;
            this.hideTypingIndicator();
        });
        
        this.socket.on('status', (data) => {
            console.log('Status update:', data.message);
        });
    }
    
    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            
            if (data.success && data.models.length > 0) {
                this.populateModelSelector(data.models);
                this.selectedModel = data.models[0];
            } else {
                this.showError(data.error || 'No models available');
                this.modelSelect.innerHTML = '<option value="">No models available</option>';
            }
        } catch (error) {
            console.error('Error loading models:', error);
            this.showError('Failed to load models. Please check if Ollama is running.');
            this.modelSelect.innerHTML = '<option value="">Error loading models</option>';
        }
    }
    
    populateModelSelector(models) {
        this.modelSelect.innerHTML = '';
        
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            this.modelSelect.appendChild(option);
        });
        
        if (models.length > 0) {
            this.modelSelect.value = models[0];
            this.selectedModel = models[0];
        }
    }
    
    async loadConversations() {
        try {
            this.showConversationsLoading();
            
            const response = await fetch('/api/conversations');
            const data = await response.json();
            
            if (data.success) {
                this.conversations = data.conversations;
                this.displayConversationsList();
                
                // If no current conversation and we have conversations, select the first one
                if (!this.currentConversationId && this.conversations.length > 0) {
                    this.selectConversation(this.conversations[0].id);
                }
            } else {
                this.showError(data.error || 'Failed to load conversations');
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.showError('Failed to load conversations');
        } finally {
            this.hideConversationsLoading();
        }
    }
    
    displayConversationsList() {
        // Clear existing conversations
        const existingItems = this.conversationsList.querySelectorAll('.conversation-item');
        existingItems.forEach(item => item.remove());
        
        if (this.conversations.length === 0) {
            this.conversationsEmpty.style.display = 'flex';
            return;
        }
        
        this.conversationsEmpty.style.display = 'none';
        
        this.conversations.forEach(conversation => {
            const item = this.createConversationItem(conversation);
            this.conversationsList.appendChild(item);
        });
    }
    
    createConversationItem(conversation) {
        const item = document.createElement('div');
        item.className = `conversation-item ${conversation.id === this.currentConversationId ? 'active' : ''}`;
        item.dataset.conversationId = conversation.id;
        
        const timeAgo = this.formatTimeAgo(conversation.updated_at);
        
        item.innerHTML = `
            <div class="conversation-title">${this.escapeHtml(conversation.title)}</div>
            <div class="conversation-meta">
                <span>${timeAgo}</span>
                <span>${conversation.message_count || 0} messages</span>
            </div>
            <div class="conversation-actions">
                <button class="conversation-menu-btn" title="More options">⋯</button>
            </div>
        `;
        
        // Add event listeners
        item.addEventListener('click', (e) => {
            if (!e.target.classList.contains('conversation-menu-btn')) {
                this.selectConversation(conversation.id);
            }
        });
        
        const menuBtn = item.querySelector('.conversation-menu-btn');
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showContextMenu(e, conversation.id);
        });
        
        return item;
    }
    
    async selectConversation(conversationId) {
        if (conversationId === this.currentConversationId) return;

        this.currentConversationId = conversationId;

        // Update UI
        this.updateActiveConversation();
        this.clearButton.disabled = false;

        // Load conversation messages
        this.socket.emit('load_conversation', { conversation_id: conversationId });

        // Hide sidebar on mobile after selection
        this.closeSidebarMobile();
    }
    
    updateActiveConversation() {
        // Update active class
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.toggle('active', item.dataset.conversationId == this.currentConversationId);
        });
        
        // Update title
        const activeConversation = this.conversations.find(c => c.id === this.currentConversationId);
        if (activeConversation) {
            this.currentConversationTitle.textContent = activeConversation.title;
        }
    }
    
    displayConversation(data) {
        this.clearMessages();
        
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(message => {
                const messageEl = this.addMessage(message.role, message.content);
                if (message.role === 'assistant') {
                    this.addCopyButtonToMessage(messageEl);
                }
            });
            this.scrollToBottom();
        } else {
            this.showWelcomeMessage();
        }
    }
    
    async createNewConversation() {
        try {
            const response = await fetch('/api/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: 'New Chat',
                    model: this.selectedModel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.loadConversations();
                this.selectConversation(data.conversation.id);
            } else {
                this.showError(data.error || 'Failed to create conversation');
            }
        } catch (error) {
            console.error('Error creating conversation:', error);
            this.showError('Failed to create conversation');
        }
    }
    
    async clearCurrentConversation() {
        if (!this.currentConversationId) return;
        
        if (confirm('Are you sure you want to clear this conversation?')) {
            this.socket.emit('clear_conversation', { 
                conversation_id: this.currentConversationId 
            });
        }
    }
    
    handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    handleInputChange() {
        const hasText = this.messageInput.value.trim().length > 0;
        const canSend = hasText && !this.isStreaming && this.selectedModel && this.currentConversationId;
        this.sendButton.disabled = !canSend;
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        const scrollHeight = this.messageInput.scrollHeight;
        const maxHeight = 120;
        this.messageInput.style.height = Math.min(scrollHeight, maxHeight) + 'px';
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isStreaming || !this.selectedModel) {
            return;
        }
        
        if (!this.currentConversationId) {
            this.showError('Please select or create a conversation first.');
            return;
        }
        
        if (!this.isConnected) {
            this.showError('Not connected to server. Please refresh the page.');
            return;
        }
        
        // Clear input and hide welcome message
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.handleInputChange();
        this.hideWelcomeMessage();
        
        // Send message via Socket.IO
        this.socket.emit('send_message', {
            conversation_id: this.currentConversationId,
            model: this.selectedModel,
            message: message
        });
        
        console.log('Message sent:', { 
            conversation_id: this.currentConversationId,
            model: this.selectedModel, 
            message 
        });
    }
    
    addMessage(role, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? 'You' : 'AI';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';

        // Store raw content for copying
        textDiv.dataset.rawContent = content;

        // Render markdown for assistant messages, plain text for user
        if (role === 'assistant') {
            textDiv.innerHTML = this.renderMarkdown(content);
            // Apply syntax highlighting to code blocks
            this.highlightCodeBlocks(textDiv);
        } else {
            textDiv.textContent = content;
        }

        contentDiv.appendChild(textDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        return isStreaming ? textDiv : messageDiv;
    }

    highlightCodeBlocks(element) {
        if (typeof hljs !== 'undefined') {
            const codeBlocks = element.querySelectorAll('pre code');
            codeBlocks.forEach((block) => {
                // Add copy button to code blocks
                this.addCopyButtonToCodeBlock(block);
                // Highlight if not already highlighted
                if (!block.classList.contains('hljs')) {
                    hljs.highlightElement(block);
                }
            });
        }
    }

    addCopyButtonToCodeBlock(codeBlock) {
        const pre = codeBlock.parentElement;
        if (pre && pre.tagName === 'PRE' && !pre.querySelector('.code-copy-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'code-copy-btn';
            copyBtn.innerHTML = '📋';
            copyBtn.title = 'Copy code';
            copyBtn.onclick = (e) => {
                e.stopPropagation();
                const code = codeBlock.textContent;
                navigator.clipboard.writeText(code).then(() => {
                    copyBtn.innerHTML = '✓';
                    copyBtn.classList.add('copied');
                    setTimeout(() => {
                        copyBtn.innerHTML = '📋';
                        copyBtn.classList.remove('copied');
                    }, 2000);
                });
            };
            pre.style.position = 'relative';
            pre.appendChild(copyBtn);
        }
    }
    
    addCopyButtonToMessage(messageElement) {
        if (!messageElement || messageElement.querySelector('.message-actions')) return;

        const messageContent = messageElement.querySelector('.message-content');
        const messageText = messageElement.querySelector('.message-text');

        if (messageContent && messageText) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'message-actions';

            const copyButton = document.createElement('button');
            copyButton.className = 'message-action';
            copyButton.textContent = '📋 Copy';
            copyButton.title = 'Copy message';
            copyButton.onclick = () => {
                // Copy raw content if available, otherwise fall back to text content
                const rawContent = messageText.dataset.rawContent || messageText.textContent;
                this.copyMessage(rawContent, copyButton);
            };

            actionsDiv.appendChild(copyButton);
            messageContent.appendChild(actionsDiv);
        }
    }
    
    appendToStreamingMessage(chunk) {
        if (this.currentStreamingMessage) {
            this.currentStreamingRawText += chunk;
            // Store raw content for copying
            this.currentStreamingMessage.dataset.rawContent = this.currentStreamingRawText;
            // Render markdown
            this.currentStreamingMessage.innerHTML = this.renderMarkdown(this.currentStreamingRawText);
            // Highlight code blocks
            this.highlightCodeBlocks(this.currentStreamingMessage);
            this.scrollToBottom();
        }
    }
    
    copyMessage(text, button = null) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('Message copied to clipboard');
            if (button) {
                const originalText = button.textContent;
                button.textContent = '✓ Copied';
                button.classList.add('copied');
                setTimeout(() => {
                    button.textContent = originalText;
                    button.classList.remove('copied');
                }, 2000);
            }
        }).catch(err => {
            console.error('Failed to copy message:', err);
            if (button) {
                button.textContent = '✗ Failed';
                setTimeout(() => {
                    button.textContent = '📋 Copy';
                }, 2000);
            }
        });
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    showWelcomeMessage() {
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }
    }
    
    hideWelcomeMessage() {
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
    }
    
    clearMessages() {
        const messages = this.messagesContainer.querySelectorAll('.message');
        messages.forEach(message => message.remove());
        this.hideTypingIndicator();
        this.showWelcomeMessage();
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('collapsed');
        const isCollapsed = this.sidebar.classList.contains('collapsed');
        this.toggleSidebarBtn.textContent = isCollapsed ? '▶' : '◀';
        localStorage.setItem('sidebarCollapsed', isCollapsed);

        // Show/hide floating toggle button (desktop only)
        if (window.innerWidth > 768) {
            this.floatingSidebarToggle.style.display = isCollapsed ? 'block' : 'none';
        }
    }

    toggleSidebarMobile() {
        // Toggle sidebar visibility on mobile
        const isShowing = this.sidebar.classList.toggle('show');
        if (isShowing) {
            this.sidebarOverlay.classList.add('show');
        } else {
            this.sidebarOverlay.classList.remove('show');
        }
    }

    closeSidebarMobile() {
        // Close sidebar on mobile (used after selecting conversation or clicking overlay)
        this.sidebar.classList.remove('show');
        this.sidebarOverlay.classList.remove('show');
    }
    
    showConversationsLoading() {
        this.conversationsLoading.style.display = 'flex';
        this.conversationsEmpty.style.display = 'none';
    }
    
    hideConversationsLoading() {
        this.conversationsLoading.style.display = 'none';
    }
    
    showContextMenu(event, conversationId) {
        this.contextMenuTarget = conversationId;
        
        const rect = event.target.getBoundingClientRect();
        this.contextMenu.style.left = rect.left + 'px';
        this.contextMenu.style.top = rect.bottom + 'px';
        this.contextMenu.style.display = 'block';
    }
    
    hideContextMenu() {
        this.contextMenu.style.display = 'none';
        this.contextMenuTarget = null;
    }
    
    showRenameModal() {
        if (!this.contextMenuTarget) return;
        
        const conversation = this.conversations.find(c => c.id === this.contextMenuTarget);
        if (conversation) {
            this.renameInput.value = conversation.title;
            this.renameModal.style.display = 'flex';
            this.renameInput.focus();
            this.renameInput.select();
        }
        this.hideContextMenu();
    }
    
    hideRenameModal() {
        this.renameModal.style.display = 'none';
        this.contextMenuTarget = null;
    }
    
    async confirmRename() {
        if (!this.contextMenuTarget) return;
        
        const newTitle = this.renameInput.value.trim();
        if (!newTitle) {
            this.showError('Please enter a valid title');
            return;
        }
        
        try {
            const response = await fetch(`/api/conversations/${this.contextMenuTarget}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.loadConversations();
                if (this.contextMenuTarget === this.currentConversationId) {
                    this.currentConversationTitle.textContent = newTitle;
                }
                this.hideRenameModal();
            } else {
                this.showError(data.error || 'Failed to rename conversation');
            }
        } catch (error) {
            console.error('Error renaming conversation:', error);
            this.showError('Failed to rename conversation');
        }
    }
    
    async deleteConversation() {
        if (!this.contextMenuTarget) return;
        
        if (confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
            try {
                const response = await fetch(`/api/conversations/${this.contextMenuTarget}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // If we're deleting the current conversation, clear it
                    if (this.contextMenuTarget === this.currentConversationId) {
                        this.currentConversationId = null;
                        this.clearMessages();
                        this.currentConversationTitle.textContent = 'Ollama Chat';
                        this.clearButton.disabled = true;
                    }
                    
                    await this.loadConversations();
                } else {
                    this.showError(data.error || 'Failed to delete conversation');
                }
            } catch (error) {
                console.error('Error deleting conversation:', error);
                this.showError('Failed to delete conversation');
            }
        }
        
        this.hideContextMenu();
    }
    
    updateStatus(type, text) {
        this.statusDot.className = `status-dot ${type}`;
        this.statusText.textContent = text;
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorToast.classList.add('show');
        
        setTimeout(() => {
            this.hideToast();
        }, 5000);
    }
    
    hideToast() {
        this.errorToast.classList.remove('show');
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    formatTimeAgo(timestamp) {
        const now = new Date();
        const date = new Date(timestamp);
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        
        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) return `${diffInHours}h ago`;
        
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays < 7) return `${diffInDays}d ago`;
        
        return date.toLocaleDateString();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global function for toast close button
function hideToast() {
    const toast = document.getElementById('error-toast');
    if (toast) {
        toast.classList.remove('show');
    }
}

// Initialize the app when the script loads
const chatApp = new OllamaChatApp();

// Export for potential use in other scripts
window.OllamaChatApp = OllamaChatApp;