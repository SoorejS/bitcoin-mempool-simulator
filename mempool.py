from typing import Dict, List, Set, Tuple
from transaction import Transaction

class Mempool:
    """
    A Bitcoin-style mempool that manages unconfirmed transactions.
    Implements fee-based transaction prioritization and eviction.
    """
    def __init__(self, max_size_mb: float = 1.0):
        """
        Initialize the mempool with a maximum size in MB.
        
        Args:
            max_size_mb: Maximum size of the mempool in megabytes
        """
        self.max_size = int(max_size_mb * 1_000_000)  # Convert MB to bytes
        self.current_size = 0
        # Maps txid to Transaction object
        self.transactions: Dict[str, Transaction] = {}
        # Tracks which UTXOs are spent by mempool transactions
        self.spent_utxos: Set[Tuple[str, int]] = set()
        # Maps UTXOs to the transactions that spend them
        self.utxo_to_tx: Dict[Tuple[str, int], str] = {}
    
    def add_transaction(self, tx: Transaction, utxo_set) -> Tuple[bool, str]:
        """
        Add a transaction to the mempool if it's valid.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # 1. Check if transaction already exists
        if tx.txid in self.transactions:
            return False, "Transaction already in mempool"
        
        # 2. Check for double spends within mempool
        for inp in tx.inputs:
            utxo_key = (inp['txid'], inp['index'])
            if utxo_key in self.spent_utxos:
                # Check if this is an RBF (Replace-By-Fee) case
                if not self._is_valid_rbf(tx, utxo_key):
                    return False, f"Double spend attempt: {utxo_key}"
        
        # 3. Validate against UTXO set
        valid, msg = utxo_set.validate_inputs(tx.inputs)
        if not valid:
            return False, f"Invalid inputs: {msg}"
        
        # 4. Check if transaction would exceed mempool size
        if self.current_size + tx.size > self.max_size:
            # Try to evict low-fee transactions to make space
            if not self._evict_for_space(tx.size):
                return False, "Mempool full and cannot evict enough transactions"
        
        # 5. If this is an RBF, remove the old transaction first
        for inp in tx.inputs:
            utxo_key = (inp['txid'], inp['index'])
            if utxo_key in self.utxo_to_tx:
                old_txid = self.utxo_to_tx[utxo_key]
                self._remove_transaction(old_txid)
        
        # 6. Add the transaction
        self.transactions[tx.txid] = tx
        self.current_size += tx.size
        
        # 7. Update spent UTXO tracking
        for inp in tx.inputs:
            utxo_key = (inp['txid'], inp['index'])
            self.spent_utxos.add(utxo_key)
            self.utxo_to_tx[utxo_key] = tx.txid
        
        return True, "Transaction added to mempool"
    
    def _is_valid_rbf(self, new_tx: Transaction, utxo_key: Tuple[str, int]) -> bool:
        """Check if a transaction is a valid RBF replacement."""
        old_txid = self.utxo_to_tx.get(utxo_key)
        if not old_txid:
            return False
            
        old_tx = self.transactions.get(old_txid)
        if not old_tx:
            return False
            
        # Basic RBF rule: New transaction must have higher fee rate
        return new_tx.fee_rate > old_tx.fee_rate
    
    def _evict_for_space(self, required_space: int) -> bool:
        """Evict lowest fee-rate transactions to make space."""
        # Sort transactions by fee rate (ascending)
        sorted_txs = sorted(
            self.transactions.values(),
            key=lambda tx: tx.fee_rate
        )
        
        space_freed = 0
        for tx in sorted_txs:
            if self.current_size - space_freed + required_space <= self.max_size:
                break
                
            self._remove_transaction(tx.txid)
            space_freed += tx.size
        
        return (self.current_size + required_space) <= self.max_size
    
    def _remove_transaction(self, txid: str):
        """Remove a transaction from the mempool."""
        if txid not in self.transactions:
            return
            
        tx = self.transactions[txid]
        self.current_size -= tx.size
        
        # Update spent UTXO tracking
        for inp in tx.inputs:
            utxo_key = (inp['txid'], inp['index'])
            self.spent_utxos.discard(utxo_key)
            self.utxo_to_tx.pop(utxo_key, None)
        
        del self.transactions[txid]
    
    def get_transactions_by_fee_rate(self, limit: int = None) -> List[Transaction]:
        """Get transactions sorted by fee rate (highest first)."""
        txs = sorted(
            self.transactions.values(),
            key=lambda tx: tx.fee_rate,
            reverse=True
        )
        return txs[:limit] if limit is not None else txs
    
    def get_mempool_info(self) -> dict:
        """Get mempool statistics."""
        return {
            'size': self.current_size,
            'bytes': f"{self.current_size:,} bytes",
            'max_size': f"{self.max_size:,} bytes",
            'usage': f"{(self.current_size / self.max_size * 100):.1f}%",
            'tx_count': len(self.transactions)
        }
    
    def clear(self):
        """Clear all transactions from the mempool."""
        self.transactions.clear()
        self.spent_utxos.clear()
        self.utxo_to_tx.clear()
        self.current_size = 0
    
    def __repr__(self) -> str:
        info = self.get_mempool_info()
        return (
            f"<Mempool: {info['tx_count']} transactions, "
            f"{info['bytes']} ({info['usage']} of {info['max_size']})>"
        )
