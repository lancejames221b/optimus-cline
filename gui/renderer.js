// State management
let currentCost = 0;
let costLimit = 100;
let recentCommands = [];
let activeTasks = new Map();
let currentProject = null;
let isGlobalIntegrations = false;

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

// Project Management
async function selectProject() {
    try {
        const project = await window.electronAPI.selectProject();
        if (project) {
            currentProject = project;
            updateProjectDisplay();
            loadIntegrationStatus();
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

// Integration Management
function toggleIntegrationScope() {
    isGlobalIntegrations = document.getElementById('globalIntegrations').checked;
    const scopeHint = document.getElementById('scopeHint');
    scopeHint.textContent = isGlobalIntegrations ? 
        'Using global integrations' : 
        'Using project-specific integrations';
    
    loadIntegrationStatus();
}

async function configureAtlassian() {
    if (!currentProject && !isGlobalIntegrations) {
        showNotification('Please select a project or use global integrations', 'error');
        return;
    }

    const domain = document.getElementById('atlassianDomain').value;
    const email = document.getElementById('atlassianEmail').value;
    const apiToken = document.getElementById('atlassianToken').value;
    const products = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    if (!domain || !email || !apiToken) {
        showNotification('Please fill in all Atlassian fields', 'error');
        return;
    }

    try {
        const success = await window.electronAPI.configureAtlassian({
            domain,
            email,
            apiToken,
            products
        }, isGlobalIntegrations);

        if (success) {
            showNotification('Atlassian integration configured successfully', 'success');
            loadIntegrationStatus();
        } else {
            showNotification('Failed to configure Atlassian integration', 'error');
        }
    } catch (error) {
        showNotification('Error configuring Atlassian integration: ' + error.message, 'error');
    }
}

async function configureDigitalOcean() {
    if (!currentProject && !isGlobalIntegrations) {
        showNotification('Please select a project or use global integrations', 'error');
        return;
    }

    const apiKey = document.getElementById('doApiKey').value;
    const spacesKey = document.getElementById('doSpacesKey').value;
    const spacesSecret = document.getElementById('doSpacesSecret').value;

    if (!apiKey) {
        showNotification('API Key is required', 'error');
        return;
    }

    try {
        const success = await window.electronAPI.configureDigitalOcean({
            apiKey,
            spacesKey,
            spacesSecret
        }, isGlobalIntegrations);

        if (success) {
            showNotification('Digital Ocean integration configured successfully', 'success');
            loadIntegrationStatus();
        } else {
            showNotification('Failed to configure Digital Ocean integration', 'error');
        }
    } catch (error) {
        showNotification('Error configuring Digital Ocean integration: ' + error.message, 'error');
    }
}

async function importSSHConfig() {
    if (!currentProject && !isGlobalIntegrations) {
        showNotification('Please select a project or use global integrations', 'error');
        return;
    }

    try {
        const success = await window.electronAPI.importSSHConfig(isGlobalIntegrations);
        if (success) {
            showNotification('SSH configurations imported successfully', 'success');
            loadSSHConfigs();
        } else {
            showNotification('Failed to import SSH configurations', 'error');
        }
    } catch (error) {
        showNotification('Error importing SSH configurations: ' + error.message, 'error');
    }
}

async function loadIntegrationStatus() {
    try {
        // Load Atlassian status
        const atlassianCreds = await window.electronAPI.getCredentials(
            'atlassian', 
            'atlassian', 
            isGlobalIntegrations
        );
        
        if (atlassianCreds) {
            document.getElementById('atlassianDomain').value = atlassianCreds.credentials.domain;
            document.getElementById('atlassianEmail').value = atlassianCreds.credentials.email;
            // Don't populate the API token for security
            atlassianCreds.credentials.products.forEach(product => {
                const checkbox = document.querySelector(`input[value="${product}"]`);
                if (checkbox) checkbox.checked = true;
            });
        } else {
            // Clear form if no credentials found
            document.getElementById('atlassianDomain').value = '';
            document.getElementById('atlassianEmail').value = '';
            document.getElementById('atlassianToken').value = '';
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
        }

        // Load Digital Ocean status
        const doCreds = await window.electronAPI.getCredentials(
            'digitalocean', 
            'digitalocean', 
            isGlobalIntegrations
        );
        
        if (doCreds) {
            document.getElementById('doSpacesKey').value = doCreds.credentials.spaces?.key || '';
            // Don't populate sensitive fields for security
        } else {
            // Clear form if no credentials found
            document.getElementById('doApiKey').value = '';
            document.getElementById('doSpacesKey').value = '';
            document.getElementById('doSpacesSecret').value = '';
        }

        // Load SSH configs
        loadSSHConfigs();
    } catch (error) {
        showNotification('Error loading integration status: ' + error.message, 'error');
    }
}

async function loadSSHConfigs() {
    try {
        const configs = await window.electronAPI.getCredentials('ssh', 'ssh', isGlobalIntegrations);
        const container = document.getElementById('sshConfigs');
        container.innerHTML = '';

        if (configs) {
            Object.entries(configs.credentials).forEach(([host, config]) => {
                const item = document.createElement('div');
                item.className = 'ssh-config-item';
                item.innerHTML = `
                    <div class="ssh-config-header">
                        <span class="ssh-host">${host}</span>
                        <button class="btn btn-secondary btn-sm" onclick="testSSHConnection('${host}')">
                            Test Connection
                        </button>
                    </div>
                    <div class="ssh-config-details">
                        <div>User: ${config.user || 'default'}</div>
                        <div>Host: ${config.hostname || host}</div>
                        ${config.port ? `<div>Port: ${config.port}</div>` : ''}
                    </div>
                `;
                container.appendChild(item);
            });
        }
    } catch (error) {
        showNotification('Error loading SSH configurations: ' + error.message, 'error');
    }
}

// Task Management
async function createNewTask() {
    if (!currentProject) {
        showNotification('Please select a project first', 'error');
        return;
    }

    const description = prompt('Enter task description:');
    if (description) {
        try {
            const taskId = await window.electronAPI.createTask(description);
            showNotification('Task created successfully', 'success');
            loadTasks();
        } catch (error) {
            showNotification('Error creating task: ' + error.message, 'error');
        }
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

        tasks.forEach(task => {
            const container = task.status === 'archived' ? archivedContainer : activeContainer;
            const item = document.createElement('div');
            item.className = 'task-item';
            item.innerHTML = `
                <div class="task-header">
                    <span class="task-id">${task.id}</span>
                    <span class="task-status">${task.status}</span>
                </div>
                <div class="task-description">${task.description}</div>
                ${task.status !== 'archived' ? `
                    <button class="btn btn-secondary btn-sm" onclick="archiveTask('${task.id}')">
                        Archive
                    </button>
                ` : ''}
            `;
            container.appendChild(item);
        });
    } catch (error) {
        showNotification('Error loading tasks: ' + error.message, 'error');
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
        case 'integrations':
            loadIntegrationStatus();
            break;
        case 'tasks':
            loadTasks();
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
    updateCostDisplay();
    
    // Set up event listeners
    window.electronAPI.onCostUpdate((event, cost) => {
        currentCost = cost;
        updateCostDisplay();
    });

    window.electronAPI.onCostLimitReached(() => {
        showNotification('Cost limit reached!', 'warning');
    });

    window.electronAPI.onTaskUpdate((event, data) => {
        activeTasks.set(data.id, data);
        loadTasks();
    });
});

// Cost Management
function updateCostDisplay() {
    const costDisplay = document.getElementById('currentCost');
    const costLimitDisplay = document.getElementById('costLimitDisplay');
    const costProgress = document.getElementById('costProgress');
    
    const percentage = (currentCost / costLimit) * 100;
    costDisplay.textContent = currentCost.toFixed(2);
    costLimitDisplay.textContent = costLimit.toFixed(2);
    
    costProgress.style.width = `${percentage}%`;
    costProgress.style.backgroundColor = colors.getProgressColor(percentage);
}

async function setCostLimit() {
    const input = document.getElementById('costLimit');
    const limit = parseFloat(input.value);
    
    if (isNaN(limit) || limit <= 0) {
        showNotification('Please enter a valid cost limit', 'error');
        return;
    }
    
    try {
        await window.electronAPI.setCostLimit(limit);
        costLimit = limit;
        updateCostDisplay();
        showNotification('Cost limit updated successfully', 'success');
    } catch (error) {
        showNotification('Error updating cost limit: ' + error.message, 'error');
    }
}
