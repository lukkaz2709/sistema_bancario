# 🏦 Sistema Bancário em Python

Este projeto implementa um **sistema bancário simples** em Python, com funcionalidades básicas de depósito, saque, extrato e encerramento.

---

## 📌 Funcionalidades principais

1. **Menu interativo**
   - O utilizador pode escolher entre 4 opções: **Depositar, Sacar, Consultar Extrato ou Sair**.

2. **Depósito**
   - Permite inserir valores positivos na conta.
   - O saldo é atualizado e o movimento é registado no **extrato**.
   - Se o valor for inválido (≤ 0), a operação falha.

3. **Saque (levantamento)**
   - Permite retirar dinheiro da conta, mas com regras:
     - Não pode ser maior que o saldo.
     - Não pode ultrapassar o **limite máximo por saque (1000 R$)**.
     - Existe um **limite de saques diários (3)**.
   - Se a operação for válida, o saldo é atualizado e o movimento registado no **extrato**.
   - Caso contrário, apresenta mensagens de erro.

4. **Extrato**
   - Mostra todas as movimentações feitas (depósitos e saques).
   - Exibe também o saldo atual.
   - Caso não existam operações, informa que não houve movimentações.

5. **Encerramento do programa**
   - A opção **[4] - Sair** termina o ciclo `while` e finaliza a aplicação.

---

## 🚀 Resumo

Este programa simula um **sistema bancário simples**, ideal para iniciantes que queiram praticar **estruturas de repetição, condicionais e manipulação de strings em Python**.
