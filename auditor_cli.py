#!/usr/bin/env python3
"""
Base Contract Auditor CLI (x402 Web3 Protocol)
Automated on-chain smart contract bytecode security analysis on Base Mainnet.
Supports:
1. Free Preview Mode: Instant risk score, bytecode metrics, and detected alert count.
2. Deep Opcode Audit: Full breakdown of SELFDESTRUCT, DELEGATECALL, ownership backdoors for 0.50 USDC via x402.

Gateway Endpoint: http://185.166.214.127/api/audit-contract
Official Base Vault: 0xbefe9ce194a3d685486e5fda11c5221146de4d6c
Official Base USDC: 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import urllib.parse

DEFAULT_GATEWAY = os.environ.get("BASE_AUDIT_GATEWAY_URL", "http://185.166.214.127").rstrip("/")

def call_api(path, method="GET", headers=None, body=None, timeout=15):
    url = f"{DEFAULT_GATEWAY}{path}"
    req_headers = {"User-Agent": "BaseContractAuditorCLI/2.0"}
    if headers:
        req_headers.update(headers)
    data = json.dumps(body).encode("utf-8") if body else None
    if body and "Content-Type" not in req_headers:
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"error": f"HTTP {e.code}", "detail": raw}
    except Exception as e:
        return 503, {"error": f"Connection error: {str(e)}"}

def cmd_preview(contract_address):
    """Executes the free preview analysis."""
    path = f"/api/audit-contract?address={urllib.parse.quote(contract_address)}"
    code, data = call_api(path, method="GET")

    preview = data.get("free_preview")
    if preview:
        print("\n" + "="*60)
        print("  BASE MAINNET SMART CONTRACT AUDIT (FREE PREVIEW)")
        print("="*60)
        print(f" Target Contract:       {contract_address}")
        print(f" Is Contract Bytecode:  {preview.get('is_contract')}")
        print(f" Bytecode Size:         {preview.get('bytecode_size_bytes')} bytes")
        print(f" Risk Level:            {preview.get('risk_level')}")
        print(f" Risk Score:            {preview.get('risk_score')}/100")
        print(f" Security Alerts Found: {preview.get('alerts_detected_count')}")
        print("-" * 60)
        print(" 🔒 FULL REPORT LOCKED (Findings & Opcode breakdown)")
        print(f" Price to unlock:       0.50 USDC on Base Mainnet")
        print(f" Vault Recipient:       {data.get('vault_evm_base')}")
        print(f" Instruction:           Send 0.50 USDC to vault and run:")
        print(f"   python auditor_cli.py audit {contract_address} --tx <tx_hash>")
        print("="*60 + "\n")
    else:
        print(json.dumps(data, indent=2))

def cmd_audit(contract_address, tx_hash):
    """Executes the complete verified security audit."""
    path = f"/api/audit-contract?address={urllib.parse.quote(contract_address)}"
    headers = {"X-PAYMENT-TX": tx_hash}
    code, data = call_api(path, method="GET", headers=headers)

    if code == 200:
        report = data.get("audit_report", {})
        print("\n" + "="*60)
        print("  BASE MAINNET DEEP SECURITY AUDIT (VERIFIED ON-CHAIN)")
        print("="*60)
        print(f" Payment Status:  {data.get('payment_status')} ({data.get('amount_paid_usdc')} USDC)")
        print(f" Transaction:     {data.get('tx_hash')}")
        print(f" Target Contract: {report.get('address')}")
        print(f" Verdict:         {report.get('verdict')}")
        print(f" Risk Score:      {report.get('risk_score')}/100 ({report.get('risk_level')})")
        print("-" * 60)
        print(" Detailed Security Findings:")
        for f in report.get("findings", []):
            print(f"   {f}")
        print("="*60 + "\n")
    else:
        print(f"\n[!] Audit Verification Failed (HTTP {code}):")
        print(json.dumps(data, indent=2) + "\n")

def cmd_status():
    code, data = call_api("/status")
    print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Base Contract Auditor CLI (x402 Protocol)")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Preview
    prev_parser = subparsers.add_parser("preview", help="Run free security preview")
    prev_parser.add_argument("contract", help="0x contract address on Base")

    # Audit
    audit_parser = subparsers.add_parser("audit", help="Run full audit with payment tx hash")
    audit_parser.add_argument("contract", help="0x contract address on Base")
    audit_parser.add_argument("--tx", required=True, help="Base transaction hash of 0.50 USDC payment")

    # Status
    subparsers.add_parser("status", help="Check gateway status and health")

    args = parser.parse_args()
    if args.subcommand == "preview":
        cmd_preview(args.contract)
    elif args.subcommand == "audit":
        cmd_audit(args.contract, args.tx)
    elif args.subcommand == "status":
        cmd_status()

if __name__ == "__main__":
    main()
