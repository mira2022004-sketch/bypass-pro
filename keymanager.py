#!/usr/bin/env python3
"""
Bypass Pro - Gerenciador de Chaves via GitHub
Uso: python keymanager.py <comando> [opcoes]

Comandos:
  generate   Gera novas chaves
  list       Lista todas as chaves
  revoke     Revoga uma chave
  extend     Estende a expiracao de uma chave
  unbind     Desvincula hardware de uma chave

Exemplos:
  python keymanager.py generate --days 30 --count 5
  python keymanager.py list
  python keymanager.py revoke ABCDE-12345-FGHIJ-67890
  python keymanager.py extend ABCDE-12345-FGHIJ-67890 --days 15
"""

import os
import sys
import json
import base64
import hashlib
import random
import string
import argparse
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Instalando dependencia 'requests'...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests

# ============================================================
# CONFIGURACAO - ALTERE AQUI!
# ============================================================
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or "ghp_xxxxxxxxxxxxxxxxxxxx"
GITHUB_OWNER = "mira2022004-sketch"
GITHUB_REPO = "bypass-pro"
KEYS_FILE = "keys.json"
# ============================================================

API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def generate_key():
    chars = string.ascii_uppercase + string.digits
    key = ""
    for i in range(20):
        key += random.choice(chars)
        if i in (4, 9, 14):
            key += "-"
    return key


def get_keys_file():
    r = requests.get(f"{API_BASE}/contents/{KEYS_FILE}", headers=HEADERS)
    if r.status_code == 404:
        return {}, None
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode()
    return json.loads(content), data["sha"]


def save_keys_file(keys, sha):
    content = json.dumps(keys, indent=2, ensure_ascii=False)
    encoded = base64.b64encode(content.encode()).decode()
    payload = {
        "message": f"keymanager: atualiza {KEYS_FILE}",
        "content": encoded,
        "sha": sha
    }
    r = requests.put(f"{API_BASE}/contents/{KEYS_FILE}", json=payload, headers=HEADERS)
    if r.status_code == 409:
        print("ERRO: Conflito - o arquivo foi modificado. Tente novamente.")
        return False
    r.raise_for_status()
    return True


def cmd_generate(args):
    keys, sha = get_keys_file()
    if keys is None:
        keys = {}

    generated = []
    for _ in range(args.count):
        while True:
            key = generate_key()
            if key not in keys:
                break
        created = datetime.utcnow()
        expires = created + timedelta(days=args.days)
        keys[key] = {
            "created": created.strftime("%Y-%m-%d"),
            "expires": expires.strftime("%Y-%m-%d"),
            "days": args.days,
            "hardware": None,
            "revoked": False,
            "notes": args.notes or ""
        }
        generated.append(key)

    if save_keys_file(keys, sha):
        print(f"\n=== {len(generated)} chave(s) gerada(s) ===\n")
        for i, k in enumerate(generated, 1):
            print(f"{i}. {k}  (expira: {keys[k]['expires']})")
        print("")
    else:
        print("Falha ao salvar.")


def cmd_list(args):
    keys, _ = get_keys_file()
    if not keys:
        print("Nenhuma chave encontrada.")
        return

    now = datetime.utcnow()
    print(f"\n{'CHAVE':<30} {'CRIADA':<12} {'EXPIRA':<12} {'DIAS':<6} {'HARDWARE':<12} {'STATUS'}")
    print("=" * 100)
    for k, v in sorted(keys.items(), key=lambda x: x[1]["created"], reverse=True):
        expires = datetime.strptime(v["expires"], "%Y-%m-%d")
        expired = expires < now
        hardware = v.get("hardware") or "---"
        hw_short = hardware[:8] + "..." if hardware and len(hardware) > 8 else hardware
        status = "REVOGADA" if v.get("revoked") else ("EXPIRADA" if expired else "ATIVA")
        print(f"{k:<30} {v['created']:<12} {v['expires']:<12} {v['days']:<6} {hw_short:<12} {status}")
    print("")


def cmd_revoke(args):
    keys, sha = get_keys_file()
    if args.key not in keys:
        print(f"Chave {args.key} nao encontrada.")
        return
    keys[args.key]["revoked"] = True
    if save_keys_file(keys, sha):
        print(f"Chave {args.key} revogada com sucesso.")
    else:
        print("Falha ao salvar.")


def cmd_extend(args):
    keys, sha = get_keys_file()
    if args.key not in keys:
        print(f"Chave {args.key} nao encontrada.")
        return
    current_expires = datetime.strptime(keys[args.key]["expires"], "%Y-%m-%d")
    new_expires = current_expires + timedelta(days=args.days)
    keys[args.key]["expires"] = new_expires.strftime("%Y-%m-%d")
    keys[args.key]["days"] += args.days
    if save_keys_file(keys, sha):
        print(f"Chave {args.key} estendida ate {keys[args.key]['expires']}.")
    else:
        print("Falha ao salvar.")


def cmd_unbind(args):
    keys, sha = get_keys_file()
    if args.key not in keys:
        print(f"Chave {args.key} nao encontrada.")
        return
    if keys[args.key]["hardware"]:
        old = keys[args.key]["hardware"]
        keys[args.key]["hardware"] = None
        if save_keys_file(keys, sha):
            print(f"Chave {args.key}: hardware '{old[:8]}...' desvinculado.")
        else:
            print("Falha ao salvar.")
    else:
        print(f"Chave {args.key} nao possui hardware vinculado.")


def main():
    parser = argparse.ArgumentParser(description="Gerenciador de Chaves Bypass Pro")
    sub = parser.add_subparsers(dest="command")

    p_gen = sub.add_parser("generate", help="Gerar novas chaves")
    p_gen.add_argument("--days", type=int, default=30, help="Dias de validade (padrao: 30)")
    p_gen.add_argument("--count", type=int, default=1, help="Quantidade de chaves (padrao: 1)")
    p_gen.add_argument("--notes", default="", help="Observacao opcional")

    p_revoke = sub.add_parser("revoke", help="Revogar uma chave")
    p_revoke.add_argument("key", help="Chave a revogar")

    p_extend = sub.add_parser("extend", help="Estender expiracao de uma chave")
    p_extend.add_argument("key", help="Chave a estender")
    p_extend.add_argument("--days", type=int, required=True, help="Dias adicionais")

    p_unbind = sub.add_parser("unbind", help="Desvincular hardware de uma chave")
    p_unbind.add_argument("key", help="Chave para desvincular")

    sub.add_parser("list", help="Listar todas as chaves")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "revoke":
        cmd_revoke(args)
    elif args.command == "extend":
        cmd_extend(args)
    elif args.command == "unbind":
        cmd_unbind(args)


if __name__ == "__main__":
    main()
