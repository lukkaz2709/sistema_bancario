# 🏦 Sistema Bancário em Python

Este projeto implementa um **sistema bancário completo** em Python, com
persistência de dados em **SQLite** e interface **CLI interativa**.

------------------------------------------------------------------------

## 🚀 Funcionalidades

### 👤 Clientes

-   **Cadastro de clientes** com nome, e-mail (login) e senha
    (armazenada em hash SHA-256).
-   **Autenticação** segura via e-mail e senha.

### 💳 Contas

-   **Abertura de conta**:
    -   **Conta Corrente (CHECKING)** com opção de limite de cheque
        especial.
    -   **Conta Poupança (SAVINGS)** com rendimento mensal (juros).
-   **Depósitos** com atualização de saldo e registro de transação.
-   **Saques** respeitando saldo e limite de cheque especial.
-   **Transferências** entre contas, com registro em ambos extratos.

### 📑 Transações

-   Cada operação gera um **registro de transação**:
    -   Tipo (DEPÓSITO, SAQUE, TRANSFERÊNCIA, JUROS, etc.)
    -   Valor da operação
    -   Saldo após a operação
    -   Descrição
    -   Data/hora (UTC)
-   **Extrato** com listagem das últimas movimentações.
-   **Exportação para CSV** de todas as transações de uma conta.

### 💰 Poupança

-   **Aplicação automática de juros mensais** em contas do tipo
    **SAVINGS**.
-   Juros configuráveis pelo administrador.

### 📌 Empréstimos

-   Solicitação de **empréstimo simples**:
    -   Regra: valor máximo = até **5x o saldo da conta**.
    -   Valor liberado é creditado na conta.
    -   Armazenamento de valor principal, saldo devedor e taxa de juros.

### 🛠 Área do Administrador

-   Usuário administrador padrão:
    -   **Email:** `admin@bank`
    -   **Senha:** `admin123`
-   Funcionalidades:
    -   Listar todos os clientes cadastrados.
    -   Listar todas as contas existentes.
    -   Aplicar juros mensais em todas as contas poupança.
    -   Exportar extrato de conta para arquivo CSV.

------------------------------------------------------------------------

## 📂 Estrutura do Banco de Dados (SQLite)

-   **customers**: dados de clientes.
-   **accounts**: contas vinculadas a clientes.
-   **transactions**: histórico de movimentações.
-   **loans**: empréstimos concedidos.
-   **meta**: metadados do sistema (ex: admin criado).

------------------------------------------------------------------------

## 🖥 Como Usar

1.  Execute o programa:

    ``` bash
    python sistema_bancario.py
    ```

2.  No primeiro uso, será criado o banco de dados `bank.db` e o usuário
    administrador.

3.  Use o menu principal para:

    -   Criar clientes
    -   Fazer login como cliente
    -   Fazer login como administrador

------------------------------------------------------------------------

## 📌 Menus

### Menu Principal

    1) Criar cliente
    2) Login cliente
    3) Login admin
    4) Sair

### Menu Cliente

    1) Abrir conta
    2) Listar contas
    3) Depositar
    4) Sacar
    5) Transferir
    6) Ver extrato
    7) Pedir empréstimo
    8) Logout

### Menu Admin

    1) Listar clientes
    2) Listar contas
    3) Aplicar juros mês (poupança)
    4) Exportar extrato conta
    5) Logout

------------------------------------------------------------------------

## ⚠️ Observações

-   Sistema educativo/simplificado, não indicado para produção.
-   Senhas são armazenadas em hash, mas **sem salt** (em produção use
    **bcrypt/argon2**).
-   Comunicação não é criptografada.
-   Não há autenticação multiusuário simultânea.

------------------------------------------------------------------------

## 📌 Próximos Passos / Possíveis Melhorias

-   Adicionar **interface gráfica (tkinter ou web)**.
-   Implementar **API REST** (FastAPI/Flask).
-   Melhorar segurança (hash com salt, autenticação multifator).
-   Relatórios financeiros avançados.
-   Sistema de notificações por e-mail.

------------------------------------------------------------------------

✅ Desenvolvido como exemplo de estudo em Python.
