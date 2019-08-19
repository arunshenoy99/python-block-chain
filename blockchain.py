import functools
import hashlib
from collections import OrderedDict
import json

from hash_util import hash_block,hash_string_256
from block import Block
from transaction import Transaction

#REWARD FOR THE MINER FOR MINIG A NEW BLOCK FROM THE OPEN TRANSACTIONS,PREVIOUS HASH AND INDEX
MINING_REWARD = 10
#INITIALIZING THE BLOCKCHAIN,OPEN TRANSACTIONS LISTS,PARTICIPANT IS A SET
blockchain = []
open_transactions = []
owner = 'Arun'

#SAVE THE BLOCKCHAIN DATA
def save_data():
    """Saves the blockchain and open transactions as strings"""
    try:
        with open('blockchain.txt',mode = 'w') as f:
            saveable_chain = [block.__dict__ for block in [Block(block_el.index,block_el.previous_hash,[tx.__dict__ for tx in block_el.transactions],block_el.proof,block_el.timestamp) for block_el in blockchain]]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_tx))
            #save_data = {
                #'chain':blockchain,
                #'ot':open_transactions
            #}
            #f.write(pickle.dumps(save_data))
    except (IOError,IndexError):
        print('Saving failed')

#LOAD THE BLOCKCHAIN DATA
def load_data():
    global blockchain,open_transactions
    try:
        with open('blockchain.txt', mode = 'r') as f:
            file_content = f.readlines()
            #file_content= pickle.loads(f.read())
            #blockchain = file_content['chain']
            #open_transactions = file_content['ot']
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(tx['sender'],tx['recipient'],tx['amount']) for tx in block['transactions']]
                updated_block = Block(block['index'], block['previous_hash'], converted_tx,block['proof'],block['timestamp'])
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            open_transactions = [Transaction(tx['sender'],tx['recipient'],tx['amount']) for tx in open_transactions]
    except (IOError,IndexError):
        #CREATE THE FIRST BLOCK IN THE BLOCKCHAIN
        genesis_block = Block(0 , '' , [] , 100 , 0)
        #ADD GENESIS BLOCK TO THE BLOCKCHAIN
        blockchain.append(genesis_block)

load_data()

#GET THE BALANCE FOR A PARTICIPANT
def get_balance(participant):
    """ Returns the balance of the participant by considering sent and recieved amounts in previous transactions and open transactions
        :participant:The participant name whose balance is to be found
     """
    tx_sender = [[tx.amount for tx in block.transactions if tx.sender==participant] for block in blockchain]
    open_tx_sender = [tx.amount for tx in open_transactions if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum+sum(tx_amt) if len(tx_amt)>0 else tx_sum+0,tx_sender,0)
    tx_recieved = [[tx.amount for tx in block.transactions if tx.recipient==participant] for block in blockchain]
    amount_recieved = functools.reduce(lambda tx_sum,tx_amt: tx_sum+sum(tx_amt) if len(tx_amt)>0 else tx_sum+0,tx_recieved,0)
    return amount_recieved-amount_sent

#DEFINE THE VALID PROOF OF WORK CRITERIA
def valid_proof(transactions , last_hash , proof):
    """Checks if the given pow number is valid
    :transactions:The transactions of the block(open transactions if new block)
    :last_hash:The previous hash value of the block
    :proof:The pow number
    """
    guess = str(str([tx.to_ordered_dict() for tx in transactions])+str(last_hash)+str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'

#GENERATE THE VALID PROOF OF WORK
def proof_of_work():
    """Generates the valid proof of work number"""
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions , last_hash , proof):
        proof = proof+1
    return proof

#GET THE LAST BLOCK IN THE BLOCKCHAIN
def get_last_blockchain_value():
    """Returns the last block in the blockchain"""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

#VERFIY THE TRANSACTION
def verify_transaction(transaction):
    """Returns the boolean True if balance is greater than transaction amount else it returns false"""
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount

#ADD A NEW TRANSACTION TO OPEN TRANSACTIONS
def add_transaction(recipient , sender = owner, amount = 1.0):
    """Adds the new transactions to the list of open transactions and returns boolean true or false based on completion status
    :recipient:The person who is the reciever
    :sender:The sender of the amount
    "amount:The amount to be sent
    """
    transaction = Transaction(sender,recipient,amount)
    if(verify_transaction(transaction)):
        open_transactions.append(transaction)
        return True
    return False

#MINE A NEW BLOCK
def mine_block():
    """Adds a new block to the blockchain after validation and proof of work"""
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof=proof_of_work()
    reward_transaction = Transaction('Mining',owner,MINING_REWARD)
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = Block(len(blockchain) , hashed_block , copied_transactions , proof)
    blockchain.append(block)
    return True
 
#GET A TRANSACTION
def get_transaction_value():
    """Returns the user input transaction amount in float"""
    tx_recipient = input('Recipient')
    tx_amount = float(input('Enter the amount:'))
    transaction = (tx_recipient,tx_amount)
    return transaction

#GET THE USER CHOICE OF THE MENU
def get_user_choice():
    """retunrs the user choice"""
    return input('Your Choice:')

#OUTPUT THE BLOCKCHAIN ELEMENTS
def print_blockchain_elements():
    """prints the blockchain elements"""
    print('Outputting blockchain')
    for block in blockchain:
        print(block)

#VERIFY HASHES AND PROOF OF WORK'S
def verify_chain():
    """Checks block hashes and proof of works and returns true or false based on success or failure"""
    for (index,block) in enumerate(blockchain):
        if(index == 0):
            continue
        if(block.previous_hash != hash_block(blockchain[index-1])):
            return False
        if (not valid_proof(block.transactions[:-1],block.previous_hash,block.proof)):
            print('Proof is invalid')
            return False
    return True

#VERIFY EACH TRANSACTION
def verify_transactions():
    """Verifies all the transactions and returns true if all are valid else false"""
    return all([verify_transaction(tx) for tx in open_transactions])

#BLOCKCHAIN COMMAND LINE INTERFACE
while True:
    print('Please choose')
    print('1.Add a new transaction value')
    print('2.Mine a block')
    print('3.Print the blocks')
    print('4.Check transactions validity')
    print('q.Quit')
    user_choice=get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient , amount = tx_data
        if(add_transaction(recipient , amount = amount)):
            print('Added Transaction')
            save_data()
        else:
            print('Transaction failed')
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        if verify_transactions():
            print('Transactions are valid')
        else:
            print('Transactions are not valid')
    elif user_choice == 'q':
        break
    else:
        print('Invalid choice')
    if not verify_chain():
        print('Invalid Blockchain')
        break    
    print('Balance of {} is {:6.2f}'.format(owner,get_balance(owner)))                  

print('Done')