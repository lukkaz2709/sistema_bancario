# projeto_banco.py
# Sistema bancário simples com SQLite

import sqlite3
import hashlib
import getpass
import sys
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Optional

DB = 'bank.db'

# --- Helpers ---------------------------------------------------------------

def to_decimal(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def now_str():
    return datetime.utcnow().isoformat(sep=' ', timespec='seconds')

# --- Database setup -------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Customers
    cur.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')

    # Accounts
    cur.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        account_type TEXT NOT NULL,
        balance TEXT NOT NULL,
        overdraft_limit TEXT DEFAULT '0.00',
        created_at TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    ''')

    # Transactions
    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount TEXT NOT NULL,
        balance_after TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    ''')

    # Loans (simple)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        principal TEXT NOT NULL,
        outstanding TEXT NOT NULL,
        interest_rate REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    ''')

    # Meta: admin existence
    cur.execute('''
    CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)
    ''')

    conn.commit()

    # create default admin if not exists
    cur.execute("SELECT v FROM meta WHERE k='admin_created'")
    row = cur.fetchone()
    if not row:
        admin_password = hash_password('admin123')
        cur.execute("INSERT INTO customers (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    ('Administrator', 'admin@bank', admin_password, now_str()))
        conn.commit()
        cur.execute("INSERT INTO meta (k, v) VALUES (?, ?)", ('admin_created', '1'))
        conn.commit()
        print('Admin created: user=admin@bank password=admin123')

    conn.close()

# --- Models / DAO ---------------------------------------------------------

class Bank:
    def __init__(self, db=DB):
        self.db = db

    def _conn(self):
        return sqlite3.connect(self.db)

    # Customer operations
    def create_customer(self, name: str, email: str, password: str) -> int:
        h = hash_password(password)
        conn = self._conn()
        cur = conn.cursor()
        cur.execute('INSERT INTO customers (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                    (name, email, h, now_str()))
        conn.commit()
        cid = cur.lastrowid
        conn.close()
        return cid

    def authenticate(self, email: str, password: str) -> Optional[int]:
        h = hash_password(password)
        conn = self._conn()
        cur = conn.cursor()
        cur.execute('SELECT id FROM customers WHERE email=? AND password_hash=?', (email, h))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def get_customer(self, customer_id: int):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, name, email, created_at FROM customers WHERE id=?', (customer_id,))
        row = cur.fetchone(); conn.close(); return row

    # Account operations
    def open_account(self, customer_id: int, account_type: str, initial_deposit=0, overdraft=0) -> int:
        bal = to_decimal(initial_deposit)
        od = to_decimal(overdraft)
        conn = self._conn(); cur = conn.cursor()
        cur.execute('INSERT INTO accounts (customer_id, account_type, balance, overdraft_limit, created_at) VALUES (?, ?, ?, ?, ?)',
                    (customer_id, account_type, str(bal), str(od), now_str()))
        conn.commit()
        aid = cur.lastrowid
        # initial transaction
        self._add_transaction(aid, 'DEPOSIT', bal, str(bal), 'Initial deposit')
        conn.close()
        return aid

    def get_accounts_for_customer(self, customer_id: int):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, account_type, balance, overdraft_limit, created_at FROM accounts WHERE customer_id=?', (customer_id,))
        rows = cur.fetchall(); conn.close(); return rows

    def _get_account(self, account_id: int):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, customer_id, account_type, balance, overdraft_limit FROM accounts WHERE id=?', (account_id,))
        row = cur.fetchone(); conn.close(); return row

    def deposit(self, account_id: int, amount) -> bool:
        amt = to_decimal(amount)
        acc = self._get_account(account_id)
        if not acc:
            return False
        new_bal = to_decimal(acc[3]) + amt
        conn = self._conn(); cur = conn.cursor()
        cur.execute('UPDATE accounts SET balance=? WHERE id=?', (str(new_bal), account_id))
        conn.commit()
        self._add_transaction(account_id, 'DEPOSIT', amt, str(new_bal), 'Deposit')
        conn.close(); return True

    def withdraw(self, account_id: int, amount) -> bool:
        amt = to_decimal(amount)
        acc = self._get_account(account_id)
        if not acc:
            return False
        balance = to_decimal(acc[3])
        overdraft = to_decimal(acc[4])
        if balance - amt < -overdraft:
            return False
        new_bal = balance - amt
        conn = self._conn(); cur = conn.cursor()
        cur.execute('UPDATE accounts SET balance=? WHERE id=?', (str(new_bal), account_id))
        conn.commit()
        self._add_transaction(account_id, 'WITHDRAW', amt, str(new_bal), 'Withdrawal')
        conn.close(); return True

    def transfer(self, from_account: int, to_account: int, amount) -> bool:
        amt = to_decimal(amount)
        # basic check
        if from_account == to_account:
            return False
        acc_from = self._get_account(from_account)
        acc_to = self._get_account(to_account)
        if not acc_from or not acc_to:
            return False
        if not self.withdraw(from_account, amt):
            return False
        # deposit into target
        self.deposit(to_account, amt)
        # add transfer descriptors
        self._add_transaction(from_account, 'TRANSFER_OUT', amt, str(to_decimal(self._get_account(from_account)[3])), f'Transfer to account {to_account}')
        self._add_transaction(to_account, 'TRANSFER_IN', amt, str(to_decimal(self._get_account(to_account)[3])), f'Transfer from account {from_account}')
        return True

    def _add_transaction(self, account_id, ttype, amount, balance_after, description=''):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('INSERT INTO transactions (account_id, type, amount, balance_after, description, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                    (account_id, ttype, str(to_decimal(amount)), str(to_decimal(balance_after)), description, now_str()))
        conn.commit(); conn.close()

    def get_transactions(self, account_id: int, limit: int = 100):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, type, amount, balance_after, description, created_at FROM transactions WHERE account_id=? ORDER BY id DESC LIMIT ?', (account_id, limit))
        rows = cur.fetchall(); conn.close(); return rows

    # Loans (very simple model)
    def request_loan(self, account_id: int, principal, interest_rate=0.05) -> Optional[int]:
        principal_d = to_decimal(principal)
        # rule: loan <= 5x balance
        acc = self._get_account(account_id)
        if not acc:
            return None
        balance = to_decimal(acc[3])
        if principal_d > balance * Decimal('5'):
            return None
        conn = self._conn(); cur = conn.cursor()
        cur.execute('INSERT INTO loans (account_id, principal, outstanding, interest_rate, created_at) VALUES (?, ?, ?, ?, ?)',
                    (account_id, str(principal_d), str(principal_d), float(interest_rate), now_str()))
        conn.commit()
        loan_id = cur.lastrowid
        conn.close()
        # credit loan amount to account
        self.deposit(account_id, principal_d)
        return loan_id

    def get_loans_for_account(self, account_id: int):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, principal, outstanding, interest_rate, created_at FROM loans WHERE account_id=?', (account_id,))
        rows = cur.fetchall(); conn.close(); return rows

    # Admin operations
    def list_all_customers(self):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, name, email, created_at FROM customers')
        rows = cur.fetchall(); conn.close(); return rows

    def list_all_accounts(self):
        conn = self._conn(); cur = conn.cursor()
        cur.execute('SELECT id, customer_id, account_type, balance, overdraft_limit, created_at FROM accounts')
        rows = cur.fetchall(); conn.close(); return rows

    def apply_monthly_interest(self, savings_rate=0.005):
        # apply to accounts with type 'SAVINGS'
        conn = self._conn(); cur = conn.cursor()
        cur.execute("SELECT id, balance FROM accounts WHERE account_type='SAVINGS'")
        rows = cur.fetchall()
        for aid, bal in rows:
            bal_d = to_decimal(bal)
            interest = (bal_d * Decimal(str(savings_rate))).quantize(Decimal('0.01'))
            new_bal = bal_d + interest
            cur.execute('UPDATE accounts SET balance=? WHERE id=?', (str(new_bal), aid))
            cur.execute('INSERT INTO transactions (account_id, type, amount, balance_after, description, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                        (aid, 'INTEREST', str(interest), str(new_bal), f'Monthly interest @{savings_rate}', now_str()))
        conn.commit(); conn.close()

    def export_account_csv(self, account_id: int, filename: str):
        import csv
        txs = self.get_transactions(account_id, limit=10000)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'type', 'amount', 'balance_after', 'description', 'created_at'])
            writer.writerows(txs)
        return filename

# --- CLI ------------------------------------------------------------------

MENU = '''
=== Sistema Bancário ===
1) Criar cliente
2) Login cliente
3) Login admin
4) Sair
=> '''

CLIENT_MENU = '''
--- Área do Cliente ---
1) Abrir conta
2) Listar minhas contas
3) Depositar
4) Sacar
5) Transferir
6) Ver extrato
7) Pedir empréstimo
8) Logout
=> '''

ADMIN_MENU = '''
--- Área Admin ---
1) Listar clientes
2) Listar contas
3) Aplicar juros mês (poupança)
4) Exportar extrato conta
5) Logout
=> '''

bank = Bank()

def input_hidden(prompt='Senha: '):
    try:
        return getpass.getpass(prompt)
    except Exception:
        return input(prompt)


def handle_create_customer():
    name = input('Nome: ').strip()
    email = input('Email (será o login): ').strip()
    pwd = input_hidden('Senha: ')
    if not name or not email or not pwd:
        print('Informações insuficientes.')
        return
    try:
        cid = bank.create_customer(name, email, pwd)
        print(f'Cliente criado com id {cid}')
    except sqlite3.IntegrityError:
        print('Email já cadastrado.')


def handle_client_session(customer_id):
    while True:
        choice = input(CLIENT_MENU).strip()
        if choice == '1':
            print('Tipos: CHECKING (CONTA CORRENTE), SAVINGS (CONTA POUPANÇA)')
            t = input('Tipo: ').strip().upper()
            initial = float(input('Depósito inicial (ex: 100.00): ') or 0)
            overdraft = float(input('Limite de cheque especial (0 para nenhum): ') or 0)
            aid = bank.open_account(customer_id, t, initial, overdraft)
            print(f'Conta criada: {aid}')
        elif choice == '2':
            accs = bank.get_accounts_for_customer(customer_id)
            for a in accs:
                print(f'ID: {a[0]} | Tipo: {a[1]} | Saldo: {a[2]} | Od: {a[3]} | Criada: {a[4]}')
        elif choice == '3':
            aid = int(input('Conta ID: '))
            amt = float(input('Valor depositar: '))
            ok = bank.deposit(aid, amt)
            print('Depósito realizado.' if ok else 'Erro no depósito.')
        elif choice == '4':
            aid = int(input('Conta ID: '))
            amt = float(input('Valor sacar: '))
            ok = bank.withdraw(aid, amt)
            print('Saque realizado.' if ok else 'Saque negado (saldo insuficiente).')
        elif choice == '5':
            fa = int(input('De (ID conta): '))
            ta = int(input('Para (ID conta): '))
            amt = float(input('Valor: '))
            ok = bank.transfer(fa, ta, amt)
            print('Transferência concluída.' if ok else 'Falha na transferência.')
        elif choice == '6':
            aid = int(input('Conta ID: '))
            txs = bank.get_transactions(aid, limit=50)
            print('Últimas transações:')
            for t in txs:
                print(f'{t[5]} | {t[1]} | {t[2]} | Saldo após: {t[3]} | {t[4]}')
        elif choice == '7':
            aid = int(input('Conta ID: '))
            amt = float(input('Valor do empréstimo: '))
            rate = float(input('Taxa anual (ex: 0.05 para 5%): ') or 0.05)
            lid = bank.request_loan(aid, amt, rate)
            print('Empréstimo aprovado, id=' + str(lid) if lid else 'Empréstimo negado.')
        elif choice == '8':
            break
        else:
            print('Opção inválida')


def handle_admin_session():
    while True:
        c = input(ADMIN_MENU).strip()
        if c == '1':
            rows = bank.list_all_customers()
            for r in rows:
                print(r)
        elif c == '2':
            rows = bank.list_all_accounts()
            for r in rows:
                print(r)
        elif c == '3':
            rate = float(input('Taxa mensal para poupança (ex 0.005 = 0.5%): ') or 0.005)
            bank.apply_monthly_interest(rate)
            print('Juros aplicados.')
        elif c == '4':
            aid = int(input('Conta ID: '))
            fname = input('Nome do arquivo csv (ex: extrato.csv): ').strip() or f'extrato_{aid}.csv'
            bank.export_account_csv(aid, fname)
            print(f'Exportado para {fname}')
        elif c == '5':
            break
        else:
            print('Opção inválida')


def main():
    init_db()
    while True:
        choice = input(MENU).strip()
        if choice == '1':
            handle_create_customer()
        elif choice == '2':
            email = input('Email: ').strip()
            pwd = input_hidden('Senha: ')
            uid = bank.authenticate(email, pwd)
            if uid:
                print('Login ok')
                handle_client_session(uid)
            else:
                print('Credenciais inválidas')
        elif choice == '3':
            email = input('Admin email: ').strip()
            pwd = input_hidden('Senha: ')
            uid = bank.authenticate(email, pwd)
            # simple check: email must be admin@bank
            if uid and email == 'admin@bank':
                print('Admin logado')
                handle_admin_session()
            else:
                print('Credenciais admin inválidas')
        elif choice == '4':
            print('Saindo...')
            sys.exit(0)
        else:
            print('Opção inválida')

if __name__ == '__main__':
    main()
