# Login no Open WebUI

## Token de Autenticação

Para fazer login no Open WebUI, siga os passos abaixo:

1. Abra o navegador e acesse: http://localhost:5173

2. Abra o console do navegador (pressione F12)

3. Cole o seguinte comando no console:

```javascript
localStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRiM2UxMjFjLWUzYTUtNGQzNi1iZjY3LTU4MmFjNDJiYjI4OCIsImV4cCI6MTc1NzUyMjk3N30.fZ0ZLInCSopmrfLQlGJRlSTZo2I2aDl5WMdEbUl0hSc');
```

4. Pressione Enter para executar o comando

5. Recarregue a página (F5)

## Informações da Conta

- **Usuário**: KortixAI
- **Email**: guilherme-varela@hotmail.com
- **Role**: admin

## Gerar Novo Token

Se precisar gerar um novo token, execute:

```bash
cd backend
source venv/bin/activate
python generate_token.py
```

## Verificação

Para verificar se está autenticado corretamente:
- As notas devem carregar normalmente
- Os chats devem aparecer na lista
- Não deve aparecer tela de login

## Troubleshooting

Se ainda tiver problemas:
1. Limpe os dados do navegador (Ctrl+Shift+Del)
2. Feche todas as abas do Open WebUI
3. Siga os passos de login novamente