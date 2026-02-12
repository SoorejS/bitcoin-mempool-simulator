# Bitcoin Mempool Simulator

A Python implementation of Bitcoin-style mempool policy, demonstrating transaction validation, fee prioritization, and block construction logic as implemented in Bitcoin Core.

## Project Purpose

This project models mempool behavior as policy, distinct from consensus rules. It demonstrates how Bitcoin nodes manage unconfirmed transactions before they are included in blocks.

**Key Distinction**: Blocks determine consensus. The mempool determines transaction relay and prioritization according to node policy.

## 1. Validation Before Admission

Transactions must pass several checks before entering the mempool:

### Consensus Validation
- **UTXO Existence**: All inputs must reference unspent transaction outputs
- **No Double Spending**: Inputs cannot be spent elsewhere in the blockchain or mempool
- **Input ≥ Output**: Sum of input values must cover output values plus fees
- **Valid Signatures**: Cryptographic verification of transaction signatures (simulated)

### Mempool Policy Validation
- Minimum relay fee requirements
- Standard transaction formats
- Size limits
- Non-standard script verification

**Note**: A transaction can be valid by consensus but still rejected by mempool policy.

## 2. Fee Prioritization

### Fee Rate Calculation
- **Fee Rate** = Fee (in satoshis) / Virtual Size (in vbytes)
- This implementation uses a simplified size approximation

### Miner Incentives
- Miners maximize revenue by prioritizing higher fee rate transactions
- Fee rate determines transaction priority, not absolute fee amount
- Transactions are sorted by ancestor fee rate (feerate including unconfirmed dependencies)

## 3. Capacity & Eviction

### Mempool Limits
- Default size limit: 300MB (configurable)
- Individual transaction size limits
- Maximum number of transactions

### Eviction Policy
When the mempool reaches capacity:
1. Transactions are sorted by fee rate (lowest first)
2. Lowest fee rate transactions are evicted until enough space is available
3. All transactions depending on evicted transactions are also removed (unconfirmed dependencies)

**Important**: Mempool contents can vary between nodes due to different policies and network conditions.

## 4. Replace-By-Fee (RBF)

### Purpose
- Allows increasing fees for stuck transactions
- Enables fee bumping without double-spending

### Replacement Rules
A transaction can replace an existing one if:
1. It spends all the same inputs
2. Pays higher absolute fees
3. Meets minimum fee increase requirements
4. Doesn't create any new unconfirmed dependencies

## 5. Mining Simulation

### Block Construction
1. Selects transactions by descending fee rate
2. Respects block size limits
3. Updates UTXO set for mined transactions
4. Removes included transactions from mempool

### Key Distinction
- **Mining**: Economic activity to extend the blockchain
- **Validation**: Cryptographic verification of transaction validity

## 6. Policy vs Consensus

### Consensus Rules
- Must be identical across all nodes
- Determine valid blocks and transactions
- Enforced by full node validation
- Changes require careful network-wide coordination and activation mechanisms 

### Policy Rules
- Can vary between node implementations
- Govern transaction relay and mempool behavior
- Include fee requirements, size limits, and DoS protections
- Can be updated without network coordination

**Critical Insight**: Mempool differences do not cause blockchain forks. Only invalid blocks can create consensus splits.

## 7. Implementation Details

### Core Components
- `mempool.py`: Mempool implementation with validation and prioritization
- `transaction.py`: Transaction data structure and validation
- `utxo.py`: Unspent Transaction Output set management
- `simple_run.py`: Interactive command-line interface

**Note on Bitcoin Core Implementation**: In Bitcoin Core, mempool policy is implemented primarily in `policy/` and `validation.cpp`. This project models the separation between mempool policy and consensus validation at a conceptual level.

### Key Design Decisions
- Simplified fee estimation
- Conservative DoS protections
- Prioritization by ancestor fee rate
- Configurable size limits (Bitcoin Core defaults to 300MB)
- Simplified standardness checks (no full Bitcoin Script implementation)

### Simplifications
This educational implementation does not include:
- Orphan transaction pool
- Full ancestor/descendant tracking graph
- Package relay
- CPFP (Child-Pays-For-Parent) modeling
- Mempool persistence to disk
- Full Bitcoin Script implementation
- P2P network layer
- Cryptographic signature verification
- Real proof-of-work mining

## What I Learned

### Key Insights
1. **Mempool Isolation**: Mempools are not globally synchronized and can differ between nodes
2. **Fee Market Dynamics**: Network congestion leads to natural fee market formation
3. **Resource Management**: Mempool limits prevent resource exhaustion attacks
4. **Miner Incentives**: Miners act economically rationally to maximize fee revenue
5. **Policy Flexibility**: Nodes can implement different policies without affecting consensus

## Getting Started

### Prerequisites
- Python 3.7+
- No additional dependencies required

### Running the Simulator
```bash
python simple_run.py
```

## License

MIT License - For educational and research purposes. Not intended for production use.
