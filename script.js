// TIE AI Tutor Frontend JavaScript
class TIEAIApp {
    constructor() {
        this.currentTheme = 'light';
        this.currentLanguage = 'en';
        this.messages = [];
        this.currentSubject = 'all';
        this.userType = 'student';
        this.userForm = 'form1';
        this.isTyping = false;
        
        this.initializeApp();
    }
    
    initializeApp() {
        this.cacheDOM();
        this.bindEvents();
        this.loadUserPreferences();
        this.showLoginModal();
    }
    
    cacheDOM() {
        // Theme elements
        this.themeToggle = document.getElementById('themeToggle');
        this.themeIcon = this.themeToggle.querySelector('i');
        this.themeText = this.themeToggle.querySelector('.theme-text');
        
        // Chat elements
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.chatContainer = document.getElementById('chatContainer');
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        // Subject selection
        this.subjectItems = document.querySelectorAll('.subject-item');
        
        // Language toggle
        this.languageOptions = document.querySelectorAll('.lang-option');
        
        // Quick question chips
        this.questionChips = document.querySelectorAll('.chip');
        
        // Modals
        this.sourceModal = document.getElementById('sourceModal');
        this.loginModal = document.getElementById('loginModal');
        this.closeModalBtn = document.getElementById('closeModalBtn');
        this.loginSubmitBtn = document.getElementById('loginSubmitBtn');
        
        // User info
        this.userRoleElement = document.querySelector('.user-role');
        this.logoutBtn = document.getElementById('logoutBtn');
        
        // Login form
        this.userTypeSelect = document.getElementById('userType');
        this.userFormSelect = document.getElementById('userForm');
        this.usernameInput = document.getElementById('username');
    }
    
