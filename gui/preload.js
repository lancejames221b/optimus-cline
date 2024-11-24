const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // Window controls
    minimizeWindow: () => ipcRenderer.send('minimize-window'),
    closeWindow: () => ipcRenderer.send('close-window'),
    
    // Project management
    selectProject: () => ipcRenderer.invoke('selectProject'),
    getCurrentProject: () => ipcRenderer.invoke('getCurrentProject'),
    
    // Command execution
    executeCommand: (command) => ipcRenderer.invoke('executeCommand', command),
    
    // Task management
    createTask: (description) => ipcRenderer.invoke('createTask', description),
    listTasks: () => ipcRenderer.invoke('listTasks'),
    archiveTask: (taskId) => ipcRenderer.invoke('archiveTask', taskId),
    
    // Cost management
    setCostLimit: (limit) => ipcRenderer.invoke('setCostLimit', limit),
    
    // Service Integrations
    configureAtlassian: (credentials, isGlobal) => 
        ipcRenderer.invoke('configureAtlassian', { credentials, isGlobal }),
    configureDigitalOcean: (credentials, isGlobal) => 
        ipcRenderer.invoke('configureDigitalOcean', { credentials, isGlobal }),
    importSSHConfig: (isGlobal) => 
        ipcRenderer.invoke('importSSHConfig', { isGlobal }),
    getCredentials: (service, type, isGlobal) => 
        ipcRenderer.invoke('getCredentials', { service, type, isGlobal }),
    
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
