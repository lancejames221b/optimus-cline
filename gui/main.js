const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const Store = require('electron-store');
const fs = require('fs').promises;
const keytar = require('keytar');
const os = require('os');
const { exec, spawn } = require('child_process');
const store = new Store();

let mainWindow;
const costPerCommand = 0.01;
let totalCost = store.get('totalCost') || 0;
let costLimit = store.get('costLimit') || 100;
let currentProject = store.get('currentProject') || null;

// Task monitoring
let activeTasks = new Map();
const TASK_DIR = path.join(os.homedir(), 'Desktop', 'cline-tasks');

// Integration constants
const VSCODE_SSH_CONFIG = path.join(os.homedir(), '.ssh/config');
const SERVICE_TYPES = {
    ATLASSIAN: 'atlassian',
    DIGITAL_OCEAN: 'digitalocean',
    SSH: 'ssh'
};

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 400,
        height: 600,
        x: 50,
        y: 50,
        frame: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        alwaysOnTop: true,
        resizable: true,
        transparent: true,
        hasShadow: true
    });

    mainWindow.loadFile('index.html');
}

// Project Management
async function initializeProject(projectPath) {
    try {
        const clineDir = path.join(projectPath, '.cline');
        const configDir = path.join(clineDir, 'configs');
        
        // Check if project is initialized
        const isInitialized = await fs.access(clineDir)
            .then(() => true)
            .catch(() => false);
        
        if (!isInitialized) {
            throw new Error('Project not initialized. Please run init-project.sh first.');
        }
        
        // Load project configuration
        const projectConfig = {
            path: projectPath,
            name: path.basename(projectPath),
            configPath: configDir
        };
        
        store.set('currentProject', projectConfig);
        currentProject = projectConfig;
        
        return projectConfig;
    } catch (error) {
        console.error('Failed to initialize project:', error);
        throw error;
    }
}

async function getProjectCredentials(service, type) {
    if (!currentProject) return null;
    
    const credentialKey = `${currentProject.name}:${service}:${type}`;
    try {
        const data = await keytar.getPassword('cline-project', credentialKey);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Failed to get project credentials:', error);
        return null;
    }
}

async function storeProjectCredentials(service, type, credentials) {
    if (!currentProject) throw new Error('No project selected');
    
    const credentialKey = `${currentProject.name}:${service}:${type}`;
    try {
        const encryptedData = JSON.stringify({
            type,
            credentials,
            timestamp: Date.now()
        });
        await keytar.setPassword('cline-project', credentialKey, encryptedData);
        
        // Store configuration reference in project
        const configFile = path.join(currentProject.configPath, `${service}-config.json`);
        await fs.writeFile(configFile, JSON.stringify({
            type,
            service,
            lastUpdated: Date.now()
        }, null, 2));
        
        return true;
    } catch (error) {
        console.error('Failed to store project credentials:', error);
        return false;
    }
}

// Credential Management System
async function storeGlobalCredentials(service, type, credentials) {
    try {
        const encryptedData = JSON.stringify({
            type,
            credentials,
            timestamp: Date.now()
        });
        await keytar.setPassword('cline-global', `${service}:${type}`, encryptedData);
        return true;
    } catch (error) {
        console.error('Failed to store global credentials:', error);
        return false;
    }
}

async function getGlobalCredentials(service, type) {
    try {
        const data = await keytar.getPassword('cline-global', `${service}:${type}`);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Failed to get global credentials:', error);
        return null;
    }
}

// Integration Configuration
async function configureAtlassian(credentials, isGlobal = false) {
    const store = isGlobal ? storeGlobalCredentials : storeProjectCredentials;
    return await store('atlassian', SERVICE_TYPES.ATLASSIAN, {
        domain: credentials.domain,
        email: credentials.email,
        apiToken: credentials.apiToken,
        products: credentials.products || ['jira', 'confluence']
    });
}

async function configureDigitalOcean(credentials, isGlobal = false) {
    const store = isGlobal ? storeGlobalCredentials : storeProjectCredentials;
    return await store('digitalocean', SERVICE_TYPES.DIGITAL_OCEAN, {
        apiKey: credentials.apiKey,
        spaces: {
            key: credentials.spacesKey,
            secret: credentials.spacesSecret
        }
    });
}

