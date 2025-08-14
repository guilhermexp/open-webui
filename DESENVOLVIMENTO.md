# 🛠️ Guia de Desenvolvimento - Notes App

Este documento fornece informações detalhadas para desenvolvedores que trabalham na aplicação Notes App.

## 📋 Visão Geral

A Notes App é uma aplicação especializada baseada no Open WebUI que foi transformada para focar exclusivamente em funcionalidades de notas. A aplicação mantém toda a robustez do sistema original, mas com 90% menos complexidade.

## 🏗️ Arquitetura Detalhada

### Frontend (SvelteKit + TypeScript)

```
src/
├── routes/
│   ├── (app)/
│   │   ├── notes/           # Páginas principais de notas
│   │   │   ├── +page.svelte # Lista de notas
│   │   │   └── +layout.svelte
│   │   └── +layout.svelte   # Layout da aplicação
│   ├── auth/               # Autenticação
│   └── +layout.svelte      # Layout raiz
├── lib/
│   ├── components/
│   │   ├── notes/          # Componentes específicos de notas
│   │   │   ├── NoteEditor/ # Editor principal
│   │   │   ├── Notes/      # Lista e gerenciamento
│   │   │   └── *.svelte
│   │   ├── common/         # Componentes reutilizáveis
│   │   │   ├── ThemeToggle.svelte # Alternar tema
│   │   │   └── *.svelte
│   │   └── layout/         # Componentes de layout
│   ├── apis/               # Clientes de API
│   │   ├── notes.ts        # API de notas
│   │   ├── audio.ts        # Transcrição de áudio
│   │   └── retrieval.ts    # Processamento de URLs
│   ├── stores/             # Estado global (Svelte stores)
│   ├── utils/              # Utilitários
│   └── constants.ts        # Constantes da aplicação
```

### Backend (FastAPI + Python)

```
backend/
├── open_webui/
│   ├── routers/            # Endpoints da API
│   │   ├── notes.py        # CRUD de notas
│   │   ├── note_folders.py # Sistema de pastas
│   │   ├── retrieval.py    # Processamento de URLs
│   │   ├── audio.py        # Transcrição de áudio
│   │   ├── files.py        # Upload de arquivos
│   │   ├── auths.py        # Autenticação
│   │   └── users.py        # Gestão de usuários
│   ├── models/             # Modelos SQLAlchemy
│   │   ├── notes.py        # Modelo de notas
│   │   └── users.py        # Modelo de usuários
│   ├── utils/              # Utilitários do backend
│   └── main.py             # Aplicação FastAPI principal
├── alembic/                # Migrações de banco
└── requirements.txt        # Dependências Python
```

## 🚀 Configuração do Ambiente

### 1. Configuração Inicial

```bash
# Clone o repositório
git clone <repository-url>
cd open-webui

# Instalar dependências do frontend
npm install

# Configurar backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Configuração de Desenvolvimento

As portas foram configuradas para evitar conflitos:

- **Frontend**: 4173 (Vite dev server)
- **Backend**: 8888 (FastAPI + Uvicorn)

### 3. Variáveis de Ambiente

#### Backend (.env no diretório backend/)
```env
# Banco de dados
DATABASE_URL=sqlite:///app/backend/data/webui.db

# CORS
CORS_ALLOW_ORIGIN=http://localhost:4173

# Funcionalidades
ENABLE_WEB_SEARCH=true
YOUTUBE_LOADER_PROXY_URL=https://your-proxy-url.com

# Opcional: Configurações de IA
OPENAI_API_KEY=your_openai_key
OLLAMA_BASE_URL=http://localhost:11434
```

#### Frontend (automaticamente configurado)
```env
VITE_BACKEND_URL=http://localhost:8888
```

## 🔧 Scripts de Desenvolvimento

### Comandos Principais
```bash
# Desenvolvimento completo (frontend + backend)
npm run dev

# Apenas frontend
npm run dev:frontend

# Apenas backend
cd backend && ./dev.sh

# Build de produção
npm run build

# Preview do build
npm run preview
```

### Comandos de Qualidade
```bash
# Linting
npm run lint:frontend  # Frontend
pylint backend/        # Backend

# Formatação
prettier --write "src/**/*.{js,ts,svelte}"  # Frontend
black backend/                              # Backend

# Testes
npm run test:frontend  # Frontend
cd backend && pytest  # Backend
```

## 🗄️ Banco de Dados

### Estrutura Principal

#### Tabela `notes`
```sql
CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    folder_id TEXT,
    title TEXT NOT NULL,
    content JSONB,  -- {md: string, html: string, json: object}
    tags TEXT[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (folder_id) REFERENCES note_folders(id)
);
```

#### Tabela `note_folders`
```sql
CREATE TABLE note_folders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    parent_id TEXT,
    name TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES note_folders(id)
);
```

### Migrações
```bash
# Criar nova migração
cd backend
alembic revision -m "descrição da alteração"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1
```

## 🔌 APIs Principais

### Notas
```typescript
// GET /api/v1/notes
// Listar notas do usuário
interface NotesResponse {
  notes: Note[];
  total: number;
}

