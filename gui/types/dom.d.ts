interface HTMLInputElement extends HTMLElement {
    value: string;
    checked: boolean;
}

interface HTMLTextAreaElement extends HTMLElement {
    value: string;
}

interface HTMLDialogElement extends HTMLElement {
    showModal(): void;
    close(): void;
}

// Custom element types
interface CustomElements extends HTMLElementTagNameMap {
    'dialog': HTMLDialogElement;
}

// Extend the existing ElementTagNameMap
interface HTMLElementTagNameMap {
    'input': HTMLInputElement;
    'textarea': HTMLTextAreaElement;
    'dialog': HTMLDialogElement;
}

// Type guard functions
function isHTMLInputElement(element: HTMLElement | null): element is HTMLInputElement {
    return element !== null && element instanceof HTMLInputElement;
}

function isHTMLTextAreaElement(element: HTMLElement | null): element is HTMLTextAreaElement {
    return element !== null && element instanceof HTMLTextAreaElement;
}

// Error types
interface AppError extends Error {
    code?: string;
    details?: any;
}

// UI Event types
interface UIEvent {
    target: HTMLElement;
}

// Custom Events
interface TaskUpdateEvent {
    id: string;
    content: string;
}

interface CommandExecutedEvent {
    command: string;
    output: string;
}

interface CostUpdateEvent {
    cost: number;
    limit: number;
}

// DOM Utility Types
type ElementId = string;
type QuerySelector = string;

interface DOMUtils {
    getElement<T extends HTMLElement>(id: ElementId): T | null;
    querySelector<T extends HTMLElement>(selector: QuerySelector): T | null;
    querySelectorAll<T extends HTMLElement>(selector: QuerySelector): NodeListOf<T>;
    createElement<K extends keyof HTMLElementTagNameMap>(tagName: K): HTMLElementTagNameMap[K];
}

// Event Handler Types
type EventHandler<T = any> = (event: T) => void;
type ErrorHandler = (error: AppError) => void;

// UI Component Types
interface UIComponent {
    render(): void;
    update(data: any): void;
    destroy(): void;
}

// Notification Types
type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface NotificationOptions {
    message: string;
    type: NotificationType;
    duration?: number;
}

// Form Types
interface FormData {
    [key: string]: string | boolean | string[];
}

interface FormValidation {
    isValid: boolean;
    errors: { [key: string]: string };
}
