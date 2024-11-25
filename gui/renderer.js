// @ts-check

/** @type {import('./types/app').Project | null} */
let currentProject = null;

/** @type {string[]} */
let customRules = [];

/** @type {Array<{name: string, value: string}>} */
let credentialFields = [];

/** @type {string[]} */
const defaultRules = [
    "Don't delete production systems",
    "Always backup before making changes",
    "Verify changes in staging first",
    "Follow security protocols",
    "Document all changes"
];

const colors = {
    success: '#4CAF50',
    warning: '#FFC107',
    danger: '#F44336',
    /**
     * @param {number} percentage
     * @returns {string}
     */
    getProgressColor: (percentage) => {
        if (percentage < 60) return colors.success;
        if (percentage < 80) return colors.warning;
        return colors.danger;
    }
};

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

// Credential Management
function showNewCredentialDialog() {
    const dialog = document.getElementById('newCredentialDialog');
    if (!dialog) return;
    dialog.style.display = 'flex';
    
    // Reset form
    const serviceInput = /** @type {HTMLInputElement} */ (document.getElementById('credentialService'));
    const nameInput = /** @type {HTMLInputElement} */ (document.getElementById('newFieldName'));
    const valueInput = /** @type {HTMLInputElement} */ (document.getElementById('newFieldValue'));
    
    if (serviceInput) serviceInput.value = '';
    if (nameInput) nameInput.value = '';
    if (valueInput) valueInput.value = '';
    credentialFields = [];
    updateCredentialFieldsList();
}

function closeNewCredentialDialog() {
    const dialog = document.getElementById('newCredentialDialog');
    if (!dialog) return;
    dialog.style.display = 'none';
}

function updateCredentialFieldsList() {
    const fieldsList = document.querySelector('.credential-field-list');
    if (!fieldsList) return;
    
    fieldsList.innerHTML = credentialFields.map((field, index) => `
        <div class="credential-field">
            <div class="field-name">${field.name}</div>
            <div class="field-value">••••••</div>
            <button class="btn btn-danger btn-sm" onclick="removeCredentialField(${index})">×</button>
        </div>
    `).join('');
}

function addCredentialField() {
    const nameInput = /** @type {HTMLInputElement} */ (document.getElementById('newFieldName'));
    const valueInput = /** @type {HTMLInputElement} */ (document.getElementById('newFieldValue'));
    
    if (!nameInput || !valueInput) return;
    
    const name = nameInput.value.trim().toUpperCase();
    const value = valueInput.value.trim();
    
    if (name && value) {
        credentialFields.push({ name, value });
        nameInput.value = '';
        valueInput.value = '';
        updateCredentialFieldsList();
    }
}

/**
 * @param {number} index
 */
function removeCredentialField(index) {
    credentialFields.splice(index, 1);
    updateCredentialFieldsList();
}

