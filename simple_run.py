import json
import random
import string
from mempool import Mempool
from transaction import Transaction
from utxo import UTXOSet

def generate_txid():
    """Generate a random transaction ID."""
    return 'tx_' + ''.join(random.choices(string.hexdigits, k=16)).lower()

def show_utxos(utxo_set):
    """Display all UTXOs."""
    print("\n" + "="*80)
    print("UNSPENT TRANSACTION OUTPUTS (UTXOs)".center(80))
    print("-" * 80)
    if not utxo_set.utxos:
        print("No UTXOs available")
    else:
        for (txid, idx), output in utxo_set.utxos.items():
            print(f"{txid}:{idx} -> {output['address']}: {output['amount']/1e8:.8f} BTC")
    print("="*80 + "\n")

def show_mempool(mempool):
    """Display mempool contents."""
    print("\n" + "="*80)
    print("MEMPOOL CONTENTS".center(80))
    print("-" * 80)
    
    info = mempool.get_mempool_info()
    print(f"Transactions: {info['tx_count']}")
    print(f"Size: {info['bytes']} ({info['usage']} of {info['max_size']})")
    
    txs = mempool.get_transactions_by_fee_rate()
    if not txs:
        print("\nMempool is empty")
    else:
        print("\nTransactions (sorted by fee rate):")
        for i, tx in enumerate(txs, 1):
            print(f"{i:3}. {tx.txid[:8]}... | Fee rate: {tx.fee_rate:>6.1f} sat/byte | "
                  f"Size: {tx.size:>5} bytes | Inputs: {len(tx.inputs)} | Outputs: {len(tx.outputs)}")
    
    print("="*80 + "\n")

def add_transaction(mempool, utxo_set):
    """Add a new transaction to the mempool."""
    print("\nAdd a new transaction")
    print("-" * 80)
    
    # Show available UTXOs
    print("\nAvailable UTXOs:")
    utxo_list = list(utxo_set.utxos.items())
    for i, ((txid, idx), output) in enumerate(utxo_list, 1):
        print(f"{i}. {txid}:{idx} -> {output['amount']/1e8:.8f} BTC")
    
    try:
        # Get inputs
        inputs = []
        while True:
            print("\nSelect a UTXO to spend (or press Enter to finish):")
            choice = input("> ").strip()
            if not choice:
                if not inputs:
                    print("At least one input is required")
                    continue
                break
                
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(utxo_list):
                    (txid, idx), output = utxo_list[idx]
                    inputs.append({"txid": txid, "index": idx})
                    print(f"Added input: {txid}:{idx}")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Please enter a number")
        
        # Get outputs
        outputs = []
        print("\nEnter output details (address and amount):")
        while True:
            address = input("Address (or leave empty to finish): ").strip()
            if not address:
                if not outputs:
                    print("At least one output is required")
                    continue
                break
                
            try:
                amount = float(input("Amount (in BTC): "))
                if amount <= 0:
                    print("Amount must be positive")
                    continue
                outputs.append({
                    "address": address,
                    "amount": int(amount * 1e8)  # Convert to satoshis
                })
                print(f"Added output: {address} - {amount:.8f} BTC")
            except ValueError:
                print("Invalid amount")
        
        # Get fee rate
        while True:
            try:
                fee_rate = float(input("\nEnter fee rate (sat/byte): "))
                if fee_rate <= 0:
                    print("Fee rate must be positive")
                    continue
                break
            except ValueError:
                print("Please enter a valid number")
        
        # Create and add transaction
        tx = Transaction(
            txid=generate_txid(),
            inputs=inputs,
            outputs=outputs,
            fee_rate=fee_rate
        )
        
        success, message = mempool.add_transaction(tx, utxo_set)
        print(f"\n{'✓' if success else '✗'} {message}")
        if success:
            print(f"Transaction ID: {tx.txid}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"\nError: {str(e)}")

def mine_block(mempool, utxo_set):
    """Mine a block with the highest fee transactions."""
    try:
        max_size = input("Enter maximum block size in bytes (default: 1000000): ").strip()
        max_size = int(max_size) if max_size.isdigit() else 1000000
        
        txs = mempool.get_transactions_by_fee_rate()
        block_size = 0
        mined_txs = []
        
        for tx in txs:
            if block_size + tx.size > max_size:
                break
            mined_txs.append(tx)
            block_size += tx.size
        
        # In a real implementation, we'd create new UTXOs here
        for tx in mined_txs:
            mempool._remove_transaction(tx.txid)
        
        print(f"\nMined block with {len(mined_txs)} transactions ({block_size} bytes)")
        
    except Exception as e:
        print(f"Error mining block: {str(e)}")

def show_help():
    """Show help information."""
    print("\n" + "="*80)
    print("BITCOIN MEMPOOL SIMULATOR - HELP".center(80))
    print("="*80)
    print("\nAvailable Commands:")
    print(" 1. Show UTXOs")
    print(" 2. Show Mempool")
    print(" 3. Add Transaction")
    print(" 4. Mine Block")
    print(" 5. Clear Mempool")
    print(" 6. Help")
    print(" 0. Exit")
    print("\n" + "="*80 + "\n")

def main():
    print("\n" + "="*80)
    print("BITCOIN MEMPOOL SIMULATOR".center(80))
    print("Type 'help' for available commands".center(80))
    print("="*80 + "\n")
    
    # Initialize components
    utxo_set = UTXOSet()
    mempool = Mempool(max_size_mb=1.0)
    
    # Add sample UTXOs
    sample_utxos = [
        {'txid': 'prev_tx1', 'index': 0, 'address': 'addr1', 'amount': 1000000},
        {'txid': 'prev_tx1', 'index': 1, 'address': 'addr2', 'amount': 2000000},
        {'txid': 'prev_tx2', 'index': 0, 'address': 'addr3', 'amount': 1500000},
        {'txid': 'prev_tx3', 'index': 0, 'address': 'addr1', 'amount': 500000},
    ]
    
    for utxo in sample_utxos:
        utxo_set.add_utxo(
            utxo['txid'],
            utxo['index'],
            {'address': utxo['address'], 'amount': utxo['amount']}
        )
    
    # Main loop
    while True:
        try:
            print("\nEnter command (1-6, or 0 to exit):")
            print("1. Show UTXOs")
            print("2. Show Mempool")
            print("3. Add Transaction")
            print("4. Mine Block")
            print("5. Clear Mempool")
            print("6. Help")
            print("0. Exit")
            
            choice = input("\n> ").strip()
            
            if choice == '0':
                print("\nExiting...")
                break
            elif choice == '1':
                show_utxos(utxo_set)
            elif choice == '2':
                show_mempool(mempool)
            elif choice == '3':
                add_transaction(mempool, utxo_set)
            elif choice == '4':
                mine_block(mempool, utxo_set)
            elif choice == '5':
                mempool.clear()
                print("\nMempool cleared")
            elif choice == '6' or choice.lower() == 'help':
                show_help()
            else:
                print("\nInvalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\nUse '0' to exit or '6' for help")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