    bindEvents() {
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Message sending
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = (this.messageInput.scrollHeight) + 'px';
        });
        
        // Clear chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // New chat
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        // Subject selection
        this.subjectItems.forEach(item => {
            item.addEventListener('click', (e) => this.selectSubject(e));
        });
        
        // Language toggle
        this.languageOptions.forEach(option => {
            option.addEventListener('click', (e) => this.selectLanguage(e));
        });
        
        // Quick questions
        this.questionChips.forEach(chip => {
            chip.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                this.messageInput.value = question;
                this.sendMessage();
            });
        });
        
        // Modal controls
        this.closeModalBtn?.addEventListener('click', () => this.hideModal(this.sourceModal));
        this.loginSubmitBtn.addEventListener('click', () => this.handleLogin());
        this.logoutBtn.addEventListener('click', () => this.handleLogout());
        
        // Close modal on outside click
        document.addEventListener('click', (e) => {
            if (e.target === this.sourceModal) {
                this.hideModal(this.sourceModal);
            }
            if (e.target === this.loginModal) {
                this.hideModal(this.loginModal);
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.messageInput.focus();
            }
            if (e.key === 'Escape') {
                this.hideModal(this.sourceModal);
            }
        });
    }
    
    loadUserPreferences() {
        const savedTheme = localStorage.getItem('tieTheme') || 'light';
        const savedLanguage = localStorage.getItem('tieLanguage') || 'en';
        const savedUserType = localStorage.getItem('tieUserType');
        const savedUserForm = localStorage.getItem('tieUserForm');
        
        if (savedTheme) this.setTheme(savedTheme);
        if (savedLanguage) this.setLanguage(savedLanguage);
        if (savedUserType) this.userType = savedUserType;
        if (savedUserForm) this.userForm = savedUserForm;
    }
    
    showLoginModal() {
        this.showModal(this.loginModal);
    }
    
    showModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    hideModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    handleLogin() {
        this.userType = this.userTypeSelect.value;
        this.userForm = this.userFormSelect.value;
        const username = this.usernameInput.value || 'User';
        
        // Save user preferences
        localStorage.setItem('tieUserType', this.userType);
        localStorage.setItem('tieUserForm', this.userForm);
        localStorage.setItem('tieUsername', username);
        
        // Update UI
        this.userRoleElement.textContent = this.userType.charAt(0).toUpperCase() + this.userType.slice(1);
        
        // Hide login modal and show chat
        this.hideModal(this.loginModal);
        this.showChatInterface();
        
        // Show welcome message
        this.showWelcomeMessage();
    }
    
    handleLogout() {
        localStorage.removeItem('tieUserType');
        localStorage.removeItem('tieUserForm');
        localStorage.removeItem('tieUsername');
        this.showLoginModal();
    }
    
    showChatInterface() {
        this.welcomeScreen.style.display = 'none';
        this.chatContainer.style.display = 'flex';
        this.messageInput.focus();
    }
    
    showWelcomeMessage() {
        const welcomeMessage = {
            sender: 'ai',
            content: `Karibu ${this.userType === 'teacher' ? 'Mwalimu' : 'Mwanafunzi'}! I am your TIE AI Tutor, ready to help you with Tanzanian curriculum questions. Ask me anything about subjects from Form 1 to 6.`,
            timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            source: {
                book: 'TIE AI Tutor System',
                subject: 'Introduction',
                topic: 'Welcome',
                page: '1'
            }
        };
        
        this.addMessageToChat(welcomeMessage);
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(this.currentTheme);
        localStorage.setItem('tieTheme', this.currentTheme);
    }
    
    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update toggle button
        if (theme === 'dark') {
            this.themeIcon.className = 'fas fa-sun';
            this.themeText.textContent = 'Light Mode';
        } else {
            this.themeIcon.className = 'fas fa-moon';
            this.themeText.textContent = 'Dark Mode';
        }
    }
    
    selectLanguage(e) {
        const language = e.target.dataset.lang;
        this.setLanguage(language);
        localStorage.setItem('tieLanguage', language);
    }
    
    setLanguage(lang) {
        this.currentLanguage = lang;
        this.languageOptions.forEach(option => {
            option.classList.toggle('active', option.dataset.lang === lang);
        });
    }
    
    selectSubject(e) {
        const subject = e.currentTarget.dataset.subject;
        
        // Update active state
        this.subjectItems.forEach(item => {
            item.classList.toggle('active', item.dataset.subject === subject);
        });
        
        this.currentSubject = subject;
        
        // Update current subject display
        const subjectNames = {
            'all': 'All Subjects',
            'physics': 'Physics',
            'chemistry': 'Chemistry',
            'biology': 'Biology',
            'mathematics': 'Mathematics',
            'kiswahili': 'Kiswahili',
            'english': 'English',
            'geography': 'Geography',
            'history': 'History'
        };
        
        const subjectIcon = e.currentTarget.querySelector('i').className;
        const subjectDisplay = document.querySelector('.current-subject');
        subjectDisplay.innerHTML = `<i class="${subjectIcon}"></i><span>${subjectNames[subject]} - ${this.userForm.replace('form', 'Form ')}</span>`;
    }
    
    async sendMessage() {
        const content = this.messageInput.value.trim();
        if (!content) return;
        
        // Create user message
        const userMessage = {
            sender: 'user',
            content: content,
            timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        };
        
        this.addMessageToChat(userMessage);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to backend
            const response = await this.sendToBackend(content);
            
            // Add AI response
            const aiMessage = {
                sender: 'ai',
                content: response.answer,
                timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                source: response.source
            };
            
            this.addMessageToChat(aiMessage);
            
        } catch (error) {
            console.error('Error:', error);
            
            // Show error message
            const errorMessage = {
                sender: 'ai',
                content: 'Sorry, I encountered an error. Please check your connection and try again.',
                timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                source: {
                    book: 'System Error',
                    subject: 'Technical',
                    topic: 'Connection',
                    page: 'N/A'
                }
            };
            
            this.addMessageToChat(errorMessage);
        } finally {
            this.hideTypingIndicator();
        }
    }
    
    async sendToBackend(question) {
        // This is a mock response - in production, this would connect to Flask backend
        // Simulating API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock response based on question
        const mockResponses = {
            'physics': {
                answer: "Newton's First Law of Motion states that an object at rest stays at rest and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced force.\n\nA SIMPLE EXAMPLE: If you slide a book on a table, it eventually stops because of friction (an unbalanced force). In space, where there's no friction, it would keep moving forever.",
                source: {
                    book: "Physics for Secondary Schools Form 2",
                    subject: "Physics",
                    topic: "Force and Motion",
                    page: "45-48",
                    form: "Form 2"
                }
            },
            'biology': {
                answer: "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water. Photosynthesis in plants generally involves the green pigment chlorophyll and generates oxygen as a byproduct.\n\nA SIMPLE EXAMPLE: A tree uses sunlight, water from the soil, and carbon dioxide from the air to make food (glucose) and release oxygen.",
                source: {
                    book: "Biology for Secondary Schools Form 1",
                    subject: "Biology",
                    topic: "Nutrition in Plants",
                    page: "78-82",
                    form: "Form 1"
                }
            },
            'chemistry': {
                answer: "Chemical bonding refers to the attractive force that holds atoms together in molecules and compounds. The three main types are ionic, covalent, and metallic bonds.\n\nA SIMPLE EXAMPLE: Table salt (NaCl) is held together by ionic bonds where sodium donates an electron to chlorine.",
                source: {
                    book: "Chemistry for Secondary Schools Form 2",
                    subject: "Chemistry",
                    topic: "Chemical Bonding",
                    page: "112-118",
                    form: "Form 2"
                }
            },
            'kiswahili': {
                answer: "Kanuni ya kwanza ya Newton inasema: Kitu kilichopo katika hali ya kupumzika kitabaki katika hali hiyo, na kitu kinachosogea kwa kasi ya mara kwa mara katika mstari wa moja kwa moja kitabaki kusogea hivyo, isipokuwa kitakaposhinikizwa na nguvu isiyo na usawa kutoka nje.\n\nMFANO RAHISI: Ukiteleza kitabu juu ya meza, kitasitamisha mwishowe kwa sababu ya msuguano (nguvu isiyo na usawa).",
                source: {
                    book: "Sayansi ya Fizikia Kidato cha 2",
                    subject: "Fizikia",
                    topic: "Nguvu na Mwendo",
                    page: "45-48",
                    form: "Kidato cha 2"
                }
            }
        };
        
        // Determine which mock response to use
        let responseKey = 'physics';
        if (question.toLowerCase().includes('photosynthesis')) responseKey = 'biology';
        if (question.toLowerCase().includes('chemical bonding')) responseKey = 'chemistry';
        if (question.toLowerCase().includes('kanuni') || question.toLowerCase().includes('newton')) responseKey = 'kiswahili';
        
        return mockResponses[responseKey];
    }
    
    addMessageToChat(message) {
        this.messages.push(message);
        
        const messageElement = this.createMessageElement(message);
        this.messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        
        // Update message count
        this.updateMessageCount();
    }
    
    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.sender}`;
        
        const isAI = message.sender === 'ai';
        const avatar = isAI ? 'TIE' : 'You';
        const avatarBg = isAI ? '#3b82f6' : '#ffffff';
        const avatarColor = isAI ? '#ffffff' : '#3b82f6';
        
        div.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <div class="message-avatar" style="background-color: ${avatarBg}; color: ${avatarColor}">
                        ${avatar}
                    </div>
                    <span class="message-sender">${isAI ? 'TIE AI Tutor' : 'You'}</span>
                    <span class="message-time">${message.timestamp}</span>
                </div>
                <div class="message-text">${this.formatMessageText(message.content)}</div>
                ${message.source ? this.createSourceBadge(message.source) : ''}
            </div>
        `;
        
        // Add click event to source badge
        if (message.source) {
            const sourceHeader = div.querySelector('.source-header');
            sourceHeader.addEventListener('click', () => this.showSourceDetails(message.source));
        }
        
        return div;
    }
    
    formatMessageText(text) {
        // Convert newlines to <br> and handle markdown-like formatting
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    createSourceBadge(source) {
        return `
            <div class="source-badge">
                <div class="source-header">
                    <div class="source-title">
                        <i class="fas fa-book"></i>
                        Source Information
                    </div>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="source-details">
                    <div class="source-item">
                        <span class="source-label">Book:</span>
                        <span class="source-value">${source.book}</span>
                    </div>
                    <div class="source-item">
                        <span class="source-label">Page:</span>
                        <span class="source-value">${source.page}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    showSourceDetails(source) {
        document.getElementById('sourceBook').textContent = source.book;
        document.getElementById('sourceSubject').textContent = source.subject;
        document.getElementById('sourceTopic').textContent = source.topic;
        document.getElementById('sourcePage').textContent = source.page;
        document.getElementById('sourceForm').textContent = source.form;
        
        this.showModal(this.sourceModal);
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }
    
    updateMessageCount() {
        const count = this.messages.length;
        const countElement = document.querySelector('.message-count');
        countElement.textContent = `${count} Message${count !== 1 ? 's' : ''}`;
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear all messages?')) {
            this.messages = [];
            this.messagesContainer.innerHTML = '';
            this.updateMessageCount();
        }
    }
    
    startNewChat() {
        this.clearChat();
        this.showWelcomeMessage();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TIEAIApp();
});