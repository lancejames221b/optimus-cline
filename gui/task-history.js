const fs = require('fs').promises;
const path = require('path');
const { CommandHistory } = require('./command-history');

class TaskHistory {
    constructor(taskDir) {
        this.taskDir = taskDir;
        this.histories = new Map(); // taskId -> CommandHistory
        this.activeTask = null;
    }

    async loadTask(taskId) {
        if (!this.histories.has(taskId)) {
            const historyPath = path.join(this.taskDir, `${taskId}.history.json`);
            try {
                const data = await fs.readFile(historyPath, 'utf8');
                const history = new CommandHistory();
                history.load(data);
                this.histories.set(taskId, history);
            } catch (error) {
                // No history file exists yet, create new history
                this.histories.set(taskId, new CommandHistory());
            }
        }
        this.activeTask = taskId;
        return this.histories.get(taskId);
    }

    async saveTask(taskId) {
        const history = this.histories.get(taskId);
        if (history) {
            const historyPath = path.join(this.taskDir, `${taskId}.history.json`);
            await fs.writeFile(historyPath, history.save());
        }
    }

    getActiveHistory() {
        return this.activeTask ? this.histories.get(this.activeTask) : null;
    }

    async createCheckpoint(name) {
        const history = this.getActiveHistory();
        if (history) {
            history.branch(name);
            await this.saveTask(this.activeTask);
            return true;
        }
        return false;
    }

    async revertToCheckpoint(name) {
        const history = this.getActiveHistory();
        if (history) {
            const success = history.switchToBranch(name);
            if (success) {
                await this.saveTask(this.activeTask);
            }
            return success;
        }
        return false;
    }

    getCheckpoints() {
        const history = this.getActiveHistory();
        return history ? Array.from(history.branches.keys()) : [];
    }

    async addCommand(command, metadata = {}) {
        const history = this.getActiveHistory();
        if (history) {
            const node = history.execute(command, metadata);
            await this.saveTask(this.activeTask);
            return node;
        }
        return null;
    }

    async revertSteps(steps) {
        const history = this.getActiveHistory();
        if (history) {
            const node = history.revert(steps);
            await this.saveTask(this.activeTask);
            return node;
        }
        return null;
    }
}

// Update main.js to use TaskHistory
ipcMain.handle('loadTaskHistory', async (event, taskId) => {
    const taskHistory = new TaskHistory(path.join(os.homedir(), '.cline/tasks'));
    await taskHistory.loadTask(taskId);
    return taskHistory.getActiveHistory().getHistory();
});

ipcMain.handle('saveCommand', async (event, { taskId, command, metadata }) => {
    const taskHistory = new TaskHistory(path.join(os.homedir(), '.cline/tasks'));
    await taskHistory.loadTask(taskId);
    const node = await taskHistory.addCommand(command, metadata);
    return node ? true : false;
});

ipcMain.handle('createCheckpoint', async (event, { taskId, name }) => {
    const taskHistory = new TaskHistory(path.join(os.homedir(), '.cline/tasks'));
    await taskHistory.loadTask(taskId);
    return await taskHistory.createCheckpoint(name);
});

ipcMain.handle('revertToCheckpoint', async (event, { taskId, name }) => {
    const taskHistory = new TaskHistory(path.join(os.homedir(), '.cline/tasks'));
    await taskHistory.loadTask(taskId);
    return await taskHistory.revertToCheckpoint(name);
});

ipcMain.handle('getCheckpoints', async (event, taskId) => {
    const taskHistory = new TaskHistory(path.join(os.homedir(), '.cline/tasks'));
    await taskHistory.loadTask(taskId);
    return taskHistory.getCheckpoints();
});

// Add to renderer.js
function loadTaskHistory(taskId) {
    ipcRenderer.invoke('loadTaskHistory', taskId).then(history => {
        commandHistory.load(history);
        visualizeHistory();
        updateCheckpointList();
    });
}

function updateCheckpointList() {
    const select = document.getElementById('branchSelect');
    select.innerHTML = '<option value="">Switch Checkpoint...</option>';
    
    ipcRenderer.invoke('getCheckpoints', currentTaskId).then(checkpoints => {
        checkpoints.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            select.appendChild(option);
        });
    });
}

function switchCheckpoint(name) {
    if (name) {
        ipcRenderer.invoke('revertToCheckpoint', {
            taskId: currentTaskId,
            name: name
        }).then(success => {
            if (success) {
                loadTaskHistory(currentTaskId);
                showNotification(`Switched to checkpoint: ${name}`);
            }
        });
    }
}

// Add checkpoint creation with notes
function createNamedCheckpoint() {
    const name = prompt('Enter checkpoint name:');
    const notes = prompt('Enter checkpoint notes (optional):');
    
    if (name) {
        ipcRenderer.invoke('createCheckpoint', {
            taskId: currentTaskId,
            name: name,
            metadata: { notes }
        }).then(success => {
            if (success) {
                updateCheckpointList();
                showNotification(`Created checkpoint: ${name}`);
            }
        });
    }
}

