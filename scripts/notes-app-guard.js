#!/usr/bin/env node

/**
 * NOTES APP PROTECTION GUARD
 * Este script garante que apenas a versão de notas seja executada
 * Bloqueia qualquer tentativa de executar a versão completa do Open WebUI
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');
const protectionFile = path.join(rootDir, '.notes-app-only');

function checkProtection() {
    // Verifica se o arquivo de proteção existe
    if (!fs.existsSync(protectionFile)) {
        console.error('❌ ERRO: Arquivo de proteção .notes-app-only não encontrado');
        console.error('❌ Esta aplicação deve funcionar APENAS como Notes App');
        process.exit(1);
    }

    // Verifica se não há Dockerfile (proteção contra build Docker completo)
    const dockerfile = path.join(rootDir, 'Dockerfile');
    if (fs.existsSync(dockerfile)) {
        console.error('❌ ERRO: Dockerfile detectado - removendo para proteger contra execução completa');
        fs.unlinkSync(dockerfile);
    }

    // Verifica se não há docker-compose.yml
    const dockerCompose = path.join(rootDir, 'docker-compose.yml');
    if (fs.existsSync(dockerCompose)) {
        console.error('❌ ERRO: docker-compose.yml detectado - removendo para proteger contra execução completa');
        fs.unlinkSync(dockerCompose);
    }

    // Verifica package.json
    const packageJsonPath = path.join(rootDir, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    if (packageJson.name !== 'notes-app') {
        console.error('❌ ERRO: package.json não está configurado como notes-app');
        process.exit(1);
    }

    // Bloqueia scripts perigosos
    const dangerousScripts = ['build', 'preview', 'docker:build', 'docker:run'];
    for (const script of dangerousScripts) {
        if (packageJson.scripts && packageJson.scripts[script] && !packageJson.scripts[script].includes('_unused')) {
            console.error(`❌ ERRO: Script perigoso detectado: ${script}`);
            process.exit(1);
        }
    }

    console.log('✅ Proteção Notes App ativa - apenas versão de notas autorizada');
    return true;
}

// Executa verificação
checkProtection();