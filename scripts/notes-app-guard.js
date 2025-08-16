#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Verificar se o arquivo de proteção existe
const protectionFile = path.join(__dirname, '..', '.notes-app-only');

if (!fs.existsSync(protectionFile)) {
    console.error('❌ ERRO: Esta aplicação deve funcionar APENAS como Notes App');
    console.error('❌ Arquivo de proteção não encontrado');
    process.exit(1);
}

console.log('✅ Proteção Notes App ativa - prosseguindo...');
