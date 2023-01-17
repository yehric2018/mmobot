import os
import sqlalchemy

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, Column, Integer
from sqlalchemy.orm import declarative_base, Session

load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_SIMS_DATABASE_NAME')

connection_url = 'mysql+pymysql://{}:{}@{}/{}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)
engine = create_engine(connection_url)
engine.echo = True

Base = declarative_base()


class BankAccount(Base):
    '''
    Represents an account for a banking application. Note that an account
    may be owned by multiple people, so we could have multiple transactions
    modifying an account's balance at once.

    Our goal is to ensure that the account's balance never gets messed up by
    any race conditions!
    '''
    __tablename__ = 'BankAccounts'

    account_id = Column(Integer, primary_key=True)
    balance = Column(Integer)


Base.metadata.create_all(bind=engine)


def prompt_account_id():
    print(
        'Welcome to the new banking service that will keep your money safe'
        ' and sound! To begin, please provide your account ID.'
    )
    account_id = input()
    while not account_id.isnumeric():
        print('Please enter an int for your account ID.')
        account_id = input()
    return int(account_id)


def prompt_change_balance(account_id):
    print(
        'Your account ID is ' + str(account_id) + '. You may now enter in how'
        ' much money you want to add to your account (or how much you want to'
        ' take out as a negative number).'
    )
    amount = input()
    while not amount.isnumeric():
        print('Please enter an int for the amount to deposit/withdraw.')
        amount = input()
    return int(amount)


def select_bank_account(session, account_id):
    get_account_statement = (
        select(BankAccount)
        .where(BankAccount.account_id == account_id)
        .with_for_update()
    )
    return session.scalars(get_account_statement).one_or_none()


def transaction_login(session, account_id):
    try:
        if select_bank_account(session, account_id) is not None:
            print(
                'You already have a bank account!'
            )
        else:
            print(
                'You do not seem to have a bank account yet, press ENTER so I'
                ' can create one for you...'
            )
            input()
            session.add(BankAccount(account_id=account_id, balance=0))
            session.commit()
    except sqlalchemy.exc.OperationalError as error:
        if error.orig.args[0] == 1213:
            # A deadlock has occurred, we need to retry.
            print(
                'Whoops, something happened in our systems, let\'s try that'
                ' again...'
            )
            session.rollback()
            transaction_login(session, account_id)
        else:
            # Some other error has occurred. We won't worry about it here.
            print(
                'If you are seeing this, a VERY bad error has occurred. Don\'t'
                ' worry though, this is just a simulation. :)'
            )
            session.rollback()


with Session(engine) as session:
    account_id = prompt_account_id()

    # BEGIN TRANSACTION 1
    # Create a new account if an account does not already exist.
    transaction_login(session, account_id)
    # END TRANSACTION 1

with Session(engine) as session:
    amount = prompt_change_balance(account_id)
    # BEGIN TRANSACTION 2
    # Add the amount to the current account.
    account = select_bank_account(session, account_id)
    print(
        'Just letting you know before this transaction, you had $'
        + str(account.balance) + ' in your account. Press ENTER to add/'
        'subtract the amount to this balance now.'
    )
    input()
    account.balance += amount
    session.commit()
    # END TRANSACTION 2

    # BEGIN TRANSACTION 3
    # See the final balance in the account.
    print(
        'Your balance has been updated! Press enter to see your final balance!'
    )
    input()
    account = select_bank_account(session, account_id)
    print(
        'You have ' + str(account.balance) + ' in your account now! Hope this'
        ' is what you wanted! (Press ENTER to complete this session)'
    )
    input()
    # END TRANSACTION 3


print(
    'Thank you for using our banking service! '
    'Unfortunately we have gone bankrupt, so we must delete all your data now!'
)
Base.metadata.drop_all(engine)