// POST /api/v1/notes
// Criar nova nota
interface CreateNoteRequest {
  title: string;
  content?: {md: string, html: string};
  folder_id?: string;
  tags?: string[];
}

// PUT /api/v1/notes/{note_id}
// Atualizar nota existente

// DELETE /api/v1/notes/{note_id}
// Excluir nota
```

### Processamento de URLs
```typescript
// POST /api/v1/retrieval/youtube
// Extrair transcrição de vídeo do YouTube
interface YouTubeRequest {
  url: string;
}

// POST /api/v1/retrieval/web
// Extrair conteúdo de página web
interface WebRequest {
  url: string;
}
```

### Transcrição de Áudio
```typescript
// POST /api/v1/audio/transcriptions
// Transcrever arquivo de áudio
interface TranscriptionRequest {
  file: File;
  model?: string;
}
```

## 🎨 Sistema de Temas

### Configuração
O sistema de temas suporta:
- **light**: Modo claro
- **dark**: Modo escuro  
- **system**: Segue preferência do sistema operacional

### Implementação
```typescript
// Aplicar tema
window.applyTheme = () => {
  const theme = localStorage.theme || 'system';
  document.documentElement.classList.remove('dark', 'light');
  
  if (theme === 'system') {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.add(isDark ? 'dark' : 'light');
  } else {
    document.documentElement.classList.add(theme);
  }
};
```

### Componente ThemeToggle
Localizado em `/src/lib/components/common/ThemeToggle.svelte`, permite alternar entre os temas com interface visual.

## 🧪 Testes

### Frontend (Vitest + Testing Library)
```bash
# Executar testes
npm run test:frontend

# Executar com cobertura
npm run test:frontend -- --coverage

# Modo watch
npm run test:frontend -- --watch
```

### Backend (pytest)
```bash
cd backend

# Executar todos os testes
pytest

# Executar teste específico
pytest test/test_notes.py

# Com cobertura
pytest --cov=open_webui

# Modo verboso
pytest -v
```

## 🚢 Deploy

### Docker
```bash
# Build da imagem
docker build -t notes-app .

# Executar container
docker run -d \
  -p 3000:8080 \
  -v notes-app-data:/app/backend/data \
  --name notes-app \
  notes-app
```

### Produção
1. Configure variáveis de ambiente de produção
2. Use PostgreSQL em vez de SQLite
3. Configure proxy reverso (nginx)
4. Implemente SSL/TLS
5. Configure monitoramento e logs

## 📝 Convenções de Código

### Frontend (TypeScript/Svelte)
- Use TypeScript para type safety
- Componentes em PascalCase (`NoteEditor.svelte`)
- Variáveis em camelCase
- Constantes em SCREAMING_SNAKE_CASE
- Props exportadas no topo do script

### Backend (Python)
- Siga PEP 8
- Use type hints
- Docstrings para funções públicas
- Nomes de funções em snake_case
- Classes em PascalCase

### Commits
Siga o padrão Conventional Commits:
```
feat: adicionar funcionalidade de busca em notas
fix: corrigir erro de salvamento automático
docs: atualizar documentação da API
refactor: simplificar lógica de processamento de URLs
```

## 🐛 Debug e Troubleshooting

### Problemas Comuns

1. **Erro de CORS**
   - Verifique se `CORS_ALLOW_ORIGIN` está configurado corretamente
   - Certifique-se que as portas coincidem

2. **Banco de dados não encontrado**
   - Execute `alembic upgrade head` para criar/atualizar tabelas

3. **Módulos não encontrados**
   - Verifique se o venv está ativado
   - Reinstale dependências com `pip install -r requirements.txt`

4. **Frontend não conecta com backend**
   - Verifique se backend está rodando na porta 8888
   - Confirme URLs em `constants.ts`

### Logs
```bash
# Backend logs
cd backend
tail -f logs/app.log

# Frontend logs
# Disponíveis no console do navegador (F12)
```

## 📚 Recursos Adicionais

- **Documentação Original**: [Open WebUI Docs](https://docs.openwebui.com)
- **SvelteKit**: [Documentação oficial](https://kit.svelte.dev/docs)
- **FastAPI**: [Documentação oficial](https://fastapi.tiangolo.com)
- **Tailwind CSS**: [Documentação oficial](https://tailwindcss.com/docs)

---

**Happy Coding!** 🚀📝