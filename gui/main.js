// @ts-check
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const Store = require('electron-store');
const fs = require('fs').promises;
const keytar = require('keytar');
const os = require('os');
const ini = require('ini');

/** @type {Electron.BrowserWindow | null} */
let mainWindow = null;

/** @type {import('./types/app').StoreSchema} */
const defaultStore = {
    firstRun: true,
    keysPath: '',
    costLimit: 100,
    totalCost: 0,
    currentProject: null,
    theme: 'dark'
};

const store = new Store({ defaults: defaultStore });

const costPerCommand = 0.01;
let totalCost = store.get('totalCost');
let costLimit = store.get('costLimit');
/** @type {import('./types/app').Project | null} */
let currentProject = store.get('currentProject');

// Default paths
const DEFAULT_KEYS_PATH = path.join(os.homedir(), '.cline', 'keys.txt');
const TEMPLATE_PATH = path.join(__dirname, '..', 'templates', 'configs', 'keys.template');
const TASK_TEMPLATE_PATH = path.join(__dirname, '..', 'templates', 'task.md');

/**
 * Sanitizes a string for use in filenames
 * @param {string} str - String to sanitize
 * @returns {string}
 */
function sanitizeFilename(str) {
    return str
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .substring(0, 50); // Limit length
}

/**
 * Generates a task markdown file from the template
 * @param {string} title - Task title
 * @param {string[]} rules - Task rules
 * @param {string} systemPrompt - System prompt
 * @returns {Promise<string>}
 */
async function generateTaskMarkdown(title, rules, systemPrompt) {
    try {
        const template = await fs.readFile(TASK_TEMPLATE_PATH, 'utf8');
        const date = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-');
        
        // Split template into sections
        const sections = template.split('\n\n');
        
        // Update title and date
        sections[0] = `# Task: ${title}\nDate: ${date}`;
        
        // Find and update rules section
        const rulesIndex = sections.findIndex(s => s.startsWith('## Task Rules'));
        if (rulesIndex !== -1) {
            const defaultRules = sections[rulesIndex].split('\n').filter(line => line.startsWith('- [ ]'));
            const customRules = rules.map(rule => `- [ ] ${rule}`);
            sections[rulesIndex] = `## Task Rules\n${defaultRules.join('\n')}\n${customRules.join('\n')}`;
        }
        
        // Find and update system prompt section
        const promptIndex = sections.findIndex(s => s.startsWith('## System Prompt'));
        if (promptIndex !== -1) {
            sections[promptIndex] = `## System Prompt\n${systemPrompt}`;
        }
        
        // Join sections back together
        return sections.join('\n\n');
    } catch (error) {
        console.error('Failed to generate task markdown:', error);
        throw error;
    }
}

/**
 * Shows the first-time setup window
 * @returns {Promise<void>}
 */
