# Bitcoin Mempool Simulator

A Python-based educational implementation of a Bitcoin-style mempool with transaction validation, fee prioritization, and basic mining simulation.

## Overview

This project simulates the behavior of a Bitcoin node's mempool, which is a temporary storage area for unconfirmed transactions. The mempool is a critical component of the Bitcoin network, responsible for:

- Validating incoming transactions
- Managing unconfirmed transactions
- Prioritizing transactions by fee rate
- Preventing double-spending
- Enabling Replace-By-Fee (RBF) functionality

## Key Features

- **UTXO-based Transaction Model**: Implements the Unspent Transaction Output model used by Bitcoin
- **Fee Prioritization**: Transactions are ordered by fee rate (satoshis per byte)
- **Mempool Management**: Implements size limits and eviction policies
- **Replace-By-Fee (RBF)**: Allows replacing transactions with higher-fee versions
- **CLI Interface**: Interactive command-line interface for testing and demonstration

## Architecture

The code is organized into modular components:

1. **transaction.py**: Defines the Transaction class and related functionality
2. **utxo.py**: Implements the UTXO (Unspent Transaction Output) set
3. **mempool.py**: Core mempool implementation with validation and prioritization
4. **main.py**: Command-line interface and demo functionality

## Why Mempools Are Not Part of Consensus

1. **Node Autonomy**: Each node maintains its own mempool independently
2. **Network Propagation**: Transactions propagate through the network asynchronously
3. **Temporary Storage**: Mempools are not part of the blockchain's permanent state
4. **Local Policy**: Nodes can implement different mempool policies (e.g., minimum fee requirements)

## Why Nodes Can Have Different Mempools

1. **Network Latency**: Transactions may reach nodes at different times
2. **Policy Differences**: Nodes may have different acceptance criteria
3. **Resource Constraints**: Nodes may have different memory limits
4. **Network Partitions**: Temporary network issues can cause inconsistencies

## Fee Rate Importance

Fee rate (satoshis per byte) determines:

1. **Transaction Priority**: Higher fee rate transactions are prioritized
2. **Block Inclusion**: Miners prefer transactions with higher fee rates
3. **Network Congestion**: During high traffic, only high-fee transactions get confirmed quickly
4. **Economic Security**: Fees incentivize miners to include transactions in blocks

## What Happens During Congestion

1. **Fee Market**: Users compete by offering higher fees
2. **Mempool Backlog**: Unconfirmed transactions accumulate
3. **Fee Spikes**: Average transaction fees increase
4. **Eviction**: Lowest fee transactions may be dropped from mempools

## Getting Started

1. Ensure you have Python 3.7+ installed
2. Clone this repository
3. Run the simulator:
   ```
   python main.py
   ```

## Example Usage

1. View available commands:
   ```
   help
   ```

2. View UTXOs:
   ```
   show_utxos
   ```

3. Add a transaction:
   ```
   add_tx {"inputs": [{"txid": "prev_tx1", "index": 0}], "outputs": [{"address": "addr2", "amount": 900000}], "fee_rate": 10}
   ```

4. View mempool:
   ```
   show_mempool
   ```

5. Mine a block:
   ```
   mine_top_block 1000000
   ```

## Limitations

This is an educational implementation and does not include:
- Cryptographic signatures
- Full Bitcoin scripting
- P2P network layer
- Real mining (PoW)
- Wallet functionality

## License

MIT License - Feel free to use this code for educational purposes.
