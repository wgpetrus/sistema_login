import json
import os
import hashlib
import re
import getpass
import logging
from typing import List, Dict, Optional

USERS_FILE = 'usuarios.json'
LOG_FILE = 'app.log'

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def carregar_usuarios() -> List[Dict]:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def salvar_usuarios(usuarios_list: List[Dict]) -> None:
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios_list, f, ensure_ascii=False, indent=2)


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def validar_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def format_nome(s: str) -> str:
    """Formata um nome: cada palavra com inicial maiúscula e restante minúsculo."""
    return ' '.join(part.capitalize() for part in s.strip().split())


def senha_valida(senha: str) -> List[str]:
    erros: List[str] = []
    if len(senha) < 8:
        erros.append('mínimo 8 caracteres')
    if not re.search(r'[A-Z]', senha):
        erros.append('pelo menos 1 letra maiúscula')
    if not re.search(r'[a-z]', senha):
        erros.append('pelo menos 1 letra minúscula')
    if not re.search(r'\d', senha):
        erros.append('pelo menos 1 número')
    if not re.search(r'[!@#\$%\^&\*()_+\-=[\]{};:\"\\|,.<>/?]', senha):
        erros.append('pelo menos 1 caractere especial')
    return erros


usuarios: List[Dict] = carregar_usuarios()


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def encontrar_usuario_por_email(email: str) -> Optional[Dict]:
    for u in usuarios:
        if u.get('email') == email:
            return u
    return None


def criar_conta() -> None:
    print('\n=== Criar Conta ===')
    primeiro_nome = input('Primeiro nome: ').strip()
    while not primeiro_nome or ' ' in primeiro_nome:
        print('O primeiro nome não pode ser vazio nem conter espaços.')
        primeiro_nome = input('Digite somente o primeiro nome: ').strip()

    sobrenome = input('Sobrenome: ').strip()

    # Normaliza capitalização do nome e sobrenome
    primeiro_nome = format_nome(primeiro_nome)
    sobrenome = format_nome(sobrenome)
    nome_completo = f"{primeiro_nome} {sobrenome}".strip()

    email = input('Email: ').strip()
    while not validar_email(email):
        print('Email inválido. Use um formato como usuario@exemplo.com')
        email = input('Email: ').strip()

    if encontrar_usuario_por_email(email):
        print('Já existe uma conta com esse email.')
        return

    senha = getpass.getpass('Crie uma senha: ')
    erros = senha_valida(senha)
    while erros:
        print('Senha fraca: ' + ', '.join(erros))
        senha = getpass.getpass('Tente outra senha: ')
        erros = senha_valida(senha)

    senha_confirmada = getpass.getpass('Confirme a senha: ')
    while senha_confirmada != senha:
        print('Senha de confirmação diferente!')
        senha_confirmada = getpass.getpass('Confirme a senha: ')

    usuario_obj = {
        'nome': nome_completo,
        'email': email,
        'senha_hash': hash_senha(senha_confirmada)
    }

    usuarios.append(usuario_obj)
    salvar_usuarios(usuarios)
    logging.info(f'Conta criada: {email}')
    print(f'Conta criada com sucesso, {nome_completo}!')


def painel_usuario(usuario: Dict) -> None:
    while True:
        print(f"\n=== Painel de {usuario.get('nome')} ===")
        print('1 - Alterar senha')
        print('2 - Excluir conta')
        print('3 - Sair (logout)')
        opc = input('Escolha: ').strip()
        if opc == '1':
            alterar_senha(usuario)
        elif opc == '2':
            confirmar = input('Tem certeza? Digite YES para excluir: ').strip()
            if confirmar == 'YES':
                excluir_conta(usuario)
                return
        elif opc == '3':
            print('Logout...')
            return
        else:
            print('Opção inválida.')


def alterar_senha(usuario: Dict) -> None:
    print('\n=== Alterar Senha ===')
    atual = getpass.getpass('Senha atual: ')
    if hash_senha(atual) != usuario.get('senha_hash'):
        print('Senha atual incorreta.')
        logging.warning(f'Tentativa de alterar senha falhou: {usuario.get("email")}')
        return

    nova = getpass.getpass('Nova senha: ')
    erros = senha_valida(nova)
    while erros:
        print('Senha fraca: ' + ', '.join(erros))
        nova = getpass.getpass('Tente outra senha: ')
        erros = senha_valida(nova)

    conf = getpass.getpass('Confirme nova senha: ')
    if conf != nova:
        print('Confirmação diferente. Cancelando.')
        return

    usuario['senha_hash'] = hash_senha(nova)
    salvar_usuarios(usuarios)
    logging.info(f'Senha alterada: {usuario.get("email")}')
    print('Senha atualizada com sucesso.')


def excluir_conta(usuario: Dict) -> None:
    try:
        usuarios.remove(usuario)
        salvar_usuarios(usuarios)
        logging.info(f'Conta excluída: {usuario.get("email")}')
        print('Conta excluída com sucesso.')
    except ValueError:
        print('Erro ao excluir a conta.')


def fazer_login() -> bool:
    print('\n=== Fazer Login ===')
    email = input('Email: ').strip()
    senha = getpass.getpass('Senha: ')

    usuario = encontrar_usuario_por_email(email)
    if usuario and usuario.get('senha_hash') == hash_senha(senha):
        print(f"Logado com sucesso! Bem-vindo(a), {usuario.get('nome')}")
        logging.info(f'Login bem-sucedido: {email}')
        painel_usuario(usuario)
        return True

    print('Email ou senha incorretos.')
    logging.warning(f'Login falhou: {email}')
    return False


def resumo() -> None:
    print('\n=== Sistema de Login ===')
    print(f'Contas cadastradas: {len(usuarios)}')


def main() -> None:
    while True:
        resumo()
        print('\n1 - Fazer login')
        print('2 - Criar conta')
        print('3 - Sair')
        escolha = input('O que deseja? ').strip()

        if escolha == '1':
            fazer_login()
        elif escolha == '2':
            criar_conta()
        elif escolha == '3':
            print('Saindo...')
            break
        else:
            print('Escolha inválida. Digite 1, 2 ou 3.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nEncerrado pelo usuário.')