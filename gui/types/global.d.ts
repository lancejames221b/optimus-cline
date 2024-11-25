declare interface Window {
    electronAPI: {
        // Window controls
        minimizeWindow: () => void;
        closeWindow: () => void;
        
        // Project management
        selectProject: () => Promise<Project | null>;
        getCurrentProject: () => Promise<Project | null>;
        
        // Task management
        createTask: (params: TaskParams) => Promise<Task>;
        listTasks: () => Promise<TaskList>;
        archiveTask: (taskId: string) => Promise<void>;
        updateTaskRules: (params: UpdateRulesParams) => Promise<void>;
        
        // Credential Management
        getCredentials: (service: string, type: string) => Promise<Credential | null>;
        importCredentials: (source: 'keys' | 'vscode') => Promise<boolean>;
        
        // Setup
        selectKeysFile: () => Promise<string | null>;
        validateKeysFile: (filePath: string) => Promise<ValidationResult>;
        getDefaultKeysPath: () => Promise<string>;
        getKeysTemplate: () => Promise<string>;
        completeSetup: (config: SetupConfig) => void;
        
        // Event listeners
        onCommandExecuted: (callback: (command: string) => void) => void;
        onCostUpdate: (callback: (cost: number) => void) => void;
        onCostLimitReached: (callback: () => void) => void;
        onTaskUpdate: (callback: (task: Task) => void) => void;
        
        // Remove event listeners
        removeCommandListener: () => void;
        removeCostUpdateListener: () => void;
        removeCostLimitListener: () => void;
        removeTaskUpdateListener: () => void;
    };
}

interface Project {
    path: string;
    name: string;
    configPath: string;
}

interface Task {
    id: string;
    title: string;
    description: string;
    status: 'active' | 'archived';
    rules: string[];
    systemPrompt: string;
    path: string;
}

interface TaskParams {
    description: string;
    rules?: string[];
    systemPrompt?: string;
}

interface TaskList {
    active: Task[];
    archived: Task[];
}

interface UpdateRulesParams {
    taskId: string;
    rules: string[];
}

interface Credential {
    type: string;
    credentials: any;
    timestamp: number;
}

interface ValidationResult {
    isValid: boolean;
    sections: Record<string, Record<string, string>>;
    error: string | null;
}

interface SetupConfig {
    keysPath: string;
}

interface KeysSection {
    [key: string]: string;
}

interface KeysFile {
    Confluence?: KeysSection;
    DigitalOcean?: KeysSection;
    'DigitalOcean Spaces'?: KeysSection;
    Google?: KeysSection;
    [key: string]: KeysSection | undefined;
}

declare module 'ini' {
    export function parse(str: string): any;
    export function stringify(obj: any, options?: any): string;
}
