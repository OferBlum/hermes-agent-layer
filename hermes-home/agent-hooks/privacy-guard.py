#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hermes adapter for the vault's privacy guard.

Copy to ~/.hermes/agent-hooks/privacy-guard.py and register it in ~/.hermes/config.yaml
under hooks.pre_tool_call (matcher ".*", fail_closed: true).

The policy is not here. It lives in the vault, in one file shared by every runtime
(see vault-privacy-guard):

    <vault>/0 - System/scripts/privacy_guard.py

This file only loads that policy and speaks Hermes' contract: the tool payload on
stdin, then {"decision": "block", "reason": ...} or {} on stdout, exit 0.

Fails CLOSED. If the policy can't be found or loaded (the vault moved, an iCloud
file was evicted, a syntax error), every tool call is blocked until it's fixed.
An agent that can't check the rule doesn't get to guess. Set fail_closed: true in
the config too, so a crash or timeout of this script also blocks.

Set HERMES_VAULT to your vault's absolute path.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

SYSTEM_DIR = "0 - System"
POLICY_FILE = Path(SYSTEM_DIR) / "scripts" / "privacy_guard.py"


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def main():
    vault = os.environ.get("HERMES_VAULT")
    if not vault:
        return block("privacy guard: HERMES_VAULT is not set")
    policy = Path(vault) / POLICY_FILE
    if not policy.is_file():
        return block("privacy guard: policy file not found")
    try:
        spec = importlib.util.spec_from_file_location("privacy_guard", policy)
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        return guard.run_hermes(sys.stdin.read())
    except Exception:
        return block("privacy guard: policy failed to load")


if __name__ == "__main__":
    sys.exit(main())
