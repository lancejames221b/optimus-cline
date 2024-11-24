// Imports
const { ipcRenderer } = require('electron');

// State management
let currentCost = 0;
let costLimit = 100;
let pendingCommands = [];
let recentCommands = [];

// UI Elements
const costDisplay = document.getElementById('currentCost');
const costLimitDisplay = document.getElementById('costLimitDisplay');
const costProgress = document.getElementById('costProgress');
const autoRunToggle = document.getElementById('autoRun');
const autoSaveToggle = document.getElementById('autoSave');

// Theme colors with opacity
const colors = {
    success: '#4CAF50',
    warning: '#FFC107',
    danger: '#F44336',
    getProgressColor: (percentage) => {
        if (percentage < 60) return colors.success;
        if (percentage < 80) return colors.warning;
        return colors.danger;
    }
};

// Animation configurations
const animations = {
    fadeIn: [
        { opacity: 0, transform: 'translateY(-20px)' },
        { opacity: 1, transform: 'translateY(0)' }
    ],
    fadeOut: [
        { opacity: 1, transform: 'translateY(0)' },
        { opacity: 0, transform: 'translateY(20px)' }
    ],
    shake: [
        { transform: 'translateX(0)' },
        { transform: 'translateX(-5px)' },
        { transform: 'translateX(5px)' },
        { transform: 'translateX(0)' }
    ]
};

// UI Functions
function showTab(tabName) {
    document.querySelectorAll('.content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    const content = document.getElementById(tabName);
    const tab = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    
    content.classList.add('active');
    tab.classList.add('active');
    
    content.animate(animations.fadeIn, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });
}

function updateCostDisplay() {
    const percentage = (currentCost / costLimit) * 100;
    costDisplay.textContent = currentCost.toFixed(2);
    costLimitDisplay.textContent = costLimit.toFixed(2);
    
    costProgress.style.width = `${percentage}%`;
    costProgress.style.backgroundColor = colors.getProgressColor(percentage);
    
    if (percentage >= 90) {
        costDisplay.parentElement.animate(animations.shake, {
            duration: 500,
            iterations: 1
        });
    }
}

function addCommandItem(command, type = 'pending') {
    const list = document.getElementById(`${type}Commands`);
    const item = document.createElement('div');
    item.className = 'command-item';
    
    const timestamp = new Date().toLocaleTimeString();
    
    item.innerHTML = `
        <div class="command-info">
            <div class="command-text">${command}</div>
            <div class="command-meta">${timestamp}</div>
        </div>
        ${type === 'pending' ? `
            <div class="command-actions">
                <button class="btn btn-success" onclick="executeCommand('${command}')">Run</button>
                <button class="btn btn-primary" onclick="saveCommand('${command}')">Save</button>
                <button class="btn btn-secondary" onclick="skipCommand('${command}')">Skip</button>
            </div>
        ` : ''}
    `;
    
    list.insertBefore(item, list.firstChild);
    item.animate(animations.fadeIn, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });
}

// Command Management
async function executeCommand(command) {
    const cost = 0.01; // Cost per command
    currentCost += cost;
    updateCostDisplay();
    
    await ipcRenderer.invoke('executeCommand', command);
    moveCommandToRecent(command, 'Executed');
}

function saveCommand(command) {
    ipcRenderer.invoke('saveCommand', command);
    moveCommandToRecent(command, 'Saved');
}

function skipCommand(command) {
    moveCommandToRecent(command, 'Skipped');
}

function moveCommandToRecent(command, action) {
    const pendingItem = document.querySelector(`.command-item:has(.command-text:contains("${command}"))`);
    if (pendingItem) {
        pendingItem.animate(animations.fadeOut, {
            duration: 300,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        }).onfinish = () => {
            pendingItem.remove();
            addCommandItem(`${command} (${action})`, 'recent');
        };
    }
}

// Credential Management
function addCredential() {
    const form = document.getElementById('credentialForm');
    form.style.display = 'block';
    form.animate(animations.fadeIn, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });
}

async function saveCredential() {
    const service = document.getElementById('serviceType').value;
    const fields = document.getElementById('credentialFields').children;
    const credentials = {};
    
    Array.from(fields).forEach(field => {
        credentials[field.name] = field.value;
    });
    
    const success = await ipcRenderer.invoke('storeCredential', { service, credentials });
    if (success) {
        document.getElementById('credentialForm').style.display = 'none';
        loadCredentials();
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadCredentials();
    updateCostDisplay();
    
    autoRunToggle.addEventListener('change', (e) => {
        ipcRenderer.send('setAutoRun', e.target.checked);
    });
    
    autoSaveToggle.addEventListener('change', (e) => {
        ipcRenderer.send('setAutoSave', e.target.checked);
    });
});

// Window Controls
function minimizeWindow() {
    ipcRenderer.send('minimize-window');
}

function closeWindow() {
    ipcRenderer.send('close-window');
}

// IPC Handlers
ipcRenderer.on('commandDetected', (event, data) => {
    addCommandItem(data.command);
});

