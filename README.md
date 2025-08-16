# Notes App 📝

**Notes App é uma aplicação especializada de notas baseada no Open WebUI, otimizada para fornecer uma experiência completa e avançada de criação e gerenciamento de notas.** Esta aplicação mantém todas as funcionalidades robustas do sistema de notas original, mas com 90% menos complexidade, focando exclusivamente na experiência de notas.

## ✨ Características Principais

### 📝 **Editor de Notas Avançado**
- Editor rico com formatação completa (Markdown, LaTeX)
- Suporte a listas de tarefas interativas
- Realce de sintaxe para código
- Visualização em tempo real

### 💬 **Chat Integrado nas Notas**
- Sistema de chat interno para cada nota
- Modo de edição assistida por IA
- Perguntas e respostas contextuais
- Suporte a múltiplos modelos de IA

### 🎵 **Transcrição de Áudio**
- Conversão automática de áudio para texto
- Integração direta no editor
- Suporte a múltiplos formatos de áudio

### 🔗 **Processamento Inteligente de URLs**
- Transcrição automática de vídeos do YouTube
- Extração de conteúdo de posts do Instagram
- Processamento de links web diversos
- Integração automática de conteúdo nas notas

### 📁 **Sistema de Organização**
- Pastas hierárquicas para organização
- Sistema de tags flexível
- Busca avançada em conteúdo e títulos
- Interface responsiva (grid/lista)

### 📄 **Exportação Múltipla**
- Exportação para PDF com formatação preservada
- Exportação em Markdown
- Manutenção da estrutura e estilos

### 🎨 **Interface Moderna**
- Design responsivo para todos os dispositivos
- Modo claro, escuro e automático (segue sistema)
- Interface limpa e focada
- Navegação intuitiva

### 👥 **Sistema de Usuários**
- Autenticação segura
- Permissões baseadas em funções
- Notas privadas por usuário
- Gestão de acesso

### 📎 **Anexos e Arquivos**
- Upload de arquivos diretamente nas notas
- Suporte a imagens, documentos e mídia
- Gestão centralizada de arquivos

## 🚀 Como Executar

### Pré-requisitos
- Node.js 18+ 
- Python 3.11+
- npm ou yarn

### Desenvolvimento Local

1. **Clone e configure o projeto:**
   ```bash
   git clone <repository-url>
   cd open-webui
   ```

2. **Configure o Backend:**
   ```bash
   cd backend
   ./dev.sh  # Configura venv, instala dependências e inicia server na porta 8888
   ```

3. **Configure o Frontend (em outro terminal):**
   ```bash
   npm install
   npm run dev:frontend  # Inicia na porta 4173
   ```

4. **Acesse a aplicação:**
   - Frontend: http://localhost:4173
   - Backend API: http://localhost:8888

### Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev           # Frontend + Backend concorrentemente  
npm run dev:frontend  # Apenas frontend (porta 4173)
./backend/dev.sh      # Apenas backend (porta 8888)

# Build e Produção
npm run build         # Build do frontend
npm run preview       # Preview do build

# Qualidade
npm run lint:frontend # Lint do frontend
npm run test:frontend # Testes do frontend
pytest                # Testes do backend (no diretório backend)
```

### Docker (Opcional)

```bash
# Build local
docker build -t notes-app .

# Executar
docker run -d -p 3000:8080 -v notes-app:/app/backend/data --name notes-app notes-app
```

## 🏗️ Arquitetura

### Frontend (SvelteKit)
- **`/src/routes/(app)/notes/`** - Páginas principais de notas
- **`/src/lib/components/notes/`** - Componentes específicos de notas
- **`/src/lib/apis/notes.ts`** - API client para notas
- **`/src/lib/stores/`** - Gerenciamento de estado global

### Backend (FastAPI)
- **`/backend/open_webui/routers/notes.py`** - API endpoints de notas
- **`/backend/open_webui/routers/note_folders.py`** - API de pastas
- **`/backend/open_webui/routers/retrieval.py`** - Processamento de URLs
- **`/backend/open_webui/routers/audio.py`** - Transcrição de áudio
- **`/backend/open_webui/routers/files.py`** - Upload de arquivos

### Base de Dados
- **SQLite** (desenvolvimento) / **PostgreSQL** (produção)
- **Tabelas principais**: `notes`, `note_folders`, `users`
- **Migrações**: Gerenciadas via Alembic

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Backend (.env no diretório backend)
DATABASE_URL=sqlite:///app/backend/data/webui.db
CORS_ALLOW_ORIGIN=http://localhost:4173
ENABLE_WEB_SEARCH=true
YOUTUBE_LOADER_PROXY_URL=<optional-proxy>

# Frontend (automático via Vite)
VITE_BACKEND_URL=http://localhost:8888
```

### Configuração de Desenvolvimento

As portas padrão foram configuradas para evitar conflitos:
- **Frontend**: 4173 (em vez de 3000/5173)
- **Backend**: 8888 (em vez de 8080/8082)

## 📚 Funcionalidades Preservadas

Esta aplicação mantém **100% das funcionalidades de notas** do Open WebUI original:

- ✅ Editor completo com chat integrado
- ✅ Transcrição de áudio e processamento de links  
- ✅ Sistema de pastas e organização avançada
- ✅ Exportação em múltiplos formatos
- ✅ Interface responsiva e moderna
- ✅ Sistema de usuários e autenticação
- ✅ Upload de arquivos e anexos
- ✅ Busca avançada e sistema de tags

## 🗑️ O Que Foi Removido

Para simplificar e focar apenas em notas, foram removidas ~90% das funcionalidades:


- ❌ Gestão de modelos de IA
- ❌ Workspace e ferramentas
- ❌ Sistema de canais
- ❌ Playground de completions
- ❌ Funcionalidades administrativas complexas
- ❌ Pipeline e plugin system
- ❌ Integrações externas desnecessárias

## 🎯 Benefícios da Transformação

- **⚡ 90% menos código** - Mais rápido e leve
- **🧹 Manutenção simplificada** - Apenas código relevante
- **🔒 Menor superfície de ataque** - Mais seguro
- **🎯 Clareza de propósito** - Foco total em notas
- **📱 Interface mais limpa** - Sem distrações


## 📝 Licença

Este projeto mantém a licença original do Open WebUI.

## 🆘 Suporte

Para questões, sugestões ou assistência:
- Abra uma issue no repositório
- Consulte a documentação original do Open WebUI para funcionalidades base

---

**Notes App** - Uma experiência de notas focada e poderosa baseada na robusta base do Open WebUI! 📝✨