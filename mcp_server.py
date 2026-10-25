#!/usr/bin/env python3
"""
Base Contract Auditor MCP Server
Model Context Protocol (MCP) server for Claude Desktop, Cursor, Antigravity, and Windsurf.
Provides on-chain Base contract auditing with free preview and verified 0.50 USDC x402 payment unlocking.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

GATEWAY_URL = os.environ.get("BASE_AUDIT_GATEWAY_URL", "http://185.166.214.127").rstrip("/")

def query_gateway(path, headers=None):
    url = f"{GATEWAY_URL}{path}"
    req_headers = {"User-Agent": "BaseContractAuditorMCP/2.0"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"error": f"HTTP {e.code}", "detail": raw}
    except Exception as e:
        return 503, {"error": f"Gateway unreachable: {str(e)}"}

TOOLS = [
    {
        "name": "preview_contract",
        "description": "Runs a FREE security preview on any smart contract on Base Mainnet. Returns bytecode metrics, risk score (0-100), and count of detected security alerts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {
                    "type": "string",
                    "description": "The 42-character 0x EVM smart contract address on Base Mainnet."
                }
            },
            "required": ["contract_address"]
        }
    },
    {
        "name": "audit_contract",
        "description": "Unlocks the FULL on-chain bytecode security audit report for 0.50 USDC on Base Mainnet. Provides detailed findings on SELFDESTRUCT, DELEGATECALL proxy logic, token signatures, and remediation advice.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {
                    "type": "string",
                    "description": "The 42-character 0x EVM smart contract address on Base Mainnet."
                },
                "tx_hash": {
                    "type": "string",
                    "description": "Base transaction hash confirming payment of at least 0.50 USDC to 0xbefe9ce194a3d685486e5fda11c5221146de4d6c."
                }
            },
            "required": ["contract_address", "tx_hash"]
        }
    },
    {
        "name": "get_payment_info",
        "description": "Returns official x402 payment requirements, receiving vault address, and official Base USDC contract address to unlock audits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {
                    "type": "string",
                    "description": "Optional smart contract address you plan to audit."
                }
            }
        }
    }
]

def handle_jsonrpc(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "base-contract-auditor-x402", "version": "2.0.0"}
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "preview_contract":
            contract = args.get("contract_address", "").strip()
            code, data = query_gateway(f"/api/audit-contract?address={urllib.parse.quote(contract)}")
            res = data.get("free_preview") or data
        elif tool_name == "audit_contract":
            contract = args.get("contract_address", "").strip()
            tx = args.get("tx_hash", "").strip()
            code, data = query_gateway(f"/api/audit-contract?address={urllib.parse.quote(contract)}", headers={"X-PAYMENT-TX": tx})
            res = data
        elif tool_name == "get_payment_info":
            contract = args.get("contract_address", "").strip()
            code, data = query_gateway(f"/api/audit-contract?address={urllib.parse.quote(contract)}" if contract else "/api/audit-contract")
            res = data
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
            }
        }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unsupported method: {method}"}}

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            resp = handle_jsonrpc(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
