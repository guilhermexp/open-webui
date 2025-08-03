# Servidores MCP Funcionando

## Servidores Testados e Funcionando

### 1. Exa Search
- **Name**: Exa Search
- **Transport Type**: HTTP
- **URL**: `https://server.smithery.ai/exa/mcp`
- **Descrição**: Busca na web usando Exa AI
- **Ferramentas**: 6 tools incluindo web_search_exa, company_research_exa, crawling_exa

## Como Adicionar no Open WebUI

1. Vá para Admin Settings → MCP
2. Clique em "Add Server"
3. Preencha:
   - Name: (nome do servidor)
   - Transport Type: **HTTP** (importante!)
   - URL: (URL do servidor)
4. Clique em "Save"
5. Teste a conexão com "Test Connection"
6. Se funcionar, clique em "Sync Tools"

## Servidores que NÃO funcionaram com a API key fornecida

- sequential
- n8n
- duckduckgo
- github
- google-drive
- google-maps
- filesystem
- supadata-ai

## Possíveis Soluções

1. **Usar servidores MCP locais**: Em vez de Smithery, você pode instalar e executar servidores MCP localmente
2. **Verificar documentação do Smithery**: Pode haver um formato específico de URL ou configuração necessária
3. **Usar o Suna diretamente**: Como você tem o código do Suna, pode ser mais fácil usar ele diretamente