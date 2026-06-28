#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BYPASS PRO - GERENCIADOR COMPLETO DE CHAVES
Sistema de gerenciamento com todas as funcionalidades
"""

import os, sys, json, base64, hashlib, random, string
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Instalando dependencia requests...")
    os.system(f"{sys.executable} -m pip install requests")
    import requests

# ============================================================
# CONFIGURAÇÕES
# ============================================================
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or ""
GITHUB_OWNER = "mira2022004-sketch"
GITHUB_REPO = "bypass-pro"
KEYS_FILE = "keys.json"
API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def clear_screen():
    """Limpa a tela"""
    os.system("cls" if os.name == "nt" else "clear")

def generate_key():
    """Gera uma chave no formato XXXXX-XXXXX-XXXXX-XXXXX"""
    chars = string.ascii_uppercase + string.digits
    key = ""
    for i in range(20):
        key += random.choice(chars)
        if i in (4, 9, 14): 
            key += "-"
    return key

def get_keys():
    """Busca as chaves do GitHub"""
    try:
        r = requests.get(f"{API_BASE}/contents/{KEYS_FILE}", headers=HEADERS, timeout=10)
        if r.status_code == 404: 
            return {}, None
        r.raise_for_status()
        d = r.json()
        content = base64.b64decode(d["content"]).decode('utf-8')
        return json.loads(content), d["sha"]
    except requests.RequestException as e:
        print(f"ERRO ao conectar ao GitHub: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"ERRO ao decodificar JSON: {e}")
        return None, None

def save_keys(keys, sha):
    """Salva as chaves no GitHub"""
    try:
        content = json.dumps(keys, indent=4, ensure_ascii=False)
        payload = {
            "message": "keymanager: atualiza keys.json",
            "content": base64.b64encode(content.encode()).decode(),
            "sha": sha
        }
        r = requests.put(f"{API_BASE}/contents/{KEYS_FILE}", json=payload, headers=HEADERS, timeout=10)
        
        if r.status_code == 409:
            print("ERRO: Conflito - arquivo foi modificado por outra pessoa.")
            return False
        
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"ERRO ao salvar no GitHub: {e}")
        return False

def format_date(date_str):
    """Formata data para exibição"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return date_str

def get_status(key_data):
    """Retorna o status de uma chave"""
    if key_data.get("revoked"):
        return "REVOGADA", "red"
    
    try:
        exp = datetime.strptime(key_data["expires"], "%Y-%m-%d")
        now = datetime.utcnow()
        
        if exp < now:
            return "EXPIRADA", "red"
        elif key_data.get("hardware"):
            return "ATIVADA", "green"
        else:
            return "DISPONIVEL", "yellow"
    except:
        return "ERRO", "red"

def print_header():
    """Imprime o cabeçalho do sistema"""
    print("=" * 70)
    print("        BYPASS PRO - GERENCIADOR COMPLETO DE CHAVES")
    print("=" * 70)
    if GITHUB_TOKEN:
        print(f"  Repo: {GITHUB_OWNER}/{GITHUB_REPO}")
        print(f"  Token: {GITHUB_TOKEN[:10]}...")
    else:
        print("  [!] TOKEN NAO CONFIGURADO")
    print("=" * 70)

# ============================================================
# MENU 1: GERAR CHAVES
# ============================================================

