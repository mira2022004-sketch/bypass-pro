#!/usr/bin/env python3
import os, sys, json, base64, hashlib, random, string
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests")
    import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or ""
GITHUB_OWNER = "mira2022004-sketch"
GITHUB_REPO = "bypass-pro"
KEYS_FILE = "keys.json"
API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}


def generate_key():
    chars = string.ascii_uppercase + string.digits
    key = ""
    for i in range(20):
        key += random.choice(chars)
        if i in (4, 9, 14): key += "-"
    return key


def get_keys():
    r = requests.get(f"{API_BASE}/contents/{KEYS_FILE}", headers=HEADERS)
    if r.status_code == 404: return {}, None
    r.raise_for_status()
    d = r.json()
    return json.loads(base64.b64decode(d["content"])), d["sha"]


def save_keys(keys, sha):
    content = json.dumps(keys, indent=2, ensure_ascii=False)
    payload = {
        "message": "keymanager: atualiza keys.json",
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }
    r = requests.put(f"{API_BASE}/contents/{KEYS_FILE}", json=payload, headers=HEADERS)
    if r.status_code == 409:
        input("ERRO: Conflito - arquivo modificado. Pressione Enter...")
        return False
    r.raise_for_status()
    return True


def menu_gerar():
    print("\n--- GERAR CHAVES ---")
    try:
        dias = int(input("Dias de validade (padrao 30): ") or "30")
        qtd = int(input("Quantidade de chaves (padrao 1): ") or "1")
    except:
        input("Valor invalido. Pressione Enter..."); return

    keys, sha = get_keys()
    if keys is None: keys = {}
    geradas = []

    for _ in range(qtd):
        while True:
            k = generate_key()
            if k not in keys: break
        exp = (datetime.utcnow() + timedelta(days=dias)).strftime("%Y-%m-%d")
        keys[k] = {"created": datetime.utcnow().strftime("%Y-%m-%d"), "expires": exp,
                    "days": dias, "hardware": None, "revoked": False, "notes": ""}
        geradas.append(k)

    if save_keys(keys, sha):
        print(f"\n=== {len(geradas)} chave(s) gerada(s) ===")
        for i, k in enumerate(geradas, 1):
            print(f"{i}. {k}  (expira: {keys[k]['expires']})")
    input("\nPressione Enter...")


def menu_listar():
    keys, _ = get_keys()
    if not keys:
        input("Nenhuma chave encontrada. Pressione Enter..."); return

    now = datetime.utcnow()
    print(f"\n{'CHAVE':<30} {'CRIADA':<12} {'EXPIRA':<12} {'HARDWARE':<10} {'STATUS'}")
    print("=" * 76)
    for k, v in sorted(keys.items(), key=lambda x: x[1]["created"], reverse=True):
        exp = datetime.strptime(v["expires"], "%Y-%m-%d")
        hw = (v.get("hardware") or "---")[:8]
        st = "REVOGADA" if v.get("revoked") else ("EXPIRADA" if exp < now else "ATIVA")
        print(f"{k:<30} {v['created']:<12} {v['expires']:<12} {hw:<10} {st}")
    input("\nPressione Enter...")


def menu_revogar():
    chave = input("\nChave a revogar: ").strip().upper()
    keys, sha = get_keys()
    if chave not in keys:
        input("Chave nao encontrada. Pressione Enter..."); return
    keys[chave]["revoked"] = True
    if save_keys(keys, sha):
        print(f"Chave {chave} revogada.")
    input("Pressione Enter...")


def menu_estender():
    chave = input("\nChave a estender: ").strip().upper()
    keys, sha = get_keys()
    if chave not in keys:
        input("Chave nao encontrada. Pressione Enter..."); return
    try:
        dias = int(input("Dias adicionais: "))
    except:
        input("Valor invalido. Pressione Enter..."); return
    exp = datetime.strptime(keys[chave]["expires"], "%Y-%m-%d") + timedelta(days=dias)
    keys[chave]["expires"] = exp.strftime("%Y-%m-%d")
    keys[chave]["days"] += dias
    if save_keys(keys, sha):
        print(f"Chave {chave} estendida ate {keys[chave]['expires']}.")
    input("Pressione Enter...")


def menu_desvincular():
    chave = input("\nChave para desvincular hardware: ").strip().upper()
    keys, sha = get_keys()
    if chave not in keys:
        input("Chave nao encontrada. Pressione Enter..."); return
    if keys[chave].get("hardware"):
        old = keys[chave]["hardware"]
        keys[chave]["hardware"] = None
        if save_keys(keys, sha):
            print(f"Hardware '{old[:8]}...' desvinculado de {chave}.")
    else:
        print("Nenhum hardware vinculado a esta chave.")
    input("Pressione Enter...")


def menu_config():
    global GITHUB_TOKEN, HEADERS
    print("\n--- CONFIGURACAO ---")
    atual = (GITHUB_TOKEN[:8] + "...") if GITHUB_TOKEN else "(vazio)"
    print(f"Token atual: {atual}")
    novo = input("Novo token (Enter para manter): ").strip()
    if novo:
        GITHUB_TOKEN = novo
        HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        print("Token atualizado (valido apenas nesta sessao).")
        print("Para salvar definitivamente, use: set GITHUB_TOKEN=seu_token")
    input("Pressione Enter...")


def main():
    global GITHUB_TOKEN, HEADERS
    if not GITHUB_TOKEN:
        print("=" * 50)
        print("  BYPASS PRO - GERENCIADOR DE CHAVES")
        print("=" * 50)
        print("\nToken nao encontrado!")
        print("Defina a variavel GITHUB_TOKEN ou configure no menu.")
        print("Ex: set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx\n")
        novo = input("Cole seu token GitHub: ").strip()
        if novo:
            global HEADERS
            GITHUB_TOKEN = novo
            HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        else:
            input("Token necessario. Pressione Enter para sair...")
            sys.exit(1)

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 50)
        print("       BYPASS PRO - GERENCIADOR DE CHAVES")
        print("=" * 50)
        print(f"  Repo: {GITHUB_OWNER}/{GITHUB_REPO}")
        print(f"  Token: {GITHUB_TOKEN[:8]}...")
        print("=" * 50)
        print("  1. Gerar chaves")
        print("  2. Listar chaves")
        print("  3. Revogar chave")
        print("  4. Estender chave")
        print("  5. Desvincular hardware")
        print("  6. Configurar token")
        print("  0. Sair")
        print("=" * 50)

        op = input("Escolha: ").strip()
        if op == "1": menu_gerar()
        elif op == "2": menu_listar()
        elif op == "3": menu_revogar()
        elif op == "4": menu_estender()
        elif op == "5": menu_desvincular()
        elif op == "6": menu_config()
        elif op == "0":
            print("Saindo...")
            break
        else:
            input("Opcao invalida. Pressione Enter...")


if __name__ == "__main__":
    main()