async function showFirstTimeSetup() {
    if (!mainWindow) return;

    const setupWindow = new BrowserWindow({
        width: 600,
        height: 400,
        parent: mainWindow,
        modal: true,
        show: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    setupWindow.loadFile('setup.html');
    setupWindow.once('ready-to-show', () => {
        setupWindow.show();
    });

    // Copy keys template if it doesn't exist
    try {
        await fs.mkdir(path.dirname(DEFAULT_KEYS_PATH), { recursive: true });
        const templateContent = await fs.readFile(TEMPLATE_PATH, 'utf8');
        await fs.writeFile(DEFAULT_KEYS_PATH, templateContent);
    } catch (error) {
        console.error('Failed to create default keys file:', error);
    }

    return new Promise((resolve) => {
        ipcMain.once('setup-complete', (event, /** @type {import('./types/app').SetupConfig} */ config) => {
            store.set('firstRun', false);
            store.set('keysPath', config.keysPath || DEFAULT_KEYS_PATH);
            setupWindow.close();
            resolve();
        });
    });
}

/**
 * Validates a keys file
 * @param {string} filePath - Path to the keys file
 * @returns {Promise<import('./types/app').ValidationResult>}
 */
async function validateKeysFile(filePath) {
    try {
        const content = await fs.readFile(filePath, 'utf8');
        /** @type {import('./types/app').ParsedKeysFile} */
        const sections = {};
        /** @type {string | null} */
        let currentSection = null;
        let isValid = false;

        content.split('\n').forEach(line => {
            line = line.trim();
            if (!line || line.startsWith('#')) return;

            const sectionMatch = line.match(/^\[(.*?)\]$/);
            if (sectionMatch && sectionMatch[1]) {
                currentSection = sectionMatch[1];
                sections[currentSection] = {};
                isValid = true;
                return;
            }

            if (currentSection) {
                const equalIndex = line.indexOf('=');
                if (equalIndex !== -1) {
                    const key = line.slice(0, equalIndex).trim();
                    const value = line.slice(equalIndex + 1).trim();
                    sections[currentSection][key] = value;
                }
            }
        });

        return {
            isValid,
            sections,
            error: isValid ? null : 'Invalid keys file format'
        };
    } catch (error) {
        return {
            isValid: false,
            sections: {},
            error: error instanceof Error ? error.message : 'Unknown error'
        };
    }
}

/**
 * Selects a keys file using the file dialog
 * @returns {Promise<string | null>}
 */
async function selectKeysFile() {
    if (!mainWindow) return null;

    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Configuration Files', extensions: ['txt'] }
        ],
        message: 'Select your keys.txt file',
        defaultPath: os.homedir()
    });

    if (!result.canceled) {
        const filePath = result.filePaths[0];
        const validation = await validateKeysFile(filePath);
        
        if (validation.isValid) {
            store.set('keysPath', filePath);
            return filePath;
        } else {
            throw new Error(validation.error || 'Invalid keys file');
        }
    }
    return null;
}