def menu_gerar():
    """Gera novas chaves"""
    clear_screen()
    print_header()
    print("\n>>> GERAR NOVAS CHAVES <<<\n")
    
    try:
        dias = input("Dias de validade (padrao 30): ").strip()
        dias = int(dias) if dias else 30
        
        qtd = input("Quantidade de chaves (padrao 1): ").strip()
        qtd = int(qtd) if qtd else 1
        
        if qtd > 100:
            print("Limite maximo: 100 chaves por vez")
            input("\nPressione Enter...")
            return
    except ValueError:
        print("Valor invalido!")
        input("\nPressione Enter...")
        return

    print(f"\nGerando {qtd} chave(s) com validade de {dias} dias...")
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if not keys:
        keys = {}
    
    geradas = []
    for _ in range(qtd):
        attempts = 0
        while attempts < 100:
            k = generate_key()
            if k not in keys:
                break
            attempts += 1
        
        if attempts >= 100:
            print("ERRO: Nao foi possivel gerar chave unica")
            continue
        
        exp = (datetime.utcnow() + timedelta(days=dias)).strftime("%Y-%m-%d")
        keys[k] = {
            "created": datetime.utcnow().strftime("%Y-%m-%d"),
            "expires": exp,
            "days": dias,
            "hardware": None,
            "revoked": False,
            "notes": ""
        }
        geradas.append(k)
    
    if geradas:
        if save_keys(keys, sha):
            print(f"\n{'='*70}")
            print(f"  {len(geradas)} CHAVE(S) GERADA(S) COM SUCESSO!")
            print(f"{'='*70}\n")
            for i, k in enumerate(geradas, 1):
                print(f"  {i:2d}. {k}  (expira: {format_date(keys[k]['expires'])})")
            print(f"\n{'='*70}")
        else:
            print("\nErro ao salvar chaves!")
    else:
        print("\nNenhuma chave foi gerada!")
    
    input("\nPressione Enter para continuar...")

# ============================================================
# MENU 2: LISTAR CHAVES
# ============================================================

def menu_listar():
    """Lista todas as chaves"""
    clear_screen()
    print_header()
    print("\n>>> LISTA DE TODAS AS CHAVES <<<\n")
    
    keys, _ = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if not keys:
        print("Nenhuma chave encontrada.")
        input("\nPressione Enter...")
        return
    
    # Estatísticas
    total = len(keys)
    ativadas = sum(1 for v in keys.values() if v.get("hardware") and not v.get("revoked"))
    disponiveis = sum(1 for v in keys.values() if not v.get("hardware") and not v.get("revoked"))
    revogadas = sum(1 for v in keys.values() if v.get("revoked"))
    expiradas = sum(1 for v in keys.values() if not v.get("revoked") and 
                    datetime.strptime(v["expires"], "%Y-%m-%d") < datetime.utcnow())
    
    print(f"Total: {total} | Ativadas: {ativadas} | Disponiveis: {disponiveis} | Revogadas: {revogadas} | Expiradas: {expiradas}")
    print(f"\n{'='*70}")
    print(f"{'CHAVE':<25} {'CRIADA':<12} {'EXPIRA':<12} {'HW':<10} {'STATUS':<12}")
    print(f"{'='*70}")
    
    for k, v in sorted(keys.items(), key=lambda x: x[1]["created"], reverse=True):
        hw = (v.get("hardware") or "---")[:8]
        status, _ = get_status(v)
        created = format_date(v["created"])
        expires = format_date(v["expires"])
        print(f"{k:<25} {created:<12} {expires:<12} {hw:<10} {status:<12}")
    
    print(f"{'='*70}")
    input("\nPressione Enter para continuar...")

# ============================================================
# MENU 3: ATIVAR CHAVE (Vincular Hardware)
# ============================================================

