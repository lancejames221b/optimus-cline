class CommandNode {
    constructor(command, timestamp, metadata = {}) {
        this.command = command;
        this.timestamp = timestamp;
        this.metadata = metadata;
        this.children = [];
        this.parent = null;
        this.result = null;
        this.status = 'pending'; // pending, success, error, reverted
    }

    addChild(node) {
        node.parent = this;
        this.children.push(node);
        return node;
    }

    setResult(result) {
        this.result = result;
        this.status = result.success ? 'success' : 'error';
    }

    revert() {
        this.status = 'reverted';
        // Recursively mark all children as reverted
        this.children.forEach(child => child.revert());
    }

    toJSON() {
        return {
            command: this.command,
            timestamp: this.timestamp,
            metadata: this.metadata,
            status: this.status,
            result: this.result,
            children: this.children.map(child => child.toJSON())
        };
    }
}

class CommandHistory {
    constructor() {
        this.root = new CommandNode('root', Date.now());
        this.current = this.root;
        this.branches = new Map(); // name -> node mapping
    }

    execute(command, metadata = {}) {
        const node = new CommandNode(command, Date.now(), metadata);
        this.current.addChild(node);
        this.current = node;
        return node;
    }

    revert(steps = 1) {
        let target = this.current;
        for (let i = 0; i < steps && target.parent; i++) {
            target = target.parent;
        }
        target.revert();
        this.current = target;
        return target;
    }

    branch(name) {
        this.branches.set(name, this.current);
    }

    switchToBranch(name) {
        const node = this.branches.get(name);
        if (node) {
            this.current = node;
            return true;
        }
        return false;
    }

    getHistory(node = this.root, level = 0) {
        const prefix = '  '.repeat(level);
        let result = [];
        
        if (node !== this.root) {
            result.push({
                command: node.command,
                timestamp: node.timestamp,
                status: node.status,
                level: level,
                isCurrent: node === this.current,
                branches: Array.from(this.branches.entries())
                    .filter(([_, n]) => n === node)
                    .map(([name]) => name)
            });
        }
        
        node.children.forEach(child => {
            result = result.concat(this.getHistory(child, level + 1));
        });
        
        return result;
    }

    save() {
        return JSON.stringify(this.root.toJSON());
    }

    load(json) {
        const data = JSON.parse(json);
        this.root = this._reconstructNode(data);
        this.current = this.root;
    }

    _reconstructNode(data) {
        const node = new CommandNode(data.command, data.timestamp, data.metadata);
        node.status = data.status;
        node.result = data.result;
        data.children.forEach(childData => {
            const childNode = this._reconstructNode(childData);
            node.addChild(childNode);
        });
        return node;
    }
}

module.exports = { CommandHistory, CommandNode };
