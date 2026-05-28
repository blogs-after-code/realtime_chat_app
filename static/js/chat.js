// Additional JavaScript for enhanced functionality
class ChatApp {
    constructor() {
        this.currentUserId = null;
        this.selectedUserId = null;
        this.ws = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.startOnlineStatusPolling();
    }
    
    setupEventListeners() {
        document.getElementById('sendBtn')?.addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        document.querySelectorAll('.user-item').forEach(item => {
            item.addEventListener('click', () => this.selectUser(item));
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat/`);
        
        this.ws.onopen = () => console.log('WebSocket connected');
        this.ws.onmessage = (e) => this.handleMessage(JSON.parse(e.data));
        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting...');
            setTimeout(() => this.connectWebSocket(), 1000);
        };
    }
    
    handleMessage(data) {
        if (data.type === 'message') {
            if (data.sender_id === this.selectedUserId) {
                this.addMessage(data.sender, data.content, data.timestamp, false);
            } else {
                this.showNotification(`New message from ${data.sender}`);
                this.updateUnreadBadge(data.sender_id);
            }
        } else if (data.type === 'status') {
            this.updateUserStatus(data.user_id, data.is_online);
        }
    }
    
    sendMessage() {
        const input = document.getElementById('messageInput');
        const content = input.value.trim();
        
        if (content && this.selectedUserId && this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'message',
                content: content,
                receiver_id: this.selectedUserId
            }));
            
            this.addMessage('You', content, new Date().toISOString(), true);
            input.value = '';
        }
    }
    
    addMessage(sender, content, timestamp, isMine) {
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isMine ? 'mine' : 'theirs'}`;
        
        const time = new Date(timestamp).toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(content)}</div>
                <div class="message-info">
                    <span class="sender">${this.escapeHtml(sender)}</span>
                    <span class="time">${time}</span>
                </div>
            </div>
        `;
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    selectUser(userItem) {
        this.selectedUserId = userItem.dataset.userId;
        const username = userItem.dataset.username;
        
        document.getElementById('chatHeader').innerHTML = `<h3>Chatting with ${username}</h3>`;
        document.querySelector('.message-input-area').style.display = 'flex';
        
        this.loadMessages(this.selectedUserId);
        
        document.querySelectorAll('.user-item').forEach(u => u.classList.remove('selected'));
        userItem.classList.add('selected');
    }
    
    loadMessages(userId) {
        fetch(`/get_messages/${userId}/`)
            .then(response => response.json())
            .then(data => {
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = '';
                data.messages.forEach(msg => {
                    this.addMessage(msg.sender, msg.content, msg.timestamp, msg.is_mine);
                });
            });
    }
    
    updateUserStatus(userId, isOnline) {
        const userItem = document.querySelector(`.user-item[data-user-id="${userId}"]`);
        if (userItem) {
            const statusSpan = userItem.querySelector('.status');
            statusSpan.className = `status ${isOnline ? 'online' : 'offline'}`;
            statusSpan.textContent = isOnline ? 'Online' : 'Offline';
        }
        this.updateOnlineCount();
    }
    
    updateOnlineCount() {
        const onlineCount = document.querySelectorAll('.status.online').length;
        const countElement = document.getElementById('onlineCount');
        if (countElement) countElement.textContent = onlineCount;
    }
    
    updateUnreadBadge(userId) {
        const userItem = document.querySelector(`.user-item[data-user-id="${userId}"]`);
        if (userItem && userId !== this.selectedUserId) {
            let badge = userItem.querySelector('.unread-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'unread-badge';
                userItem.querySelector('.user-details').appendChild(badge);
            }
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
            badge.style.display = 'inline';
        }
    }
    
    showNotification(message) {
        if (Notification.permission === 'granted') {
            new Notification('New Message', { body: message });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission();
        }
        
        // Also show in-page notification
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'in-page-notification';
        notificationDiv.textContent = message;
        notificationDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 12px 20px;
            border-radius: 5px;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        document.body.appendChild(notificationDiv);
        setTimeout(() => notificationDiv.remove(), 3000);
    }
    
    startOnlineStatusPolling() {
        setInterval(() => {
            fetch('/get_online_users/')
                .then(response => response.json())
                .then(data => {
                    document.querySelectorAll('.user-item').forEach(item => {
                        const userId = parseInt(item.dataset.userId);
                        const isOnline = data.online_users.includes(userId);
                        this.updateUserStatus(userId, isOnline);
                    });
                });
        }, 5000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.chat-container')) {
        new ChatApp();
    }
});