def menu_ativar():
    """Ativa uma chave vinculando a um hardware"""
    clear_screen()
    print_header()
    print("\n>>> ATIVAR CHAVE (Vincular Hardware) <<<\n")
    
    chave = input("Digite a chave: ").strip().upper()
    if not chave:
        return
    
    hardware_id = input("Digite o Hardware ID: ").strip()
    if not hardware_id:
        return
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if chave not in keys:
        print(f"\nChave '{chave}' nao encontrada!")
        input("\nPressione Enter...")
        return
    
    key_data = keys[chave]
    
    # Verificações
    if key_data.get("revoked"):
        print("\nERRO: Esta chave foi revogada!")
        input("\nPressione Enter...")
        return
    
    exp = datetime.strptime(key_data["expires"], "%Y-%m-%d")
    if exp < datetime.utcnow():
        print("\nERRO: Esta chave esta expirada!")
        input("\nPressione Enter...")
        return
    
    if key_data.get("hardware"):
        print(f"\nAVISO: Esta chave ja esta vinculada ao hardware: {key_data['hardware'][:16]}...")
        confirma = input("Deseja SOBRESCREVER o vinculo? (S/N): ").strip().upper()
        if confirma != "S":
            return
    
    # Ativar
    keys[chave]["hardware"] = hardware_id
    keys[chave]["activated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    if save_keys(keys, sha):
        print(f"\n{'='*70}")
        print(f"  CHAVE ATIVADA COM SUCESSO!")
        print(f"{'='*70}")
        print(f"  Chave: {chave}")
        print(f"  Hardware: {hardware_id[:32]}...")
        print(f"  Expira em: {format_date(key_data['expires'])}")
        print(f"{'='*70}")
    else:
        print("\nErro ao salvar!")
    
    input("\nPressione Enter...")

# ============================================================
# MENU 4: APAGAR CHAVE
# ============================================================

def menu_apagar():
    """Apaga uma chave permanentemente"""
    clear_screen()
    print_header()
    print("\n>>> APAGAR CHAVE PERMANENTEMENTE <<<\n")
    print("⚠️  CUIDADO: Esta acao NAO PODE SER DESFEITA!\n")
    
    chave = input("Digite a chave a apagar: ").strip().upper()
    if not chave:
        return
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if chave not in keys:
        print(f"\nChave '{chave}' nao encontrada!")
        input("\nPressione Enter...")
        return
    
    # Mostrar informações da chave
    key_data = keys[chave]
    print(f"\nInformacoes da chave:")
    print(f"  Criada em: {format_date(key_data['created'])}")
    print(f"  Expira em: {format_date(key_data['expires'])}")
    print(f"  Hardware: {key_data.get('hardware') or 'Nao vinculada'}")
    print(f"  Status: {get_status(key_data)[0]}")
    
    confirma = input(f"\nTem CERTEZA que deseja APAGAR '{chave}'? (digite SIM): ").strip().upper()
    
    if confirma == "SIM":
        del keys[chave]
        if save_keys(keys, sha):
            print(f"\n✓ Chave '{chave}' apagada com sucesso!")
        else:
            print("\nErro ao salvar!")
    else:
        print("\nOperacao cancelada.")
    
    input("\nPressione Enter...")

# ============================================================
# MENU 5: REVOGAR CHAVE
# ============================================================

def menu_revogar():
    """Revoga uma chave (bloqueia sem apagar)"""
    clear_screen()
    print_header()
    print("\n>>> REVOGAR CHAVE (Bloquear sem apagar) <<<\n")
    
    chave = input("Digite a chave a revogar: ").strip().upper()
    if not chave:
        return
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if chave not in keys:
        print(f"\nChave '{chave}' nao encontrada!")
        input("\nPressione Enter...")
        return
    
    if keys[chave].get("revoked"):
        print("\nEsta chave ja esta revogada!")
        input("\nPressione Enter...")
        return
    
    motivo = input("Motivo da revogacao (opcional): ").strip()
    
    keys[chave]["revoked"] = True
    keys[chave]["revoked_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if motivo:
        keys[chave]["revoked_reason"] = motivo
    
    if save_keys(keys, sha):
        print(f"\n✓ Chave '{chave}' revogada com sucesso!")
        if motivo:
            print(f"  Motivo: {motivo}")
    else:
        print("\nErro ao salvar!")
    
    input("\nPressione Enter...")

# ============================================================
# MENU 6: REATIVAR CHAVE REVOGADA
# ============================================================

def menu_reativar():
    """Reativa uma chave que foi revogada"""
    clear_screen()
    print_header()
    print("\n>>> REATIVAR CHAVE REVOGADA <<<\n")
    
    chave = input("Digite a chave a reativar: ").strip().upper()
    if not chave:
        return
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if chave not in keys:
        print(f"\nChave '{chave}' nao encontrada!")
        input("\nPressione Enter...")
        return
    
    if not keys[chave].get("revoked"):
        print("\nEsta chave nao esta revogada!")
        input("\nPressione Enter...")
        return
    
    keys[chave]["revoked"] = False
    keys[chave]["reactivated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    if save_keys(keys, sha):
        print(f"\n✓ Chave '{chave}' reativada com sucesso!")
    else:
        print("\nErro ao salvar!")
    
    input("\nPressione Enter...")

# ============================================================
# MENU 7: ESTENDER VALIDADE
# ============================================================

def menu_estender():
    """Estende a validade de uma chave"""
    clear_screen()
    print_header()
    print("\n>>> ESTENDER VALIDADE DA CHAVE <<<\n")
    
    chave = input("Digite a chave: ").strip().upper()
    if not chave:
        return
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if chave not in keys:
        print(f"\nChave '{chave}' nao encontrada!")
        input("\nPressione Enter...")
        return
    
    key_data = keys[chave]
    print(f"\nValidade atual: {format_date(key_data['expires'])}")
    
    try:
        dias = int(input("Dias adicionais: "))
    except ValueError:
        print("Valor invalido!")
        input("\nPressione Enter...")
        return
    
    exp = datetime.strptime(key_data["expires"], "%Y-%m-%d") + timedelta(days=dias)
    keys[chave]["expires"] = exp.strftime("%Y-%m-%d")
    keys[chave]["days"] = key_data.get("days", 0) + dias
    keys[chave]["extended_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    if save_keys(keys, sha):
        print(f"\n✓ Chave estendida ate {format_date(keys[chave]['expires'])}!")
    else:
        print("\nErro ao salvar!")
    
    input("\nPressione Enter...")

# ============================================================
# MENU 8: DESVINCULAR HARDWARE
# ============================================================

def menu_desvincular():
    """Desvincula o hardware de uma chave"""
    clear_screen()
    print_header()
    print("\n>>> DESVINCULAR HARDWARE <<<\n")
    
    chave = input("Digite a chave: ").strip().upper()
    if not chave:
        return
    
    keys, sha = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    if chave not in keys:
        print(f"\nChave '{chave}' nao encontrada!")
        input("\nPressione Enter...")
        return
    
    if not keys[chave].get("hardware"):
        print("\nNenhum hardware vinculado a esta chave!")
        input("\nPressione Enter...")
        return
    
    old_hw = keys[chave]["hardware"]
    print(f"\nHardware atual: {old_hw[:32]}...")
    
    confirma = input("\nDeseja desvincular? (S/N): ").strip().upper()
    if confirma != "S":
        return
    
    keys[chave]["hardware"] = None
    keys[chave]["unlinked_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    keys[chave]["unlinked_from"] = old_hw
    
    if save_keys(keys, sha):
        print(f"\n✓ Hardware desvinculado com sucesso!")
    else:
        print("\nErro ao salvar!")
    
    input("\nPressione Enter...")

# ============================================================
# MENU 9: BUSCAR CHAVE
# ============================================================

def menu_buscar():
    """Busca e exibe detalhes de uma chave"""
    clear_screen()
    print_header()
    print("\n>>> BUSCAR CHAVE <<<\n")
    
    chave = input("Digite a chave ou parte dela: ").strip().upper()
    if not chave:
        return
    
    keys, _ = get_keys()
    if keys is None:
        input("\nErro ao conectar. Pressione Enter...")
        return
    
    encontradas = [k for k in keys.keys() if chave in k]
    
    if not encontradas:
        print(f"\nNenhuma chave encontrada com '{chave}'")
        input("\nPressione Enter...")
        return
    
    print(f"\n{'='*70}")
    print(f"Encontrada(s) {len(encontradas)} chave(s):")
    print(f"{'='*70}\n")
    
    for k in encontradas:
        v = keys[k]
        status, _ = get_status(v)
        
        print(f"Chave: {k}")
        print(f"  Status: {status}")
        print(f"  Criada em: {format_date(v['created'])}")
        print(f"  Expira em: {format_date(v['expires'])}")
        print(f"  Dias totais: {v.get('days', 'N/A')}")
        print(f"  Hardware: {v.get('hardware') or 'Nao vinculada'}")
        if v.get("notes"):
            print(f"  Notas: {v['notes']}")
        print()
    
    input("Pressione Enter...")

# ============================================================
# MENU 10: CONFIGURAR TOKEN
# ============================================================

def menu_config():
    """Configura o token do GitHub"""
    global GITHUB_TOKEN, HEADERS
    
    clear_screen()
    print_header()
    print("\n>>> CONFIGURAR TOKEN GITHUB <<<\n")
    
    if GITHUB_TOKEN:
        print(f"Token atual: {GITHUB_TOKEN[:10]}...")
    else:
        print("Token atual: (vazio)")
    
    print("\nPara gerar um token:")
    print("1. Acesse: https://github.com/settings/tokens")
    print("2. Gere um token com permissao 'repo'")
    print("3. Cole aqui\n")
    
    novo = input("Novo token (Enter para manter): ").strip()
    
    if novo:
        GITHUB_TOKEN = novo
        HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        print("\n✓ Token atualizado!")
        print("\nPara salvar permanentemente:")
        print(f"  Windows: set GITHUB_TOKEN={novo}")
        print(f"  Linux/Mac: export GITHUB_TOKEN={novo}")
    else:
        print("\nToken nao alterado.")
    
    input("\nPressione Enter...")

# ============================================================
# MENU PRINCIPAL
# ============================================================

def main_menu():
    """Menu principal"""
    while True:
        clear_screen()
        print_header()
        print("\n>>> MENU PRINCIPAL <<<\n")
        print("  [1]  Gerar chaves")
        print("  [2]  Listar todas as chaves")
        print("  [3]  Ativar chave (vincular hardware)")
        print("  [4]  Apagar chave permanentemente")
        print("  [5]  Revogar chave (bloquear)")
        print("  [6]  Reativar chave revogada")
        print("  [7]  Estender validade")
        print("  [8]  Desvincular hardware")
        print("  [9]  Buscar chave")
        print("  [10] Configurar token GitHub")
        print("  [0]  Sair")
        print(f"\n{'='*70}")
        
        op = input("Escolha uma opcao: ").strip()
        
        if op == "1":
            menu_gerar()
        elif op == "2":
            menu_listar()
        elif op == "3":
            menu_ativar()
        elif op == "4":
            menu_apagar()
        elif op == "5":
            menu_revogar()
        elif op == "6":
            menu_reativar()
        elif op == "7":
            menu_estender()
        elif op == "8":
            menu_desvincular()
        elif op == "9":
            menu_buscar()
        elif op == "10":
            menu_config()
        elif op == "0":
            clear_screen()
            print("Saindo... Ate logo!")
            break
        else:
            print("\nOpcao invalida!")
            input("Pressione Enter...")

# ============================================================
# INICIALIZAÇÃO
# ============================================================

def main():
    """Função principal"""
    global GITHUB_TOKEN, HEADERS
    
    if not GITHUB_TOKEN:
        clear_screen()
        print("=" * 70)
        print("  BYPASS PRO - GERENCIADOR COMPLETO DE CHAVES")
        print("=" * 70)
        print("\n⚠️  TOKEN NAO CONFIGURADO!\n")
        print("Defina a variavel GITHUB_TOKEN ou configure agora.")
        print("\nPara gerar um token:")
        print("1. Acesse: https://github.com/settings/tokens")
        print("2. Clique em 'Generate new token (classic)'")
        print("3. Selecione permissao 'repo'")
        print("4. Gere e copie o token\n")
        
        novo = input("Cole seu token GitHub (ou Enter para sair): ").strip()
        
        if novo:
            GITHUB_TOKEN = novo
            HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            print("\n✓ Token configurado!")
            print("\nPara salvar permanentemente:")
            print(f"  Windows: set GITHUB_TOKEN={novo}")
            print(f"  Linux/Mac: export GITHUB_TOKEN={novo}")
            input("\nPressione Enter para continuar...")
        else:
            print("\nToken necessario para usar o sistema. Saindo...")
            sys.exit(1)
    
    main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuario. Saindo...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERRO FATAL: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)
