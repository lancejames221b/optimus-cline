import { Project, TaskParams, TaskList, SetupConfig, ValidationResult } from './app';

interface ElectronAPI {
    // Window controls
    minimizeWindow: () => void;
    closeWindow: () => void;
    
    // Project management
    selectProject: () => Promise<Project | null>;
    getCurrentProject: () => Promise<Project | null>;
    
    // Task management
    createTask: (params: TaskParams) => Promise<{ id: string }>;
    listTasks: () => Promise<TaskList>;
    archiveTask: (taskId: string) => Promise<boolean>;
    openTaskFile: (taskId: string) => Promise<boolean>;
    
    // Credential Management
    getCredentials: (service: string, type: string) => Promise<{ credentials: any } | null>;
    importCredentials: (source: 'keys' | 'vscode') => Promise<boolean>;
    saveKeysFile: (content: string) => Promise<boolean>;
    
    // File Management
    selectKeysFile: () => Promise<string | null>;
    validateKeysFile: (filePath: string) => Promise<ValidationResult>;
    getDefaultKeysPath: () => Promise<string>;
    getKeysTemplate: () => Promise<string>;
    
    // Setup
    completeSetup: (config: SetupConfig) => void;
    
    // Event listeners
    onCommandExecuted: (callback: (command: string, result: any) => void) => void;
    onCostUpdate: (callback: (cost: number) => void) => void;
    onCostLimitReached: (callback: () => void) => void;
    onTaskUpdate: (callback: (task: Task) => void) => void;
    
    // Remove event listeners
    removeCommandListener: () => void;
    removeCostUpdateListener: () => void;
    removeCostLimitListener: () => void;
    removeTaskUpdateListener: () => void;
}

interface Window {
    electronAPI: ElectronAPI;
}

interface NotificationType {
    info: string;
    success: string;
    warning: string;
    error: string;
}

interface AnimationConfig {
    fadeIn: Keyframe[];
    fadeOut: Keyframe[];
}

interface ThemeColors {
    success: string;
    warning: string;
    danger: string;
    getProgressColor: (percentage: number) => string;
}

interface AppState {
    currentCost: number;
    costLimit: number;
    currentProject: Project | null;
    customRules: string[];
    defaultRules: string[];
}

interface CredentialField {
    name: string;
    value: string;
}

interface CredentialSection {
    [key: string]: string;
}
