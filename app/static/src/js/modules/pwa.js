// app/static/src/js/modules/pwa.js

class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.init();
    }

    init() {
        if ('serviceWorker' in navigator) {
            this.registerServiceWorker();
        }
        this.setupInstallPrompt();
        this.checkIfInstalled();
        this.setupUpdateDetection();
    }

    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/static/sw.js');
            console.log('Service Worker registered:', registration);

            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        this.showUpdateNotification();
                    }
                });
            });
        } catch (error) {
            console.error('Service Worker registration failed:', error);
        }
    }

    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            console.log('App was installed');
            this.hideInstallButton();
            showToast('App wurde erfolgreich installiert!', 'success');
        });
    }

    showInstallButton() {
        const container = document.getElementById('install-button-container');
        const button = document.getElementById('install-button');
        
        if (container && button) {
            container.classList.remove('d-none');
            
            button.addEventListener('click', async () => {
                if (!this.deferredPrompt) return;
                
                this.deferredPrompt.prompt();
                const { outcome } = await this.deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                
                this.deferredPrompt = null;
                this.hideInstallButton();
            });
        }
    }

    hideInstallButton() {
        const container = document.getElementById('install-button-container');
        if (container) {
            container.classList.add('d-none');
        }
    }

    checkIfInstalled() {
        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('App is installed');
            document.body.classList.add('pwa-installed');
        }

        if (window.navigator.standalone === true) {
            console.log('App is installed (iOS)');
            document.body.classList.add('pwa-installed');
        }
    }

    showUpdateNotification() {
        showToast('Eine neue Version ist verfügbar! Seite neu laden für Update.', 'info', 10000);
    }

    setupUpdateDetection() {
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            window.location.reload();
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
});

window.PWAManager = PWAManager;