async function saveCredential() {
    const serviceInput = /** @type {HTMLInputElement} */ (document.getElementById('credentialService'));
    if (!serviceInput) return;
    
    const service = serviceInput.value.trim();
    if (!service) {
        showNotification('Please enter a service name', 'warning');
        return;
    }
    
    if (credentialFields.length === 0) {
        showNotification('Please add at least one credential field', 'warning');
        return;
    }
    
    try {
        // Get existing keys.txt content
        const template = await window.electronAPI.getKeysTemplate();
        const sections = template.split('\n\n');
        
        // Create the new section content
        const newSection = `[${service}]\n${credentialFields.map(field => 
            `${field.name}=${field.value}`
        ).join('\n')}`;
        
        // Find the section for this service
        const sectionStart = `[${service}]`;
        let sectionIndex = sections.findIndex(s => s.includes(sectionStart));
        
        if (sectionIndex === -1) {
            // Add new section
            sections.push(newSection);
        } else {
            // Update existing section
            sections[sectionIndex] = newSection;
        }
        
        // Save the updated content
        await window.electronAPI.saveKeysFile(sections.join('\n\n'));
        
        showNotification('Credential saved successfully', 'success');
        closeNewCredentialDialog();
        loadCredentialsList();
    } catch (error) {
        showNotification(`Error saving credential: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
}

async function selectKeysFile() {
    try {
        const filePath = await window.electronAPI.selectKeysFile();
        if (filePath) {
            showNotification('Keys file selected successfully', 'success');
            loadCredentialsList();
        }
    } catch (error) {
        showNotification(`Error selecting keys file: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
}

async function loadCredentialsList() {
    const container = document.getElementById('credentialsList');
    if (!container) return;
    
    container.innerHTML = '';

    try {
        // Get template to parse sections
        const template = await window.electronAPI.getKeysTemplate();
        const sections = template.split('\n\n');
        
        // Extract service names
        const services = sections
            .map(section => {
                const match = section.match(/^\[(.*?)\]/);
                return match ? match[1] : null;
            })
            .filter((name): name is string => name !== null);
        
        // Load credentials for each service
        for (const service of services) {
            const creds = await window.electronAPI.getCredentials(service, service);
            if (creds) {
                const section = document.createElement('div');
                section.className = 'credential-section';
                section.innerHTML = `
                    <h4>${service}</h4>
                    <div class="credential-details">
                        ${Object.entries(creds.credentials).map(([key, value]) => `
                            <div>${key}: ${typeof value === 'string' ? '••••••' : 'Not set'}</div>
                        `).join('')}
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

// Task Management
async function showNewTaskDialog() {
    if (!currentProject) {
        showNotification('Please select a project first', 'warning');
        return;
    }

    const dialog = document.getElementById('newTaskDialog');
    if (!dialog) return;
    dialog.style.display = 'flex';
    
    // Reset form
    const descInput = /** @type {HTMLInputElement} */ (document.getElementById('taskDescription'));
    const promptInput = /** @type {HTMLTextAreaElement} */ (document.getElementById('systemPrompt'));
    const ruleInput = /** @type {HTMLInputElement} */ (document.getElementById('newRule'));
    
    if (descInput) descInput.value = '';
    if (promptInput) promptInput.value = '';
    if (ruleInput) ruleInput.value = '';
    customRules = [];
    
    // Reset safety checks
    document.querySelectorAll('.safety-checks input[type="checkbox"]')
        .forEach(checkbox => {
            if (checkbox instanceof HTMLInputElement) {
                checkbox.checked = false;
            }
        });
    
    // Load default rules
    updateRulesList();
}

function closeNewTaskDialog() {
    const dialog = document.getElementById('newTaskDialog');
    if (dialog) dialog.style.display = 'none';
}

function updateRulesList() {
    // Update default rules
    const defaultRulesList = document.getElementById('defaultRules');
    if (defaultRulesList) {
        defaultRulesList.innerHTML = defaultRules.map(rule => `
            <div class="rule-item">
                <span class="rule-text">${rule}</span>
            </div>
        `).join('');
    }
    
    // Update custom rules
    const customRulesList = document.getElementById('customRules');
    if (customRulesList) {
        customRulesList.innerHTML = customRules.map((rule, index) => `
            <div class="rule-item">
                <span class="rule-text">${rule}</span>
                <button class="btn btn-danger btn-sm" onclick="removeCustomRule(${index})">×</button>
            </div>
        `).join('');
    }
}

function addTaskRule() {
    const input = /** @type {HTMLInputElement} */ (document.getElementById('newRule'));
    if (!input) return;
    
    const rule = input.value.trim();
    if (rule) {
        customRules.push(rule);
        input.value = '';
        updateRulesList();
    }
}

/**
 * @param {number} index
 */
function removeCustomRule(index) {
    customRules.splice(index, 1);
    updateRulesList();
}

/**
 * @returns {{ valid: boolean; message?: string }}
 */
function validateSafetyChecks() {
    const uncheckedBoxes = Array.from(
        document.querySelectorAll('.safety-checks input[type="checkbox"]:not(:checked)')
    ).filter((el) => el instanceof HTMLInputElement);
    
    if (uncheckedBoxes.length > 0) {
        const missingChecks = uncheckedBoxes
            .map(box => box.parentElement?.textContent?.trim() || '')
            .filter(text => text)
            .join('\n- ');
            
        return {
            valid: false,
            message: `Missing safety checks:\n- ${missingChecks}`
        };
    }
    
    return { valid: true };
}

async function createTask() {
    if (!currentProject) {
        showNotification('Please select a project first', 'warning');
        return;
    }

    const descInput = /** @type {HTMLInputElement} */ (document.getElementById('taskDescription'));
    const promptInput = /** @type {HTMLTextAreaElement} */ (document.getElementById('systemPrompt'));
    
    if (!descInput || !promptInput) {
        showNotification('Error: Form elements not found', 'error');
        return;
    }

    const description = descInput.value.trim();
    const systemPrompt = promptInput.value.trim();
    
    if (!description) {
        showNotification('Please provide a task description', 'error');
        return;
    }
    
    // Validate safety checks
    const safetyValidation = validateSafetyChecks();
    if (!safetyValidation.valid && safetyValidation.message) {
        const proceed = confirm(
            `Warning: Some safety checks are not complete:\n${safetyValidation.message}\n\nDo you want to proceed anyway?`
        );
        if (!proceed) return;
    }
    
    try {
        await window.electronAPI.createTask({
            description,
            rules: [...defaultRules, ...customRules],
            systemPrompt
        });
        
        showNotification('Task created successfully', 'success');
        closeNewTaskDialog();
        loadTasks();
    } catch (error) {
        showNotification(`Error creating task: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
}

async function loadTasks() {
    const activeContainer = document.getElementById('activeTasks');
    const archivedContainer = document.getElementById('archivedTasks');
    
    if (!activeContainer || !archivedContainer) return;

    if (!currentProject) {
        activeContainer.innerHTML = '<div class="no-project">No project selected</div>';
        archivedContainer.innerHTML = '<div class="no-project">No project selected</div>';
        return;
    }

    try {
        const tasks = await window.electronAPI.listTasks();
        
        activeContainer.innerHTML = '';
        archivedContainer.innerHTML = '';

        // Render active tasks
        tasks.active.forEach(task => {
            const item = document.createElement('div');
            item.className = 'task-item';
            item.innerHTML = `
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <div class="task-actions">
                        <button class="btn btn-primary btn-sm" onclick="openTask('${task.id}')">
                            Open
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="archiveTask('${task.id}')">
                            Archive
                        </button>
                    </div>
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
            activeContainer.appendChild(item);
        });

        // Render archived tasks
        tasks.archived.forEach(task => {
            const item = document.createElement('div');
            item.className = 'task-item archived';
            item.innerHTML = `
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <div class="task-actions">
                        <button class="btn btn-primary btn-sm" onclick="openTask('${task.id}')">
                            Open
                        </button>
                        <span class="task-status">Archived</span>
                    </div>
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
            archivedContainer.appendChild(item);
        });
    } catch (error) {
        showNotification(`Error loading tasks: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
}

/**
 * Opens a task in VS Code or default text editor
 * @param {string} taskId
 */
async function openTask(taskId) {
    try {
        await window.electronAPI.openTaskFile(taskId);
        showNotification('Opening task...', 'info');
    } catch (error) {
        showNotification(`Error opening task: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
}

/**
 * @param {string} taskId
 */
async function archiveTask(taskId) {
    try {
        await window.electronAPI.archiveTask(taskId);
        showNotification('Task archived successfully', 'success');
        loadTasks();
    } catch (error) {
        showNotification(`Error archiving task: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
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
        showNotification(`Error selecting project: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
}

function updateProjectDisplay() {
    const projectDisplay = document.getElementById('currentProject');
    const projectInfo = document.getElementById('projectInfo');
    
    if (!projectDisplay || !projectInfo) return;
    
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

// UI Functions
/**
 * @param {string} tabName
 */
function showTab(tabName) {
    document.querySelectorAll('.content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    const content = document.getElementById(tabName);
    const tab = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    
    if (!content || !tab) return;
    
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
/**
 * @param {string} message
 * @param {'info' | 'success' | 'warning' | 'error'} type
 */
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const messageElement = document.getElementById('notificationMessage');
    
    if (!notification || !messageElement) return;
    
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
    if (!notification) return;
    
    notification.animate(animations.fadeOut, {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }).onfinish = () => {
        if (notification) notification.style.display = 'none';
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
