# Teste de Embelezamento de Notas com Instagram/YouTube

## Como Testar a Funcionalidade de Embelezamento

### 1. Teste com YouTube
Crie uma nova nota e adicione este conteúdo:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 2. Teste com Instagram
Crie uma nova nota e adicione este conteúdo:
```
https://www.instagram.com/reel/C4hgXvRg4ZV/
```

### 3. Teste com Website
Crie uma nova nota e adicione este conteúdo:
```
https://example.com
```

### 4. Como Embelezar
1. Clique no botão de embelezamento (ícone de varinha mágica)
2. Selecione um modelo de IA na lista
3. Aguarde o processamento

## Verificações de Debug

### No Console do Browser (F12)
Você deve ver logs como:
- "Enhance note handler called"
- "Selected model: [model_id]"
- "Extracting YouTube URLs from: [content]"
- "YouTube extraction result: [result]"

### Possíveis Problemas

1. **Modelo não selecionado**: O sistema agora auto-seleciona o primeiro modelo disponível
2. **Token de autenticação**: Verifique se está logado
3. **Backend não está rodando**: Execute `cd backend && ./dev.sh`
4. **Dependências faltando**: Verifique se `youtube-transcript-api` e `instaloader` estão instalados

## Script de Teste do Backend

Execute o script de teste:
```bash
cd backend
python test_instagram_endpoint.py
```

Primeiro você precisa obter seu token:
1. Abra o navegador com a aplicação
2. Pressione F12 (DevTools)
3. Vá para Application > Local Storage
4. Copie o valor de "token"
5. Cole no script test_instagram_endpoint.py

## Logs do Backend

Para ver logs detalhados:
```bash
cd backend
tail -f logs/open-webui.log
```

## URLs de Teste

### YouTube
- https://www.youtube.com/watch?v=dQw4w9WgXcQ (Rick Roll - sempre disponível)
- https://youtu.be/dQw4w9WgXcQ (versão curta)

### Instagram
- https://www.instagram.com/reel/C4hgXvRg4ZV/
- https://www.instagram.com/p/C4hgXvRg4ZV/

### Websites
- https://example.com
- https://openai.com
- https://anthropic.com