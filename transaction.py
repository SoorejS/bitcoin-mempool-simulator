class Transaction:
    """
    Represents a Bitcoin-style transaction with inputs and outputs.
    """
    def __init__(self, txid, inputs, outputs, fee_rate):
        """
        Initialize a transaction.
        
        Args:
            txid (str): Unique transaction ID
            inputs (list): List of input dictionaries with txid and index
            outputs (list): List of output dictionaries with address and amount
            fee_rate (float): Fee rate in satoshis per byte (approximate)
        """
        self.txid = txid
        self.inputs = inputs  # List of {'txid': str, 'index': int}
        self.outputs = outputs  # List of {'address': str, 'amount': int}
        self.fee_rate = fee_rate
        self.size = self._estimate_size()
    
    def _estimate_size(self):
        """Estimate transaction size in bytes (simplified)"""
        # Rough estimation: 10 bytes per input, 34 bytes per output
        input_size = len(self.inputs) * 10
        output_size = len(self.outputs) * 34
        return input_size + output_size + 10  # +10 for overhead
    
    def __repr__(self):
        return f"Transaction({self.txid[:8]}..., fee_rate={self.fee_rate} sat/byte)"
