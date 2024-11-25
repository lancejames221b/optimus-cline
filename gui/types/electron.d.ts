declare namespace Electron {
    interface BrowserWindow {
        loadFile(filePath: string): Promise<void>;
        webContents: WebContents;
        minimize(): void;
        close(): void;
        show(): void;
    }

    interface WebContents {
        send(channel: string, ...args: any[]): void;
        openDevTools(): void;
    }

    interface IpcMain {
        handle(channel: string, listener: (event: IpcMainEvent, ...args: any[]) => Promise<any> | any): void;
        on(channel: string, listener: (event: IpcMainEvent, ...args: any[]) => void): void;
        once(channel: string, listener: (event: IpcMainEvent, ...args: any[]) => void): void;
    }

    interface IpcMainEvent {
        reply(channel: string, ...args: any[]): void;
    }

    interface Dialog {
        showOpenDialog(window: BrowserWindow, options: OpenDialogOptions): Promise<OpenDialogReturnValue>;
    }

    interface OpenDialogOptions {
        properties: Array<'openFile' | 'openDirectory' | 'multiSelections' | 'showHiddenFiles'>;
        filters?: Array<{
            name: string;
            extensions: string[];
        }>;
        message?: string;
    }

    interface OpenDialogReturnValue {
        canceled: boolean;
        filePaths: string[];
    }

    interface App {
        whenReady(): Promise<void>;
        on(event: string, listener: (...args: any[]) => void): void;
        quit(): void;
    }
}

declare module 'electron' {
    const BrowserWindow: {
        new(options: any): Electron.BrowserWindow;
        getAllWindows(): Electron.BrowserWindow[];
    };
    const ipcMain: Electron.IpcMain;
    const app: Electron.App;
    const dialog: Electron.Dialog;
    export { BrowserWindow, ipcMain, app, dialog };
}

declare module 'electron-store' {
    class Store<T = any> {
        constructor(options?: {
            defaults?: Partial<T>;
            name?: string;
            cwd?: string;
            encryptionKey?: string | Buffer;
            fileExtension?: string;
            clearInvalidConfig?: boolean;
            serialize?: (value: T) => string;
            deserialize?: (value: string) => T;
        });

        get<K extends keyof T>(key: K): T[K];
        set<K extends keyof T>(key: K, value: T[K]): void;
        set(object: Partial<T>): void;
        has(key: keyof T): boolean;
        reset(...keys: Array<keyof T>): void;
        delete(key: keyof T): void;
        clear(): void;
        openInEditor(): void;
        size: number;
        path: string;
        store: T;
    }

    export = Store;
}

declare module 'keytar' {
    export function getPassword(service: string, account: string): Promise<string | null>;
    export function setPassword(service: string, account: string, password: string): Promise<void>;
    export function deletePassword(service: string, account: string): Promise<boolean>;
    export function findPassword(service: string): Promise<string | null>;
    export function findCredentials(service: string): Promise<Array<{ account: string; password: string; }>>;
}
