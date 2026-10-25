# Base Contract Auditor x402 (`base-contract-auditor-x402`)

[![Network: Base Mainnet](https://img.shields.io/badge/Network-Base_Mainnet_(8453)-0052FF.svg)](https://base.org)
[![Payment Standard: x402](https://img.shields.io/badge/Payment-x402_Micropayments-green.svg)](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.3)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![MCP Ready](https://img.shields.io/badge/MCP-Model_Context_Protocol-8A2BE2.svg)](https://modelcontextprotocol.io/)

Production-grade **Model Context Protocol (MCP)** server and standalone CLI client for automated on-chain smart contract bytecode security auditing on **Base Mainnet**.

Features a **Free Preview Mode** (instant risk score & alert count) and deep vulnerability inspection unlocked via the **x402 Micropayment Protocol** for **0.50 USDC**.

---

## ⚡ Quick Start

### 1. Free Security Preview (No Payment Required)
Run instant risk scoring on any contract deployed on Base:
```bash
python3 auditor_cli.py preview 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913
```

**Preview Output:**
```text
============================================================
  BASE MAINNET SMART CONTRACT AUDIT (FREE PREVIEW)
============================================================
 Target Contract:       0x833589fcd6edb6e08f4c7c32d4f71b54bda02913
 Is Contract Bytecode:  True
 Bytecode Size:         2412 bytes
 Risk Level:            MEDIUM
 Risk Score:            30/100
 Security Alerts Found: 2
------------------------------------------------------------
 🔒 FULL REPORT LOCKED (Findings & Opcode breakdown)
 Price to unlock:       0.50 USDC on Base Mainnet
 Vault Recipient:       0xbefe9ce194a3d685486e5fda11c5221146de4d6c
============================================================
```

### 2. Deep Opcode Audit (0.50 USDC via x402)
Send **0.50 USDC** on Base Mainnet to our official auditor vault:
- **Auditor Vault:** `0xbefe9ce194a3d685486e5fda11c5221146de4d6c`
- **Base USDC Contract:** `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913`

Once confirmed on Base, run:
```bash
python3 auditor_cli.py audit 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 --tx 0x4f12ab...
```

The gateway verifies the `Transfer` log on-chain, prevents replay attacks with SQLite WAL recording, and outputs the full opcode audit report!

---

## 🤖 MCP Configuration (Claude Desktop, Cursor, Antigravity)

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "base-contract-auditor": {
      "command": "python3",
      "args": [
        "/absolute/path/to/base-contract-auditor-x402/mcp_server.py"
      ],
      "env": {
        "BASE_AUDIT_GATEWAY_URL": "http://185.166.214.127:8402"
      }
    }
  }
}
```

### Exposed MCP Tools:
- `preview_contract`: Runs free preview risk scoring.
- `audit_contract`: Unlocks complete vulnerability findings with valid transaction hash.
- `get_payment_info`: Queries current x402 payment requirements.

---

## 🛡️ Security Checks Included
- `SELFDESTRUCT` (0xFF) drainage exploits.
- `DELEGATECALL` (0xF4) upgradeable proxy risks.
- Interface compliance (`ERC-20`, `ERC-721`).
- Centralized administrative / owner backdoors (`owner`, `transferOwnership`).

## 📄 License
MIT License. Copyright (c) 2026 ossamartinaaron09-ui.
