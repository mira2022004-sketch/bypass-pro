#!/usr/bin/env python3
"""
SYNC GITHUB - Sincroniza keys.json local com GitHub
"""

import os
import sys
import json
import base64

try:
    import requests
except ImportError:
    print("Instalando requests...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or ""
GITHUB_OWNER = "mira2022004-sketch"
GITHUB_REPO = "bypass-pro"
KEYS_FILE = "keys.json"
API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_github_keys():
    """Busca keys.json do GitHub"""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"{API_BASE}/contents/{KEYS_FILE}"
    r = requests.get(url, headers=headers, timeout=10)
    
    if r.status_code == 404:
        return None, None
    
    r.raise_for_status()
    data = r.json()
    content = json.loads(base64.b64decode(data["content"]).decode('utf-8'))
    return content, data["sha"]

def upload_to_github(keys, sha=None):
    """Envia keys.json para GitHub"""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    content = json.dumps(keys, indent=4, ensure_ascii=False)
    encoded = base64.b64encode(content.encode()).decode()
    
    payload = {
        "message": "sync: atualiza keys.json",
        "content": encoded
    }
    
    if sha:
        payload["sha"] = sha
    
    url = f"{API_BASE}/contents/{KEYS_FILE}"
    r = requests.put(url, json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    return True

def main():
    clear()
    print("=" * 70)
    print("  SYNC GITHUB - Sincronizar keys.json")
    print("=" * 70)
    print()
    
    if not GITHUB_TOKEN:
        print("ERRO: Token GitHub nao configurado!")
        print("Execute: set GITHUB_TOKEN=seu_token")
        input("\nPressione Enter...")
        return
    
    print(f"Repo: {GITHUB_OWNER}/{GITHUB_REPO}")
    print(f"Token: {GITHUB_TOKEN[:10]}...")
    print()
    
    # Menu
    print("[1] Upload: Local -> GitHub")
    print("[2] Download: GitHub -> Local")
    print("[3] Comparar")
    print("[0] Sair")
    print()
    
    op = input("Escolha: ").strip()
    
    if op == "1":
        # Upload local para GitHub
        print("\n>>> UPLOAD LOCAL -> GITHUB <<<\n")
        
        if not os.path.exists("keys.json"):
            print("ERRO: keys.json local nao encontrado!")
            input("\nPressione Enter...")
            return
        
        with open("keys.json", "r", encoding="utf-8") as f:
            local_keys = json.load(f)
        
        print(f"Chaves locais: {len(local_keys)}")
        
        # Busca SHA do GitHub
        print("Buscando SHA do GitHub...")
        github_keys, sha = get_github_keys()
        
        if github_keys:
            print(f"Chaves no GitHub: {len(github_keys)}")
            confirma = input("\nIsto vai SOBRESCREVER o GitHub! Confirma? (S/N): ").strip().upper()
            if confirma != "S":
                print("Cancelado.")
                input("\nPressione Enter...")
                return
        else:
            print("Arquivo nao existe no GitHub. Sera criado.")
            sha = None
        
        print("\nEnviando...")
        if upload_to_github(local_keys, sha):
            print("✓ Upload concluido com sucesso!")
        else:
            print("✗ Erro no upload!")
    
    elif op == "2":
        # Download GitHub para local
        print("\n>>> DOWNLOAD GITHUB -> LOCAL <<<\n")
        
        print("Buscando keys.json do GitHub...")
        github_keys, sha = get_github_keys()
        
        if not github_keys:
            print("ERRO: keys.json nao encontrado no GitHub!")
            input("\nPressione Enter...")
            return
        
        print(f"Chaves no GitHub: {len(github_keys)}")
        
        if os.path.exists("keys.json"):
            print("AVISO: keys.json local sera sobrescrito!")
            confirma = input("Confirma? (S/N): ").strip().upper()
            if confirma != "S":
                print("Cancelado.")
                input("\nPressione Enter...")
                return
        
        with open("keys.json", "w", encoding="utf-8") as f:
            json.dump(github_keys, f, indent=4, ensure_ascii=False)
        
        print("✓ Download concluido com sucesso!")
    
    elif op == "3":
        # Comparar
        print("\n>>> COMPARAR LOCAL vs GITHUB <<<\n")
        
        # Local
        if os.path.exists("keys.json"):
            with open("keys.json", "r", encoding="utf-8") as f:
                local_keys = json.load(f)
            print(f"Local: {len(local_keys)} chaves")
        else:
            local_keys = {}
            print("Local: arquivo nao encontrado")
        
        # GitHub
        print("Buscando GitHub...")
        github_keys, sha = get_github_keys()
        
        if github_keys:
            print(f"GitHub: {len(github_keys)} chaves")
        else:
            github_keys = {}
            print("GitHub: arquivo nao encontrado")
        
        print()
        
        # Diferenças
        local_only = set(local_keys.keys()) - set(github_keys.keys())
        github_only = set(github_keys.keys()) - set(local_keys.keys())
        both = set(local_keys.keys()) & set(github_keys.keys())
        
        if local_only:
            print(f"Apenas no local: {len(local_only)} chave(s)")
            for k in list(local_only)[:5]:
                print(f"  - {k}")
            if len(local_only) > 5:
                print(f"  ... e mais {len(local_only) - 5}")
        
        if github_only:
            print(f"\nApenas no GitHub: {len(github_only)} chave(s)")
            for k in list(github_only)[:5]:
                print(f"  - {k}")
            if len(github_only) > 5:
                print(f"  ... e mais {len(github_only) - 5}")
        
        if not local_only and not github_only:
            print("✓ Local e GitHub estao sincronizados!")
        
        print(f"\nEm ambos: {len(both)} chave(s)")
    
    elif op == "0":
        return
    else:
        print("Opcao invalida!")
    
    input("\nPressione Enter...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido.")
    except Exception as e:
        print(f"\n\nERRO: {e}")
        input("\nPressione Enter...")
