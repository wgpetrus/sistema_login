# Sistema de Login (simples)

Projeto simples: um sistema de cadastro/login em linha de comando.

Funcionalidades
- Criar conta com validação de email e verificação de força de senha
- Login com senhas digitadas em modo oculto (usa `getpass`)
- Painel do usuário: alterar senha ou excluir conta
- Persistência em `usuarios.json`
- Logs em `app.log`

Requisitos
- Python 3.8+
- Não há dependências externas (usa apenas a biblioteca padrão)

Como executar
1. Abra um terminal na pasta do projeto
2. Execute:

```powershell
python .\main.py
```

Notas
- Este projeto é propositalmente simples para fins de aprendizado.
- Para produção, recomenda-se usar um banco de dados e hash de senha com salt (ex.: `bcrypt`).