export interface Project {
    name: string;
    path: string;
    configPath: string;
}

export interface StoreSchema {
    firstRun: boolean;
    keysPath: string;
    costLimit: number;
    totalCost: number;
    currentProject: Project | null;
    theme: string;
}

export interface SetupConfig {
    keysPath?: string;
}

export interface ParsedKeysFile {
    [section: string]: {
        [key: string]: string;
    };
}

export interface ValidationResult {
    isValid: boolean;
    sections: ParsedKeysFile;
    error: string | null;
}

export interface TaskParams {
    description: string;
    rules: string[];
    systemPrompt: string;
}

export interface Task {
    id: string;
    title: string;
    rules: string[];
    systemPrompt: string;
    status: 'active' | 'archived';
    created: string;
}

export interface TaskList {
    active: Task[];
    archived: Task[];
}
