const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const Store = require('electron-store');
const WebSocket = require('ws');
const fs = require('fs').promises;
const keytar = require('keytar');
const os = require('os');
const store = new Store();

let mainWindow;
let vscodeWs;
const costPerCommand = 0.01;
let totalCost = store.get('totalCost') || 0;
let costLimit = store.get('costLimit') || 100;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 400,
        height: 600,
        x: 50,
        y: 50,
        frame: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        alwaysOnTop: true,
        resizable: true,
        transparent: true,
        hasShadow: true
    });

    mainWindow.loadFile('index.html');
}

// VSCode WebSocket connection
function connectToVSCode() {
    vscodeWs = new WebSocket('ws://localhost:54321');

    vscodeWs.on('message', (data) => {
        const message = JSON.parse(data);

        switch(message.type) {
            case 'commandExecuted':
                updateCost(costPerCommand);
                mainWindow.webContents.send('command-executed', message.command);
                break;
        }
    });
}

// Cost management
function updateCost(amount) {
    totalCost += amount;
    store.set('totalCost', totalCost);

    mainWindow.webContents.send('cost-update', totalCost);

    if (totalCost >= costLimit) {
        mainWindow.webContents.send('cost-limit-reached');
        if (vscodeWs) {
            vscodeWs.send(JSON.stringify({
                type: 'setAutoRun',
                value: false
            }));
        }
    }
}

// IPC Handlers
ipcMain.handle('executeCommand', async (event, command) => {
    const { exec } = require('child_process');
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else {
                updateCost(costPerCommand);
                resolve({ stdout, stderr });
            }
        });
    });
});

ipcMain.handle('setCostLimit', (event, limit) => {
    costLimit = limit;
    store.set('costLimit', limit);
});

ipcMain.on('minimize-window', () => {
    mainWindow.minimize();
});

ipcMain.on('close-window', () => {
    mainWindow.close();
});

// App lifecycle
app.whenReady().then(() => {
    createWindow();
    connectToVSCode();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Cleanup
app.on('before-quit', () => {
    if (vscodeWs) {
        vscodeWs.close();
    }
});
