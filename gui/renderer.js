// State management
let currentCost = 0;
let costLimit = 100;
let currentProject = null;
let customRules = [];
let defaultRules = [
    "Don't delete production systems",
    "Always backup before making changes",
    "Verify changes in staging first",
    "Follow security protocols",
    "Document all changes"
];

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
    ]
};

// Task Management
function showNewTaskDialog() {
    const dialog = document.getElementById('newTaskDialog');
    dialog.style.display = 'flex';
    
    // Reset form
    document.getElementById('taskDescription').value = '';
    document.getElementById('systemPrompt').value = '';
    document.getElementById('newRule').value = '';
    customRules = [];
    
    // Reset safety checks
    document.querySelectorAll('.safety-checks input[type="checkbox"]')
        .forEach(checkbox => checkbox.checked = false);
    
    // Load default rules
    updateRulesList();
}

function closeNewTaskDialog() {
    const dialog = document.getElementById('newTaskDialog');
    dialog.style.display = 'none';
}

function updateRulesList() {
    // Update default rules
    const defaultRulesList = document.getElementById('defaultRules');
    defaultRulesList.innerHTML = defaultRules.map(rule => `
        <div class="rule-item">
            <span class="rule-text">${rule}</span>
        </div>
    `).join('');
    
    // Update custom rules
    const customRulesList = document.getElementById('customRules');
    customRulesList.innerHTML = customRules.map((rule, index) => `
        <div class="rule-item">
            <span class="rule-text">${rule}</span>
            <button class="btn btn-danger btn-sm" onclick="removeCustomRule(${index})">×</button>
        </div>
    `).join('');
}

function addTaskRule() {
    const input = document.getElementById('newRule');
    const rule = input.value.trim();
    
    if (rule) {
        customRules.push(rule);
        input.value = '';
        updateRulesList();
    }
}

function removeCustomRule(index) {
    customRules.splice(index, 1);
    updateRulesList();
}

function validateSafetyChecks() {
    const uncheckedBoxes = Array.from(
        document.querySelectorAll('.safety-checks input[type="checkbox"]:not(:checked)')
    );
    
    if (uncheckedBoxes.length > 0) {
        const missingChecks = uncheckedBoxes
            .map(box => box.parentElement.textContent.trim())
            .join('\n- ');
            
        return {
            valid: false,
            message: `Missing safety checks:\n- ${missingChecks}`
        };
    }
    
    return { valid: true };
}

async function createTask() {
    const description = document.getElementById('taskDescription').value.trim();
    const systemPrompt = document.getElementById('systemPrompt').value.trim();
    
    if (!description) {
        showNotification('Please provide a task description', 'error');
        return;
    }
    
    // Validate safety checks
    const safetyValidation = validateSafetyChecks();
    if (!safetyValidation.valid) {
        const proceed = confirm(
            `Warning: Some safety checks are not complete:\n${safetyValidation.message}\n\nDo you want to proceed anyway?`
        );
        if (!proceed) return;
    }
    
    try {
        const task = await window.electronAPI.createTask({
            description,
            rules: [...defaultRules, ...customRules],
            systemPrompt
        });
        
        showNotification('Task created successfully', 'success');
        closeNewTaskDialog();
        loadTasks();
    } catch (error) {
        showNotification('Error creating task: ' + error.message, 'error');
    }
}

