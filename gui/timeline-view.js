class TimelineView {
    constructor(container) {
        this.container = container;
        this.timeline = document.createElement('div');
        this.timeline.className = 'timeline-container';
        this.container.appendChild(this.timeline);
        
        this.addStyles();
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .timeline-container {
                position: relative;
                padding: 20px;
                margin: 20px 0;
                background: var(--card-bg);
                border-radius: 8px;
            }

            .timeline-line {
                position: absolute;
                left: 50%;
                top: 0;
                bottom: 0;
                width: 2px;
                background: var(--accent);
                transform: translateX(-50%);
            }

            .timeline-node {
                position: relative;
                margin: 20px 0;
                display: flex;
                align-items: center;
                gap: 20px;
            }

            .timeline-node::before {
                content: '';
                position: absolute;
                left: 50%;
                width: 12px;
                height: 12px;
                background: var(--accent);
                border-radius: 50%;
                transform: translateX(-50%);
                transition: all 0.3s ease;
            }

            .timeline-node.checkpoint::before {
                background: var(--success);
                width: 16px;
                height: 16px;
                border: 2px solid var(--text);
            }

            .timeline-node.current::before {
                background: var(--text);
                box-shadow: 0 0 0 4px rgba(246, 177, 122, 0.3);
            }

            .timeline-content {
                flex: 1;
                padding: 15px;
                background: var(--secondary);
                border-radius: 8px;
                margin-left: 50%;
                transform: translateX(20px);
                transition: all 0.3s ease;
            }

            .timeline-content:hover {
                transform: translateX(20px) translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }

            .timeline-command {
                font-family: 'SF Mono', monospace;
                margin-bottom: 8px;
            }

            .timeline-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.9em;
                color: var(--text);
                opacity: 0.8;
            }

            .timeline-actions {
                display: flex;
                gap: 8px;
                margin-top: 10px;
            }

            .timeline-branch {
                position: absolute;
                left: 0;
                width: calc(50% - 1px);
                padding: 10px;
                background: var(--primary);
                border-radius: 6px;
                transform: translateX(-10px);
            }

            .timeline-branch::after {
                content: '';
                position: absolute;
                right: -10px;
                top: 50%;
                width: 10px;
                height: 2px;
                background: var(--accent);
                transform: translateY(-50%);
            }

            .checkpoint-label {
                position: absolute;
                left: 52%;
                top: 50%;
                transform: translateY(-50%);
                background: var(--success);
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                white-space: nowrap;
            }

            .timeline-notes {
                font-style: italic;
                margin-top: 5px;
                color: var(--text);
                opacity: 0.7;
            }
        `;
        document.head.appendChild(style);
    }

    render(history) {
        this.timeline.innerHTML = `
            <div class="timeline-line"></div>
            ${this.renderNodes(history)}
        `;
    }

    renderNodes(history) {
        return history.map(entry => `
            <div class="timeline-node ${entry.isCurrent ? 'current' : ''} ${entry.branches.length ? 'checkpoint' : ''}">
                ${entry.branches.length ? `
                    <div class="checkpoint-label">
                        ${entry.branches.join(', ')}
                    </div>
                ` : ''}
                
                <div class="timeline-content">
                    <div class="timeline-command">${entry.command}</div>
                    <div class="timeline-meta">
                        <span>${new Date(entry.timestamp).toLocaleTimeString()}</span>
                        <span class="status ${entry.status}">${entry.status}</span>
                    </div>
                    ${entry.metadata?.notes ? `
                        <div class="timeline-notes">${entry.metadata.notes}</div>
                    ` : ''}
                    <div class="timeline-actions">
                        <button class="btn btn-warning btn-sm" onclick="revertTo('${entry.timestamp}')">
                            Revert Here
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="branchFrom('${entry.timestamp}')">
                            Branch
                        </button>
                        ${!entry.branches.length ? `
                            <button class="btn btn-success btn-sm" onclick="createCheckpointAt('${entry.timestamp}')">
                                Create Checkpoint
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }
}

// Add to renderer.js
let timelineView;

document.addEventListener('DOMContentLoaded', () => {
    const historyContent = document.getElementById('history');
    timelineView = new TimelineView(historyContent);
    
    // Update visualizeHistory function
    const originalVisualizeHistory = visualizeHistory;
    visualizeHistory = function() {
        const history = commandHistory.getHistory();
        timelineView.render(history);
        originalVisualizeHistory();
    };
});

function createCheckpointAt(timestamp) {
    const name = prompt('Enter checkpoint name:');
    const notes = prompt('Enter checkpoint notes (optional):');
    
    if (name) {
        const steps = getStepsToTimestamp(timestamp);
        if (steps > 0) {
            commandHistory.revert(steps);
            commandHistory.branch(name);
            if (notes) {
                commandHistory.current.metadata.notes = notes;
            }
            visualizeHistory();
            showNotification(`Created checkpoint: ${name}`);
        }
    }
}
