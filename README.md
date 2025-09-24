# 🏦 Sistema Bancário em Python

Este projeto implementa um **sistema bancário** em Python,
utilizando funções para gerenciar **usuários, contas, depósitos, saques
e extratos**.

------------------------------------------------------------------------

## 🔹 Estrutura do Código

### **1. Menu**

-   `menu()`: exibe as opções principais do sistema:
    -   `[d]` Depositar
    -   `[s]` Sacar
    -   `[e]` Extrato
    -   `[nc]` Nova conta
    -   `[lc]` Listar contas
    -   `[nu]` Novo usuário
    -   `[q]` Sair

------------------------------------------------------------------------

### **2. Operações Bancárias**

-   **Depositar (`depositar`)**
    -   Atualiza saldo e registra depósito no extrato se o valor for
        válido.
-   **Sacar (`sacar`)**
    -   Verifica se:
        -   há saldo suficiente,
        -   valor não excede limite,
        -   número de saques não ultrapassa o máximo diário.
    -   Registra saque no extrato, se válido.
-   **Exibir Extrato (`exibir_extrato`)**
    -   Mostra todas as movimentações realizadas.
    -   Caso não existam movimentações, exibe mensagem padrão.

------------------------------------------------------------------------

### **3. Usuários**

-   **Criar Usuário (`criar_usuario`)**
    -   Solicita CPF, nome, data de nascimento e endereço.
    -   Verifica se CPF já existe via `filtrar_usuario`.
    -   Adiciona usuário à lista, se válido.
-   **Filtrar Usuário (`filtrar_usuario`)**
    -   Retorna usuário cadastrado pelo CPF.

------------------------------------------------------------------------

### **4. Contas**

-   **Criar Conta (`criar_conta`)**
    -   Solicita CPF do usuário.
    -   Cria uma nova conta vinculada ao usuário, se ele existir.
-   **Listar Contas (`listar_contas`)**
    -   Exibe todas as contas cadastradas com agência, nº da conta e
        titular.

------------------------------------------------------------------------

### **5. Programa Principal**

-   **Função `main()`**:
    -   Define constantes:
        -   `LIMITE_SAQUES = 3`\
        -   `AGENCIA = "0001"`\
    -   Inicializa variáveis: saldo, limite, extrato, usuários e contas.
    -   Executa um loop com o menu até o usuário encerrar com `[q]`.

------------------------------------------------------------------------

## ✅ Conclusão

Este sistema bancário procedural possibilita: - Criar e gerenciar
usuários, - Criar contas bancárias, - Realizar depósitos e saques com
regras de limite, - Consultar extratos, - Listar contas existentes.

Diferente da versão orientada a objetos, este sistema é baseado em
**funções** e segue um estilo mais **estrutural**.
