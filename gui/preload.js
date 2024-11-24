const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
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
    updateTaskRules: (params) => ipcRenderer.invoke('updateTaskRules', params),
    
    // Cost management
    setCostLimit: (limit) => ipcRenderer.invoke('setCostLimit', limit),
    
    // Credential Management
    importCredentials: (source) => ipcRenderer.invoke('importCredentials', source),
    configureGitHub: (credentials) => ipcRenderer.invoke('configureGitHub', credentials),
    getCredentials: (service, type) => ipcRenderer.invoke('getCredentials', { service, type }),
    
    // Event listeners
    onCommandExecuted: (callback) => ipcRenderer.on('command-executed', callback),
    onCostUpdate: (callback) => ipcRenderer.on('cost-update', callback),
    onCostLimitReached: (callback) => ipcRenderer.on('cost-limit-reached', callback),
    onTaskUpdate: (callback) => ipcRenderer.on('task-update', callback),
    
    // Remove event listeners
    removeCommandListener: () => ipcRenderer.removeAllListeners('command-executed'),
    removeCostUpdateListener: () => ipcRenderer.removeAllListeners('cost-update'),
    removeCostLimitListener: () => ipcRenderer.removeAllListeners('cost-limit-reached'),
    removeTaskUpdateListener: () => ipcRenderer.removeAllListeners('task-update')
});
