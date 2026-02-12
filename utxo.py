class UTXOSet:
    """
    Manages the set of Unspent Transaction Outputs (UTXOs).
    """
    def __init__(self):
        # Maps (txid, index) to output details
        self.utxos = {}
    
    def add_utxo(self, txid, index, output):
        """Add a new UTXO to the set."""
        self.utxos[(txid, index)] = output
    
    def spend_utxo(self, txid, index):
        """Mark a UTXO as spent and return it if it exists."""
        return self.utxos.pop((txid, index), None)
    
    def get_utxo(self, txid, index):
        """Get a UTXO if it exists and is unspent."""
        return self.utxos.get((txid, index))
    
    def validate_inputs(self, inputs):
        """
        Validate that all inputs exist in the UTXO set.
        
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        for inp in inputs:
            if (inp['txid'], inp['index']) not in self.utxos:
                return False, f"Input {inp['txid']}:{inp['index']} not found in UTXO set"
        return True, ""
    
    def get_balance(self, address):
        """Get total balance for a given address."""
        return sum(
            output['amount'] 
            for output in self.utxos.values() 
            if output['address'] == address
        )
    
    def __len__(self):
        return len(self.utxos)
    
    def __repr__(self):
        return f"<UTXOSet: {len(self)} unspent outputs>"