ipcRenderer.on('costUpdate', (event, cost) => {
    currentCost = cost;
    updateCostDisplay();
});

ipcRenderer.on('costLimitReached', () => {
    autoRunToggle.checked = false;
    document.body.animate(animations.shake, {
        duration: 500,
        iterations: 1
    });
});

// Command History Visualization
const commandHistory = new CommandHistory();

function visualizeHistory() {
    const historyContainer = document.getElementById('commandHistory');
    const history = commandHistory.getHistory();
    
    historyContainer.innerHTML = '';
    
    history.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'history-item';
        if (entry.isCurrent) item.classList.add('current');
        
        const indent = '├─ '.repeat(entry.level);
        const branches = entry.branches.length ? 
            `[${entry.branches.join(', ')}]` : '';
        
        item.innerHTML = `
            <div class="history-content" style="margin-left: ${entry.level * 20}px">
                <div class="history-command">
                    <span class="history-prefix">${indent}</span>
                    <span class="command-text">${entry.command}</span>
                    <span class="branch-tags">${branches}</span>
                </div>
                <div class="history-meta">
                    <span class="timestamp">${new Date(entry.timestamp).toLocaleTimeString()}</span>
                    <span class="status ${entry.status}">${entry.status}</span>
                </div>
                <div class="history-actions">
                    <button onclick="revertTo('${entry.timestamp}')" 
                            class="btn btn-warning btn-sm">Revert</button>
                    <button onclick="branchFrom('${entry.timestamp}')" 
                            class="btn btn-primary btn-sm">Branch</button>
                </div>
            </div>
        `;
        
        historyContainer.appendChild(item);
    });
}

function revertTo(timestamp) {
    const steps = getStepsToTimestamp(timestamp);
    if (steps > 0) {
        const node = commandHistory.revert(steps);
        visualizeHistory();
        
        // Show revert notification
        showNotification(`Reverted ${steps} steps to: ${node.command}`);
    }
}

function branchFrom(timestamp) {
    const branchName = prompt('Enter branch name:');
    if (branchName) {
        const steps = getStepsToTimestamp(timestamp);
        if (steps > 0) {
            commandHistory.revert(steps);
            commandHistory.branch(branchName);
            visualizeHistory();
            
            showNotification(`Created branch '${branchName}'`);
        }
    }
}

function getStepsToTimestamp(timestamp) {
    let steps = 0;
    let current = commandHistory.current;
    
    while (current && current.timestamp !== parseInt(timestamp)) {
        steps++;
        current = current.parent;
    }
    
    return steps;
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    notification.animate(animations.fadeIn, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });
    
    setTimeout(() => {
        notification.animate(animations.fadeOut, {
            duration: 300,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        }).onfinish = () => notification.remove();
    }, 3000);
}

// Add history styles
const style = document.createElement('style');
style.textContent = `
.history-item {
    margin: 10px 0;
    padding: 10px;
    background: var(--secondary);
    border-radius: 6px;
    transition: all 0.3s ease;
}

.history-item.current {
    background: var(--accent);
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.history-content {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.history-command {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'SF Mono', monospace;
}

.history-prefix {
    color: var(--text);
    opacity: 0.7;
}

.branch-tags {
    color: var(--accent);
    font-size: 0.9em;
}

.history-meta {
    display: flex;
    gap: 10px;
    font-size: 0.9em;
    color: var(--text);
    opacity: 0.8;
}

.status {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8em;
}

.status.success { background: var(--success); }
.status.error { background: var(--danger); }
.status.reverted { background: var(--warning); }

.history-actions {
    display: flex;
    gap: 8px;
    margin-top: 5px;
}

.btn-sm {
    padding: 4px 8px;
    font-size: 0.9em;
}

.notification {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--accent);
    color: white;
    padding: 10px 20px;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    z-index: 1000;
}
`;

document.head.appendChild(style);

// Initialize history visualization
document.addEventListener('DOMContentLoaded', () => {
    const historyTab = document.createElement('button');
    historyTab.className = 'tab';
    historyTab.textContent = 'History';
    historyTab.onclick = () => showTab('history');
    document.querySelector('.tab-container').appendChild(historyTab);
    
    const historyContent = document.createElement('div');
    historyContent.id = 'history';
    historyContent.className = 'content';
    historyContent.innerHTML = `
        <div class="history-controls">
            <button class="btn btn-primary" onclick="commandHistory.branch('checkpoint')">
                Create Checkpoint
            </button>
            <select id="branchSelect" onchange="switchBranch(this.value)">
                <option value="">Switch Branch...</option>
            </select>
        </div>
        <div id="commandHistory"></div>
    `;
    document.querySelector('.container').appendChild(historyContent);
    
    visualizeHistory();
});

// Update command execution to include history
const originalExecuteCommand = executeCommand;
executeCommand = async function(command) {
    const node = commandHistory.execute(command);
    try {
        await originalExecuteCommand(command);
        node.setResult({ success: true });
    } catch (error) {
        node.setResult({ success: false, error });
    }
    visualizeHistory();
};
