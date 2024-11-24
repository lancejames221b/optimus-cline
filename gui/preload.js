const { contextBridge, ipcRenderer } = require('electron');
const keytar = require('keytar');

// Secure credential management
contextBridge.exposeInMainWorld('credentials', {
    // Store credentials securely
    store: async (service, account, password) => {
        try {
            await keytar.setPassword(service, account, password);
            return true;
        } catch (error) {
            console.error('Error saving credential:', error);
            return false;
        }
    },

    // Retrieve credentials
    get: async (service, account) => {
        try {
            return await keytar.getPassword(service, account);
        } catch (error) {
            console.error('Error getting credential:', error);
            return null;
        }
    },

    // List all credentials for a service
    list: async (service) => {
        try {
            return await keytar.findCredentials(service);
        } catch (error) {
            console.error('Error listing credentials:', error);
            return [];
        }
    }
});

// Command execution
contextBridge.exposeInMainWorld('commands', {
    execute: (command) => ipcRenderer.invoke('executeCommand', command),
    setCostLimit: (limit) => ipcRenderer.invoke('setCostLimit', limit),
    onCostUpdate: (callback) => ipcRenderer.on('cost-update', callback),
    onLimitReached: (callback) => ipcRenderer.on('cost-limit-reached', callback)
});

// Window controls
contextBridge.exposeInMainWorld('window', {
    minimize: () => ipcRenderer.send('minimize-window'),
    close: () => ipcRenderer.send('close-window')
});

// Task management
contextBridge.exposeInMainWorld('tasks', {
    create: (name) => ipcRenderer.invoke('createTask', name),
    list: () => ipcRenderer.invoke('listTasks'),
    archive: (taskId) => ipcRenderer.invoke('archiveTask', taskId)
});

// History management
contextBridge.exposeInMainWorld('history', {
    save: (command, result) => ipcRenderer.invoke('saveHistory', { command, result }),
    load: () => ipcRenderer.invoke('loadHistory'),
    createCheckpoint: (name) => ipcRenderer.invoke('createCheckpoint', name),
    revertToCheckpoint: (name) => ipcRenderer.invoke('revertToCheckpoint', name),
    getCheckpoints: () => ipcRenderer.invoke('getCheckpoints')
});

// Notifications
contextBridge.exposeInMainWorld('notifications', {
    show: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
});
