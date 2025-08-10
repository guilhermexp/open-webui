#!/usr/bin/env node

import { spawn, execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Find available port
function findAvailablePort() {
    const ports = [8080, 8081, 8082, 8083, 8084];
    for (const port of ports) {
        try {
            execSync(`lsof -i :${port}`, { stdio: 'ignore' });
        } catch {
            return port;
        }
    }
    return 8080;
}

const BACKEND_PORT = findAvailablePort();
console.log(`Starting Open WebUI Development Environment`);
console.log(`Backend port: ${BACKEND_PORT}`);
console.log(`Frontend port: 5173`);

// Set environment variables
process.env.BACKEND_PORT = BACKEND_PORT;

// Start backend
console.log('Starting backend...');
const backend = spawn('bash', ['./dev.sh'], {
    cwd: join(__dirname, 'backend'),
    env: { ...process.env, BACKEND_PORT },
    stdio: 'inherit'
});

// Wait a bit for backend to start
setTimeout(() => {
    console.log('Starting frontend...');
    
    // Start frontend
    const frontend = spawn('npm', ['run', 'dev:frontend'], {
        cwd: __dirname,
        env: { ...process.env, BACKEND_PORT },
        stdio: 'inherit'
    });
    
    // Handle exit
    process.on('SIGINT', () => {
        console.log('\nShutting down...');
        backend.kill();
        frontend.kill();
        process.exit();
    });
    
    frontend.on('exit', () => {
        backend.kill();
        process.exit();
    });
    
}, 3000);