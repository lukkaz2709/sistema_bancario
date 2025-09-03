menu = """

[1] - Depositar
[2] - Sacar
[3] - Extrato
[4] - Sair

=> """

saldo = 0
limite = 1000
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:

    opcao = input(menu)

    if opcao == "1":
        valor = float(input("informe o valor do depósito: "))

        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"
        
        else:
            print("Operação falhou, valor inválido!")

    elif opcao == "2":
        valor = float(input("informe o valor do saque: "))

        excedeu_saldo = valor > saldo

        excedeu_limite = valor > limite

        excedeu_saques = numero_saques > LIMITE_SAQUES

        if excedeu_saldo:
            print("Operação falhou! você não tem saldo suficiente. ")

        elif excedeu_limite:
            print("Operação falhou! o valor do saque excede o limite. ")

        elif excedeu_limite:
            print("Operação falhou! número máximo de saques excedido. ")

        elif valor > 0:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f}\n"
            numero_saques += 1

        else:
            print("Operação falhou! o valor informado é inválido.")

    elif opcao == "3":
        print("\n=========EXTRATO=========")
        print("Não foram realizadas movimentações em sua conta" if not extrato else extrato)
        print(f"\n Saldo: R$ {saldo:.2f}")
        print("=============================")

    elif opcao == "4":
        break

    else:
        print("ATENÇÃO!!! Operação inválida, por favor selecione novamente a operação desejada!")

