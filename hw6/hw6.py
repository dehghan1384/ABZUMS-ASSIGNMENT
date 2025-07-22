class BankAccount:
    # Class attribute
    bank_name = "First National Bank"
    
    def __init__(self, account_holder: str, initial_balance: float = 0.0):
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transactions = []
    def deposit(self, amount: float) -> None:
        if amount > 0:
            self.balance += amount
            self.transactions.append(f"Deposit: +${amount}")
            print(f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")
        else:
            print("Deposit amount must be positive.")

        
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return
        
        if amount <= self.balance:
            self.balance -= amount
            self.transactions.append(f"Withdrawal: -${amount}")
            print(f"Withdrawn ${amount:.2f}. New balance: ${self.balance:.2f}")
        else:
            print("Not enough balance")
    def __str__(self) -> str:
        return f"Account Holder: {self.account_holder}, Balance: ${self.balance:.2f}"

    @classmethod
    def change_bank_name(cls, new_name: str) -> None:
        cls.bank_name = new_name

    @staticmethod
    def validate_amount(amount: float) -> bool:
        return amount > 0        
    def show_transactions(self) -> None:
    # Print all transactions
        print(self.transactions)

# Create accounts
alice_account = BankAccount("Alice", 1000)
bob_account = BankAccount("Bob", 500)

# Perform transactions
print(alice_account.deposit(200))      
print(bob_account.withdraw(-100))     
print(bob_account.withdraw(600))      
print(bob_account.deposit(150))        

# Change bank name
BankAccount.change_bank_name("Global Trust Bank")

# Print accounts
print(alice_account)                  
print(bob_account)                     

# Validate amounts
print(f"Is -50 valid? {BankAccount.validate_amount(-50)}")  
print(f"Is 300 valid? {BankAccount.validate_amount(300)}")  

# Print all transactions
bob_account.show_transactions()  

class SavingsAccount(BankAccount):
    def __init__(self, account_holder: str, initial_balance: float = 0.0, interest_rate: float = 0.01):
        # Initialize parent class and add new attribute
        super().__init__(account_holder , initial_balance)
        self.interest_rate=interest_rate

    
    def add_interest(self) -> None:
        # Calculate and deposit interest
        self.deposit(self.interest_rate * self.balance)
    
    def __str__(self) -> str:
        # Enhanced string representation
        return 'Savings Account - '+ super().__str__() + f" interest_rate = {(self.interest_rate*100):.1f}%"
    # Test SavingsAccount here
Charlie_account = SavingsAccount('charlie', 0 , 0.05 )
# --------------
Charlie_account.deposit(1000)
# --------------
Charlie_account.add_interest()
# --------------
print(Charlie_account)