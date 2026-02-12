/**
 * Custom Notification System for ContraLog
 * Replaces SweetAlert2 with a premium, enterprise-look notification
 */

const Notifications = {
    container: null,

    init() {
        if (this.container) return;
        this.container = document.createElement('div');
        this.container.id = 'notifications-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);

        const style = document.createElement('style');
        style.textContent = `
            .cl-notification {
                background: white;
                border-left: 4px solid #0a3a5c;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                padding: 16px 20px;
                min-width: 300px;
                max-width: 450px;
                display: flex;
                align-items: center;
                gap: 15px;
                pointer-events: auto;
                animation: slideIn 0.3s ease-out forwards;
                border-radius: 4px;
            }
            .cl-notification.error { border-left-color: #dc2626; }
            .cl-notification.success { border-left-color: #059669; }
            .cl-notification.warning { border-left-color: #d97706; }
            
            .cl-notification-icon {
                font-size: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .cl-notification-content {
                flex: 1;
            }
            
            .cl-notification-title {
                font-weight: 700;
                font-size: 0.9rem;
                margin-bottom: 2px;
                color: #1e293b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .cl-notification-message {
                font-size: 0.85rem;
                color: #64748b;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    },

    show(title, message, type = 'info', duration = 5000) {
        this.init();
        
        const notif = document.createElement('div');
        notif.className = `cl-notification ${type}`;
        
        let icon = 'ℹ️';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '❌';
        if (type === 'warning') icon = '⚠️';
        
        notif.innerHTML = `
            <div class="cl-notification-icon">${icon}</div>
            <div class="cl-notification-content">
                <div class="cl-notification-title">${title}</div>
                <div class="cl-notification-message">${message}</div>
            </div>
        `;
        
        this.container.appendChild(notif);
        
        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => {
                notif.remove();
            }, 300);
        }, duration);
    },

    success(title, message) { this.show(title, message, 'success'); },
    error(title, message) { this.show(title, message, 'error'); },
    warning(title, message) { this.show(title, message, 'warning'); },
    info(title, message) { this.show(title, message, 'info'); }
};

// Global helper for migration from Swal
window.showNotif = (title, text, icon) => {
    if (icon === 'success') Notifications.success(title, text);
    else if (icon === 'error') Notifications.error(title, text);
    else if (icon === 'warning') Notifications.warning(title, text);
    else Notifications.info(title, text);
};
