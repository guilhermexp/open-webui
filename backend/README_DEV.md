# 🚀 Desenvolvimento do Open WebUI

## Configuração Padrão

### Portas
- **Frontend**: `5173` (Vite)
- **Backend**: `8083` (FastAPI)

### Comando de Desenvolvimento
```bash
npm run dev
```

Este comando inicia:
- Frontend (Vite) na porta 5173
- Backend (FastAPI) na porta 8083 usando `dev.sh`

### Scripts de Desenvolvimento

#### `dev.sh` (Backend)
- Porta: `8083`
- Ativa ambiente virtual
- Configura CORS para `http://localhost:5173`
- Ativa autenticação obrigatória
- Recarregamento automático habilitado

#### `vite.config.ts` (Frontend)
- Proxy configurado para redirecionar `/api` → `http://localhost:8083`
- WebSocket proxy para Socket.IO
- Arquivos estáticos proxy

### Banco de Dados
- SQLite: `backend/data/webui.db`
- 174 notas, 21 chats, 3 usuários

### Autenticação
Para fazer login, use a página `login.html` ou execute:
```bash
cd backend
source venv/bin/activate
python generate_token.py
```

## ⚠️ Arquivos Removidos
- Scripts com portas incorretas (8080, 8082)
- Diretórios de backup antigos
- Scripts temporários de correção

## 📁 Estrutura Limpa
```
open-webui/
├── backend/         # API FastAPI
│   ├── dev.sh      # Script principal de desenvolvimento
│   ├── data/       # Banco de dados e uploads
│   └── venv/       # Ambiente virtual Python
├── src/            # Frontend SvelteKit
└── vite.config.ts  # Configuração do Vite
```