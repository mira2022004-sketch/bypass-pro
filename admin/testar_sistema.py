#!/usr/bin/env python3
"""
Script de teste do sistema de gerenciamento de chaves
Verifica se tudo está configurado corretamente
"""

import os
import sys
import json

print("=" * 70)
print("  TESTE DO SISTEMA BYPASS PRO")
print("=" * 70)
print()

# Teste 1: Python
print("[1] Verificando versão do Python...")
version = sys.version_info
if version.major >= 3 and version.minor >= 6:
    print(f"    ✓ Python {version.major}.{version.minor}.{version.micro} OK")
else:
    print(f"    ✗ Python muito antigo! Versão: {version.major}.{version.minor}")
    print("      Instale Python 3.6 ou superior")

print()

# Teste 2: Requests
print("[2] Verificando biblioteca 'requests'...")
try:
    import requests
    print(f"    ✓ requests versão {requests.__version__} instalado")
except ImportError:
    print("    ✗ requests não instalado!")
    print("      Execute: pip install requests")

print()

# Teste 3: Token GitHub
print("[3] Verificando token GitHub...")
token = os.environ.get("GITHUB_TOKEN")
if token:
    print(f"    ✓ Token configurado: {token[:10]}...")
    if len(token) < 20:
        print("      ⚠️  Token parece muito curto!")
else:
    print("    ✗ Token não configurado!")
    print("      Execute: set GITHUB_TOKEN=seu_token")

print()

# Teste 4: Arquivo keys.json
print("[4] Verificando arquivo keys.json...")
if os.path.exists("keys.json"):
    try:
        with open("keys.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"    ✓ keys.json válido com {len(data)} chave(s)")
        
        # Listar chaves
        for key in list(data.keys())[:3]:
            status = "REVOGADA" if data[key].get("revoked") else "ATIVA"
            print(f"      - {key}: {status}")
        
        if len(data) > 3:
            print(f"      ... e mais {len(data) - 3} chave(s)")
    except json.JSONDecodeError:
        print("    ✗ keys.json está corrompido!")
        print("      Verifique o formato JSON")
    except Exception as e:
        print(f"    ✗ Erro ao ler keys.json: {e}")
else:
    print("    ⚠️  keys.json não encontrado")
    print("      Será criado automaticamente ao gerar primeira chave")

print()

# Teste 5: Conexão GitHub
if token:
    print("[5] Testando conexão com GitHub...")
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        r = requests.get("https://api.github.com/user", headers=headers, timeout=5)
        
        if r.status_code == 200:
            user = r.json()
            print(f"    ✓ Conectado como: {user.get('login', 'desconhecido')}")
        elif r.status_code == 401:
            print("    ✗ Token inválido ou expirado!")
            print("      Gere um novo token em: https://github.com/settings/tokens")
        else:
            print(f"    ✗ Erro HTTP {r.status_code}")
    except requests.RequestException as e:
        print(f"    ✗ Erro de conexão: {e}")
        print("      Verifique sua internet")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
else:
    print("[5] Pulando teste de conexão (token não configurado)")

print()

# Teste 6: Verificar arquivos
print("[6] Verificando arquivos do projeto...")
arquivos = [
    ("keymanager_completo.py", "Gerenciador completo"),
    ("client/BypassPro.ps1", "Cliente PowerShell"),
    ("server/index.js", "Servidor Node.js"),
]

for arquivo, descricao in arquivos:
    if os.path.exists(arquivo):
        size = os.path.getsize(arquivo) / 1024
        print(f"    ✓ {arquivo} ({size:.1f} KB) - {descricao}")
    else:
        print(f"    ✗ {arquivo} não encontrado - {descricao}")

print()

# Resumo
print("=" * 70)
print("  RESUMO")
print("=" * 70)

problemas = []

if version.major < 3 or (version.major == 3 and version.minor < 6):
    problemas.append("Python desatualizado")

try:
    import requests
except:
    problemas.append("requests não instalado")

if not token:
    problemas.append("Token GitHub não configurado")

if problemas:
    print("\n⚠️  PROBLEMAS ENCONTRADOS:")
    for p in problemas:
        print(f"  - {p}")
    print("\nResolva os problemas acima antes de usar o sistema.")
else:
    print("\n✓ TUDO PRONTO! Você pode usar o sistema.")
    print("\nPara iniciar:")
    print("  python keymanager_completo.py")

print()
print("=" * 70)
input("\nPressione Enter para sair...")
