const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const Store = require('electron-store');
const fs = require('fs').promises;
const keytar = require('keytar');
const os = require('os');
const { exec, spawn } = require('child_process');
const ini = require('ini');
const store = new Store();

let mainWindow;
const costPerCommand = 0.01;
let totalCost = store.get('totalCost') || 0;
let costLimit = store.get('costLimit') || 100;
let currentProject = store.get('currentProject') || null;

// Default task rules
const DEFAULT_TASK_RULES = [
    "Don't delete production systems",
    "Always backup before making changes",
    "Verify changes in staging first",
    "Follow security protocols",
    "Document all changes"
];

// Task Management
async function createTask(description, rules = [], systemPrompt = '') {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    try {
        // Generate task ID
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const taskId = `task_${timestamp}_${description.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const taskPath = path.join(currentProject.path, '.cline', 'tasks', 'active', `${taskId}.md`);

        // Read task template
        const templatePath = path.join(currentProject.path, '.cline', 'tasks', 'templates', 'task.md');
        let template = await fs.readFile(templatePath, 'utf8');

        // Replace template variables
        template = template
            .replace('{TITLE}', description)
            .replace('{DATE}', new Date().toISOString());

        // Add custom rules
        const allRules = [...DEFAULT_TASK_RULES, ...rules];
        const rulesSection = allRules.map(rule => `- [ ] ${rule}`).join('\n');
        template = template.replace('[Additional task-specific rules will be added here]', rulesSection);

        // Add system prompt
        template = template.replace(
            '[Task-specific system prompt that defines behavior, constraints, and objectives]',
            systemPrompt || 'Default system prompt: Follow task rules and maintain system integrity.'
        );

        // Write task file
        await fs.writeFile(taskPath, template);

        // Create symlink in Desktop cline-tasks
        const desktopTaskPath = path.join(os.homedir(), 'Desktop', 'cline-tasks', currentProject.name);
        await fs.mkdir(desktopTaskPath, { recursive: true });
        await fs.symlink(taskPath, path.join(desktopTaskPath, `${taskId}.md`));

        return {
            id: taskId,
            path: taskPath,
            description,
            rules: allRules,
            systemPrompt
        };
    } catch (error) {
        console.error('Failed to create task:', error);
        throw error;
    }
}

async function listTasks() {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    try {
        const activePath = path.join(currentProject.path, '.cline', 'tasks', 'active');
        const archivePath = path.join(currentProject.path, '.cline', 'tasks', 'archive');

        const [activeFiles, archiveFiles] = await Promise.all([
            fs.readdir(activePath),
            fs.readdir(archivePath)
        ]);

        const tasks = {
            active: await Promise.all(activeFiles
                .filter(file => file.endsWith('.md'))
                .map(file => parseTaskFile(path.join(activePath, file), 'active'))),
            archived: await Promise.all(archiveFiles
                .filter(file => file.endsWith('.md'))
                .map(file => parseTaskFile(path.join(archivePath, file), 'archived')))
        };

        return tasks;
    } catch (error) {
        console.error('Failed to list tasks:', error);
        throw error;
    }
}

async function parseTaskFile(filePath, status) {
    try {
        const content = await fs.readFile(filePath, 'utf8');
        const lines = content.split('\n');
        
        // Parse basic info
        const titleMatch = lines[0].match(/# Task: (.*)/);
        const title = titleMatch ? titleMatch[1] : 'Untitled Task';
        
        // Parse rules
        const rules = [];
        let inRulesSection = false;
        let systemPrompt = '';
        
        for (const line of lines) {
            if (line.startsWith('## Task Rules')) {
                inRulesSection = true;
                continue;
            } else if (line.startsWith('## System Prompt')) {
                inRulesSection = false;
                systemPrompt = lines[lines.indexOf(line) + 1];
                continue;
            } else if (line.startsWith('##')) {
                inRulesSection = false;
                continue;
            }
            
            if (inRulesSection && line.startsWith('- ')) {
                rules.push(line.substring(2).trim());
            }
        }

        return {
            id: path.basename(filePath, '.md'),
            title,
            status,
            rules,
            systemPrompt,
            path: filePath
        };
    } catch (error) {
        console.error('Failed to parse task file:', error);
        throw error;
    }
}

async function archiveTask(taskId) {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    try {
        const activePath = path.join(currentProject.path, '.cline', 'tasks', 'active', `${taskId}.md`);
        const archivePath = path.join(currentProject.path, '.cline', 'tasks', 'archive', `${taskId}.md`);

        await fs.rename(activePath, archivePath);

        // Update symlink in Desktop cline-tasks
        const desktopTaskPath = path.join(os.homedir(), 'Desktop', 'cline-tasks', currentProject.name, `${taskId}.md`);
        await fs.unlink(desktopTaskPath).catch(() => {}); // Ignore if doesn't exist

        return { success: true, taskId };
    } catch (error) {
        console.error('Failed to archive task:', error);
        throw error;
    }
}

async function updateTaskRules(taskId, rules) {
    if (!currentProject) {
        throw new Error('No project selected');
    }

    try {
        const taskPath = path.join(currentProject.path, '.cline', 'tasks', 'active', `${taskId}.md`);
        const content = await fs.readFile(taskPath, 'utf8');
        
        // Update rules section
        const lines = content.split('\n');
        let inRulesSection = false;
        let newContent = '';
        
        for (const line of lines) {
            if (line.startsWith('## Task Rules')) {
                inRulesSection = true;
                newContent += line + '\n';
                rules.forEach(rule => {
                    newContent += `- [ ] ${rule}\n`;
                });
                continue;
            } else if (line.startsWith('##')) {
                inRulesSection = false;
            }
            
            if (!inRulesSection) {
                newContent += line + '\n';
            }
        }

        await fs.writeFile(taskPath, newContent);
        return { success: true, taskId };
    } catch (error) {
        console.error('Failed to update task rules:', error);
        throw error;
    }
}

// IPC Handlers
ipcMain.handle('createTask', async (event, { description, rules, systemPrompt }) => {
    return await createTask(description, rules, systemPrompt);
});

ipcMain.handle('listTasks', async () => {
    return await listTasks();
});

ipcMain.handle('archiveTask', async (event, taskId) => {
    return await archiveTask(taskId);
});

ipcMain.handle('updateTaskRules', async (event, { taskId, rules }) => {
    return await updateTaskRules(taskId, rules);
});

[Previous credential management and other functions remain unchanged...]

// Window Management
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800, // Increased width for better task management
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

// App lifecycle
app.whenReady().then(() => {
    createWindow();
    
    // Restore last project if available
    if (currentProject) {
        initializeProject(currentProject.path).catch(console.error);
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