async function loadTasks() {
    if (!currentProject) {
        document.getElementById('activeTasks').innerHTML = '<div class="no-project">No project selected</div>';
        document.getElementById('archivedTasks').innerHTML = '<div class="no-project">No project selected</div>';
        return;
    }

    try {
        const tasks = await window.electronAPI.listTasks();
        
        const activeContainer = document.getElementById('activeTasks');
        const archivedContainer = document.getElementById('archivedTasks');
        
        activeContainer.innerHTML = '';
        archivedContainer.innerHTML = '';

        // Render active tasks
        tasks.active.forEach(task => {
            const container = activeContainer;
            const item = document.createElement('div');
            item.className = 'task-item';
            item.innerHTML = `
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <button class="btn btn-secondary btn-sm" onclick="archiveTask('${task.id}')">
                        Archive
                    </button>
                </div>
                <div class="task-rules">
                    <h4>Rules:</h4>
                    <ul>
                        ${task.rules.map(rule => `
                            <li class="rule-item">
                                <span class="rule-text">${rule}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="task-prompt">
                    <h4>System Prompt:</h4>
                    <div class="prompt-text">${task.systemPrompt}</div>
                </div>
            `;
            container.appendChild(item);
        });

        // Render archived tasks
        tasks.archived.forEach(task => {
            const container = archivedContainer;
            const item = document.createElement('div');
            item.className = 'task-item archived';
            item.innerHTML = `
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <span class="task-status">Archived</span>
                </div>
                <div class="task-rules">
                    <h4>Rules:</h4>
                    <ul>
                        ${task.rules.map(rule => `
                            <li class="rule-item">
                                <span class="rule-text">${rule}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
            container.appendChild(item);
        });
    } catch (error) {
        showNotification('Error loading tasks: ' + error.message, 'error');
    }
}

async function archiveTask(taskId) {
    try {
        await window.electronAPI.archiveTask(taskId);
        showNotification('Task archived successfully', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error archiving task: ' + error.message, 'error');
    }
}

// Project Management
async function selectProject() {
    try {
        const project = await window.electronAPI.selectProject();
        if (project) {
            currentProject = project;
            updateProjectDisplay();
            loadTasks();
            showNotification('Project loaded successfully', 'success');
        }
    } catch (error) {
        showNotification('Error selecting project: ' + error.message, 'error');
    }
}

function updateProjectDisplay() {
    const projectDisplay = document.getElementById('currentProject');
    const projectInfo = document.getElementById('projectInfo');
    
    if (currentProject) {
        projectDisplay.textContent = currentProject.name;
        projectInfo.innerHTML = `
            <div><strong>Name:</strong> ${currentProject.name}</div>
            <div><strong>Path:</strong> ${currentProject.path}</div>
            <div><strong>Config:</strong> ${currentProject.configPath}</div>
        `;
    } else {
        projectDisplay.textContent = 'No Project Selected';
        projectInfo.innerHTML = '<div>No project selected</div>';
    }
}

// Credential Management
async function importFromKeys() {
    try {
        const success = await window.electronAPI.importCredentials('keys');
        if (success) {
            showNotification('Successfully imported credentials from keys.txt', 'success');
            loadCredentialsList();
        } else {
            showNotification('Failed to import credentials from keys.txt', 'error');
        }
    } catch (error) {
        showNotification('Error importing credentials: ' + error.message, 'error');
    }
}

async function importFromVSCode() {
    try {
        const success = await window.electronAPI.importCredentials('vscode');
        if (success) {
            showNotification('Successfully imported credentials from VS Code', 'success');
            loadCredentialsList();
        } else {
            showNotification('Failed to import credentials from VS Code', 'error');
        }
    } catch (error) {
        showNotification('Error importing credentials: ' + error.message, 'error');
    }
}

async function loadCredentialsList() {
    const container = document.getElementById('credentialsList');
    container.innerHTML = '';

    try {
        // Create sections for different credential types
        const sections = {
            'Atlassian': await window.electronAPI.getCredentials('atlassian', 'atlassian'),
            'Digital Ocean': await window.electronAPI.getCredentials('digitalocean', 'digitalocean'),
            'GitHub': await window.electronAPI.getCredentials('github', 'github'),
            'Google': await window.electronAPI.getCredentials('google', 'google')
        };

        for (const [name, creds] of Object.entries(sections)) {
            if (creds) {
                const section = document.createElement('div');
                section.className = 'credential-section';
                section.innerHTML = `
                    <h4>${name}</h4>
                    <div class="credential-details">
                        ${formatCredentialDetails(name, creds.credentials)}
                    </div>
                `;
                container.appendChild(section);
            }
        }

        if (container.children.length === 0) {
            container.innerHTML = '<div class="no-credentials">No credentials imported yet</div>';
        }
    } catch (error) {
        console.error('Error loading credentials:', error);
        container.innerHTML = '<div class="error">Error loading credentials</div>';
    }
}

function formatCredentialDetails(type, creds) {
    const hideValue = (value) => value ? '••••••' : 'Not set';
    
    switch (type) {
        case 'Atlassian':
            return `
                <div>Email: ${creds.email || 'Not set'}</div>
                <div>Domain: ${creds.domain || 'Not set'}</div>
                <div>API Token: ${hideValue(creds.apiToken)}</div>
            `;
        case 'Digital Ocean':
            return `
                <div>API Token: ${hideValue(creds.apiToken)}</div>
                <div>Region: ${creds.region || 'Not set'}</div>
                ${creds.spaces ? `
                    <div>Spaces Access Key: ${hideValue(creds.spaces.accessKey)}</div>
                    <div>Spaces Endpoint: ${creds.spaces.endpoint || 'Not set'}</div>
                ` : ''}
            `;
        case 'GitHub':
            return `
                <div>Username: ${creds.username || 'Not set'}</div>
                <div>Token: ${hideValue(creds.token)}</div>
                ${creds.source ? `<div>Source: ${creds.source}</div>` : ''}
            `;
        case 'Google':
            return `
                <div>Email: ${creds.email || 'Not set'}</div>
                <div>MFA Type: ${creds.mfaType || 'Not set'}</div>
            `;
        default:
            return '<div>No details available</div>';
    }
}

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

    // Load data based on tab
    switch(tabName) {
        case 'tasks':
            loadTasks();
            break;
        case 'credentials':
            loadCredentialsList();
            break;
    }
}

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const messageElement = document.getElementById('notificationMessage');
    
    notification.className = `notification ${type}`;
    messageElement.textContent = message;
    notification.style.display = 'flex';
    
    notification.animate(animations.fadeIn, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });

    setTimeout(() => closeNotification(), 5000);
}

function closeNotification() {
    const notification = document.getElementById('notification');
    notification.animate(animations.fadeOut, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }).onfinish = () => {
        notification.style.display = 'none';
    };
}

// Window Controls
function minimizeWindow() {
    window.electronAPI.minimizeWindow();
}

function closeWindow() {
    window.electronAPI.closeWindow();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Load current project if any
    currentProject = await window.electronAPI.getCurrentProject();
    updateProjectDisplay();
    
    // Initialize UI
    loadTasks();
    loadCredentialsList();
    updateRulesList();
});