async function importVSCodeSSHConfig(isGlobal = false) {
    try {
        const configContent = await fs.readFile(VSCODE_SSH_CONFIG, 'utf8');
        const hosts = parseSSHConfig(configContent);
        const store = isGlobal ? storeGlobalCredentials : storeProjectCredentials;
        
        for (const [host, config] of Object.entries(hosts)) {
            await store('ssh', SERVICE_TYPES.SSH, {
                host,
                ...config
            });
        }
        
        return true;
    } catch (error) {
        console.error('Failed to import SSH config:', error);
        return false;
    }
}

function parseSSHConfig(content) {
    const hosts = {};
    let currentHost = null;
    
    content.split('\n').forEach(line => {
        line = line.trim();
        if (!line || line.startsWith('#')) return;
        
        if (line.toLowerCase().startsWith('host ')) {
            currentHost = line.split(' ')[1];
            hosts[currentHost] = {};
        } else if (currentHost && line.includes(' ')) {
            const [key, ...values] = line.split(' ');
            hosts[currentHost][key.toLowerCase()] = values.join(' ');
        }
    });
    
    return hosts;
}

// CLI Integration
function executeCliCommand(command, args) {
    return new Promise((resolve, reject) => {
        const cwd = currentProject ? currentProject.path : process.cwd();
        exec(`${command} ${args.join(' ')}`, { cwd }, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else {
                updateCost(costPerCommand);
                resolve({ stdout, stderr });
            }
        });
    });
}

// Cost management
function updateCost(amount) {
    totalCost += amount;
    store.set('totalCost', totalCost);
    mainWindow.webContents.send('cost-update', totalCost);

    if (totalCost >= costLimit) {
        mainWindow.webContents.send('cost-limit-reached');
    }
}

// IPC Handlers
ipcMain.handle('selectProject', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
    });
    
    if (!result.canceled) {
        const projectPath = result.filePaths[0];
        return await initializeProject(projectPath);
    }
    return null;
});

ipcMain.handle('getCurrentProject', () => {
    return currentProject;
});

ipcMain.handle('configureAtlassian', async (event, params) => {
    return await configureAtlassian(params.credentials, params.isGlobal);
});

ipcMain.handle('configureDigitalOcean', async (event, params) => {
    return await configureDigitalOcean(params.credentials, params.isGlobal);
});

ipcMain.handle('importSSHConfig', async (event, params) => {
    return await importVSCodeSSHConfig(params.isGlobal);
});

ipcMain.handle('getCredentials', async (event, params) => {
    return params.isGlobal ? 
        await getGlobalCredentials(params.service, params.type) : 
        await getProjectCredentials(params.service, params.type);
});

ipcMain.handle('executeCommand', async (event, command) => {
    return await executeCliCommand(command, []);
});

ipcMain.handle('createTask', async (event, description) => {
    return await executeCliCommand('new-task.sh', [description]);
});

ipcMain.handle('listTasks', async () => {
    const result = await executeCliCommand('list-tasks.sh', []);
    return result.stdout.trim().split('\n').map(task => {
        const [id, description, status] = task.split('\t');
        return { id, description, status };
    });
});

ipcMain.handle('archiveTask', async (event, taskId) => {
    return await executeCliCommand('archive-task.sh', [taskId]);
});

ipcMain.handle('setCostLimit', (event, limit) => {
    costLimit = limit;
    store.set('costLimit', limit);
});

ipcMain.on('minimize-window', () => {
    mainWindow.minimize();
});

ipcMain.on('close-window', () => {
    mainWindow.close();
});

// App lifecycle
app.whenReady().then(() => {
    createWindow();
    
    // Restore last project if available
    if (currentProject) {
        initializeProject(currentProject.path).catch(console.error);
    }
    
    // Start monitoring existing tasks
    fs.readdir(TASK_DIR)
        .then(files => {
            files.forEach(file => {
                if (file.startsWith('task_')) {
                    monitorTask(file);
                }
            });
        })
        .catch(console.error);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
