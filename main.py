import cmd
import json
import random
import string
import sys
from typing import Dict, List, Optional

from mempool import Mempool
from transaction import Transaction
from utxo import UTXOSet

class MempoolCLI(cmd.Cmd):
    """Command-line interface for the Bitcoin mempool simulator."""
    
    prompt = 'mempool> '
    
    def __init__(self):
        super().__init__()
        self.utxo_set = UTXOSet()
        self.mempool = Mempool(max_size_mb=1.0)  # 1MB mempool
        self._initialize_sample_utxos()
    
    def _initialize_sample_utxos(self):
        """Initialize some sample UTXOs for testing."""
        # Add some sample UTXOs
        sample_utxos = [
            {'txid': 'prev_tx1', 'index': 0, 'address': 'addr1', 'amount': 1000000},
            {'txid': 'prev_tx1', 'index': 1, 'address': 'addr2', 'amount': 2000000},
            {'txid': 'prev_tx2', 'index': 0, 'address': 'addr3', 'amount': 1500000},
            {'txid': 'prev_tx3', 'index': 0, 'address': 'addr1', 'amount': 500000},
        ]
        
        for utxo in sample_utxos:
            self.utxo_set.add_utxo(
                utxo['txid'],
                utxo['index'],
                {'address': utxo['address'], 'amount': utxo['amount']}
            )
    
    def do_add_tx(self, arg):
        """Add a transaction to the mempool.
        
        Example: add_tx {"inputs": [{"txid": "prev_tx1", "index": 0}], 
                 "outputs": [{"address": "addr2", "amount": 900000}], 
                 "fee_rate": 10}
        """
        try:
            if not arg:
                print("Error: Transaction data required")
                return
                
            data = json.loads(arg)
            txid = self._generate_txid()
            
            tx = Transaction(
                txid=txid,
                inputs=data['inputs'],
                outputs=data['outputs'],
                fee_rate=float(data.get('fee_rate', 1.0))
            )
            
            success, message = self.mempool.add_transaction(tx, self.utxo_set)
            if success:
                print(f"✓ {message}")
                print(f"  TXID: {txid}")
            else:
                print(f"✗ {message}")
                
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def do_show_mempool(self, _):
        """Show all transactions in the mempool."""
        print("\n" + "="*80)
        print("MEMPOOL OVERVIEW".center(80))
        print("="*80)
        
        # Show mempool info
        info = self.mempool.get_mempool_info()
        print(f"Transactions: {info['tx_count']}")
        print(f"Size: {info['bytes']} ({info['usage']} of {info['max_size']})")
        
        # Show transactions sorted by fee rate
        print("\nTRANSACTIONS (sorted by fee rate):")
        print("-" * 80)
        
        txs = self.mempool.get_transactions_by_fee_rate()
        if not txs:
            print("  Mempool is empty")
        else:
            for i, tx in enumerate(txs, 1):
                print(f"{i:3}. {tx.txid[:8]}... | Fee rate: {tx.fee_rate:>6.1f} sat/byte | Size: {tx.size:>5} bytes")
                print(f"     Inputs:  {len(tx.inputs)}")
                print(f"     Outputs: {len(tx.outputs)}")
        
        print("="*80 + "\n")
    
    def do_mine_top_block(self, arg):
        """Mine a block with the highest fee transactions."""
        try:
            max_size = int(arg) if arg.isdigit() else 1_000_000  # Default 1MB block
            txs = self.mempool.get_transactions_by_fee_rate()
            
            block_size = 0
            mined_txs = []
            
            for tx in txs:
                if block_size + tx.size > max_size:
                    break
                mined_txs.append(tx)
                block_size += tx.size
            
            # Update UTXO set (in a real implementation, this would create new UTXOs)
            for tx in mined_txs:
                self.mempool._remove_transaction(tx.txid)
            
            print(f"Mined block with {len(mined_txs)} transactions ({block_size} bytes)")
            
        except Exception as e:
            print(f"Error mining block: {str(e)}")
    
    def do_clear_mempool(self, _):
        """Clear all transactions from the mempool."""
        self.mempool.clear()
        print("Mempool cleared")
    
    def do_show_utxos(self, _):
        """Show all UTXOs in the UTXO set."""
        print("\n" + "="*80)
        print("UTXO SET OVERVIEW".center(80))
        print("="*80)
        
        if not hasattr(self.utxo_set, 'utxos') or not self.utxo_set.utxos:
            print("No UTXOs in the set")
            return
        
        for (txid, idx), output in self.utxo_set.utxos.items():
            print(f"{txid[:8]}...:{idx:<3} -> {output['address']}: {output['amount']/1e8:.8f} BTC")
        
        print("="*80 + "\n")
    
    def do_help(self, arg):
        """Show help information."""
        print("\nBitcoin Mempool Simulator - Available Commands:")
        print("-" * 60)
        print("add_tx <tx_json>     Add a transaction to the mempool")
        print("show_mempool         Show all transactions in the mempool")
        print("mine_top_block [size] Mine a block (optional size in bytes)")
        print("clear_mempool        Clear all transactions from mempool")
        print("show_utxos           Show all UTXOs in the UTXO set")
        print("help                 Show this help message")
        print("exit                 Exit the program")
        print("\nExample transaction:")
        print('''{"inputs": [{"txid": "prev_tx1", "index": 0}], 
 "outputs": [{"address": "addr2", "amount": 900000}], 
 "fee_rate": 10}''')
    
    def do_exit(self, _):
        """Exit the program."""
        print("Exiting mempool simulator. Goodbye!")
        return True
    
    def _generate_txid(self, length=32):
        """Generate a random transaction ID."""
        return ''.join(random.choices('0123456789abcdef', k=length))

if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("BITCOIN MEMPOOL SIMULATOR".center(60))
        print("Type 'help' for available commands".center(60))
        print("="*60 + "\n")
        
        cli = MempoolCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")