/**
 * Creates the main application window
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
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
    
    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

// Window control handlers
ipcMain.on('minimize-window', () => {
    mainWindow?.minimize();
});

ipcMain.on('close-window', () => {
    mainWindow?.close();
});

// Project management handlers
ipcMain.handle('getCurrentProject', () => {
    return currentProject;
});

ipcMain.handle('selectProject', async () => {
    if (!mainWindow) return null;

    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        message: 'Select project directory',
        defaultPath: os.homedir()
    });

    if (!result.canceled) {
        const projectPath = result.filePaths[0];
        const projectName = path.basename(projectPath);
        
        currentProject = {
            name: projectName,
            path: projectPath,
            configPath: path.join(projectPath, '.cline')
        };
        
        // Create project config directory
        await fs.mkdir(currentProject.configPath, { recursive: true });
        
        store.set('currentProject', currentProject);
        return currentProject;
    }
    return null;
});

// Task management handlers
ipcMain.handle('createTask', async (event, /** @type {import('./types/app').TaskParams} */ params) => {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-');
    const sanitizedDesc = sanitizeFilename(params.description);
    const taskId = `task_${timestamp}_${sanitizedDesc}`;
    const tasksDir = path.join(currentProject.configPath, 'tasks');
    const taskDir = path.join(tasksDir, taskId);
    
    try {
        // Create tasks directory if it doesn't exist
        await fs.mkdir(tasksDir, { recursive: true });
        // Create task directory
        await fs.mkdir(taskDir);
        
        // Create task metadata
        const taskData = {
            id: taskId,
            title: params.description,
            rules: params.rules,
            systemPrompt: params.systemPrompt,
            status: 'active',
            created: new Date().toISOString()
        };
        
        // Save task metadata
        await fs.writeFile(
            path.join(taskDir, 'task.json'),
            JSON.stringify(taskData, null, 2)
        );
        
        // Generate and save task markdown
        const markdown = await generateTaskMarkdown(
            params.description,
            params.rules,
            params.systemPrompt
        );
        await fs.writeFile(path.join(taskDir, 'task.md'), markdown);
        
        return { id: taskId };
    } catch (error) {
        throw new Error('Failed to create task: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
});

ipcMain.handle('listTasks', async () => {
    if (!currentProject) {
        return { active: [], archived: [] };
    }

    const tasksDir = path.join(currentProject.configPath, 'tasks');
    try {
        await fs.mkdir(tasksDir, { recursive: true });
        const entries = await fs.readdir(tasksDir, { withFileTypes: true });
        
        /** @type {import('./types/app').TaskList} */
        const tasks = {
            active: [],
            archived: []
        };

        for (const entry of entries) {
            if (entry.isDirectory()) {
                try {
                    const taskData = JSON.parse(
                        await fs.readFile(path.join(tasksDir, entry.name, 'task.json'), 'utf8')
                    );
                    if (taskData.status === 'archived') {
                        tasks.archived.push(taskData);
                    } else {
                        tasks.active.push(taskData);
                    }
                } catch (error) {
                    console.error(`Failed to read task ${entry.name}:`, error);
                }
            }
        }

        return tasks;
    } catch (error) {
        console.error('Failed to list tasks:', error);
        return { active: [], archived: [] };
    }
});

ipcMain.handle('archiveTask', async (event, taskId) => {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    const taskPath = path.join(currentProject.configPath, 'tasks', taskId, 'task.json');
    try {
        const taskData = JSON.parse(await fs.readFile(taskPath, 'utf8'));
        taskData.status = 'archived';
        await fs.writeFile(taskPath, JSON.stringify(taskData, null, 2));
        return true;
    } catch (error) {
        throw new Error('Failed to archive task: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
});

// Task execution handlers
ipcMain.handle('openTaskFile', async (event, taskId) => {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    const taskPath = path.join(currentProject.configPath, 'tasks', taskId, 'task.md');
    try {
        // Check if VS Code is available
        const vscodePath = '/usr/local/bin/code';
        try {
            await fs.access(vscodePath);
            // Open in VS Code
            require('child_process').spawn(vscodePath, [taskPath], {
                detached: true,
                stdio: 'ignore'
            }).unref();
        } catch {
            // Fallback to default text editor
            require('child_process').spawn('open', [taskPath], {
                detached: true,
                stdio: 'ignore'
            }).unref();
        }
        return true;
    } catch (error) {
        throw new Error('Failed to open task: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
});

// Credential management handlers
ipcMain.handle('getCredentials', async (event, { service, type }) => {
    try {
        const credentials = await keytar.getPassword(`cline-${service}`, type);
        return credentials ? { credentials: JSON.parse(credentials) } : null;
    } catch (error) {
        console.error(`Failed to get credentials for ${service}:`, error);
        return null;
    }
});

ipcMain.handle('importCredentials', async (event, source) => {
    try {
        if (source === 'keys') {
            const keysPath = store.get('keysPath');
            if (!keysPath) throw new Error('Keys file path not set');
            
            const validation = await validateKeysFile(keysPath);
            if (!validation.isValid) throw new Error(validation.error || 'Invalid keys file');
            
            // Store credentials securely
            for (const [service, creds] of Object.entries(validation.sections)) {
                await keytar.setPassword(`cline-${service}`, service, JSON.stringify(creds));
            }
            return true;
        } else if (source === 'vscode') {
            // TODO: Implement VS Code settings import
            throw new Error('VS Code import not implemented yet');
        }
        return false;
    } catch (error) {
        console.error('Failed to import credentials:', error);
        return false;
    }
});

// Credential file handlers
ipcMain.handle('saveKeysFile', async (event, content) => {
    const keysPath = store.get('keysPath');
    if (!keysPath) {
        throw new Error('Keys file path not set');
    }

    try {
        await fs.writeFile(keysPath, content);
        return true;
    } catch (error) {
        throw new Error('Failed to save keys file: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
});

// Setup handlers
ipcMain.handle('selectKeysFile', async () => {
    return await selectKeysFile();
});

ipcMain.handle('validateKeysFile', async (event, filePath) => {
    return await validateKeysFile(filePath);
});

ipcMain.handle('getDefaultKeysPath', () => {
    return DEFAULT_KEYS_PATH;
});

ipcMain.handle('getKeysTemplate', async () => {
    try {
        return await fs.readFile(TEMPLATE_PATH, 'utf8');
    } catch (error) {
        console.error('Failed to read template:', error);
        return '';
    }
});

// App lifecycle
app.whenReady().then(async () => {
    createWindow();
    
    // Show first-time setup if needed
    if (store.get('firstRun')) {
        await showFirstTimeSetup();
    }
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
