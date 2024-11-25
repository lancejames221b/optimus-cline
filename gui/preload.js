// @ts-check
const { contextBridge, ipcRenderer } = require('electron');

/** @type {import('./types/renderer').ElectronAPI} */
const api = {
    // Window controls
    minimizeWindow: () => ipcRenderer.send('minimize-window'),
    closeWindow: () => ipcRenderer.send('close-window'),
    
    // Project management
    selectProject: () => ipcRenderer.invoke('selectProject'),
    getCurrentProject: () => ipcRenderer.invoke('getCurrentProject'),
    
    // Task management
    createTask: (params) => ipcRenderer.invoke('createTask', params),
    listTasks: () => ipcRenderer.invoke('listTasks'),
    archiveTask: (taskId) => ipcRenderer.invoke('archiveTask', taskId),
    openTaskFile: (taskId) => ipcRenderer.invoke('openTaskFile', taskId),
    
    // Credential Management
    getCredentials: (service, type) => ipcRenderer.invoke('getCredentials', { service, type }),
    importCredentials: (source) => ipcRenderer.invoke('importCredentials', source),
    saveKeysFile: (content) => ipcRenderer.invoke('saveKeysFile', content),
    
    // File Management
    selectKeysFile: () => ipcRenderer.invoke('selectKeysFile'),
    validateKeysFile: (filePath) => ipcRenderer.invoke('validateKeysFile', filePath),
    getDefaultKeysPath: () => ipcRenderer.invoke('getDefaultKeysPath'),
    getKeysTemplate: () => ipcRenderer.invoke('getKeysTemplate'),
    
    // Setup
    completeSetup: (config) => ipcRenderer.send('setup-complete', config),
    
    // Event listeners
    onCommandExecuted: (callback) => {
        ipcRenderer.on('command-executed', (_event, command, result) => callback(command, result));
    },
    onCostUpdate: (callback) => {
        ipcRenderer.on('cost-update', (_event, cost) => callback(cost));
    },
    onCostLimitReached: (callback) => {
        ipcRenderer.on('cost-limit-reached', () => callback());
    },
    onTaskUpdate: (callback) => {
        ipcRenderer.on('task-update', (_event, task) => callback(task));
    },
    
    // Remove event listeners
    removeCommandListener: () => ipcRenderer.removeAllListeners('command-executed'),
    removeCostUpdateListener: () => ipcRenderer.removeAllListeners('cost-update'),
    removeCostLimitListener: () => ipcRenderer.removeAllListeners('cost-limit-reached'),
    removeTaskUpdateListener: () => ipcRenderer.removeAllListeners('task-update')
};

// Expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', api);
