// app/static/src/js/modules/toast.js
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container position-fixed top-0 end-0 p-3';
            this.container.style.zIndex = '9999';
            document.body.appendChild(this.container);
        }

        // Listen for HTMX events
        this.setupHTMXListeners();
    }

    show(message, type = 'info', duration = 5000) {
        const toastId = 'toast-' + Date.now();
        const toastHTML = this.createToastHTML(toastId, message, type);
        
        this.container.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { delay: duration });
        
        // Remove after hide
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
        
        toast.show();
    }

    createToastHTML(id, message, type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill', 
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        const bgColors = {
            success: 'text-bg-success',
            error: 'text-bg-danger',
            warning: 'text-bg-warning',
            info: 'text-bg-primary'
        };

        return `
            <div id="${id}" class="toast align-items-center ${bgColors[type] || ''} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi ${icons[type]} me-2"></i>
                        ${this.escapeHtml(message)}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setupHTMXListeners() {
        // Custom HTMX event for toasts
        document.body.addEventListener('showToast', (event) => {
            const { message, type, duration } = event.detail;
            this.show(message, type, duration);
        });

        // Handle HX-Trigger header
        document.body.addEventListener('htmx:afterRequest', (event) => {
            const trigger = event.detail.xhr.getResponseHeader('HX-Trigger');
            if (trigger) {
                try {
                    const data = JSON.parse(trigger);
                    if (data.showToast) {
                        this.show(data.showToast.message, data.showToast.type);
                    }
                } catch (e) {
                    // Not JSON, ignore
                }
            }
        });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.toastManager = new ToastManager();
});

// Global helper
window.showToast = (message, type, duration) => {
    if (window.toastManager) {
        window.toastManager.show(message, type, duration);
    }
};
