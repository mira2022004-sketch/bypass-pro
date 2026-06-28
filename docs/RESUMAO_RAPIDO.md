# ⚡ RESUMÃO RÁPIDO - BYPASS PRO

## 🚀 CONFIGURAÇÃO (5 MINUTOS)

```bash
# 1. Instalar dependência
pip install requests

# 2. Configurar token
set GITHUB_TOKEN=ghp_seu_token_aqui

# 3. Testar
python testar_sistema.py
```

---

## 💰 VENDER (3 PASSOS)

### 1. Gerar chave:
```bash
python keymanager_completo.py
[1] Gerar
Dias: 30
Quantidade: 1

Resultado: XXXXX-XXXXX-XXXXX-XXXXX
```

### 2. Enviar ao cliente:
```
Sua chave: XXXXX-XXXXX-XXXXX-XXXXX
Download: [link do .exe]
```

### 3. Cliente ativa e pronto! ✅

---

## 🔧 GERENCIAR CHAVES

```bash
python keymanager_completo.py
```

**Ações principais:**
- `[1]` Gerar novas chaves
- `[2]` Listar todas (com estatísticas)
- `[5]` Revogar (bloquear cliente)
- `[7]` Estender validade (renovação)
- `[8]` Desvincular (trocar de PC)

---

## 🛠️ PROBLEMAS COMUNS

### Cliente: "Não funciona"
```bash
python keymanager_completo.py
[9] Buscar chave
```
Verifique se está expirada, revogada ou vinculada a outro PC.

### Cliente: "Quero trocar de PC"
```bash
[8] Desvincular hardware
```

### Cliente: "Expirou"
```bash
[7] Estender validade
Dias: 30
```

---

## 🔐 COMPILAR CLIENTE

```powershell
# 1. Editar client/BypassPro_v2.ps1
# Trocar: $script:GITHUB_TOKEN = "seu_token"

# 2. Compilar
Invoke-ps2exe -inputFile "client/BypassPro_v2.ps1" -outputFile "BypassPro.exe" -requireAdmin -noConsole

# 3. Distribuir BypassPro.exe
```

---

## 📊 VER ESTATÍSTICAS

```bash
python keymanager_completo.py
[2] Listar

Mostra:
Total: 50 | Ativadas: 32 | Disponíveis: 10 | Revogadas: 5 | Expiradas: 3
```

---

## 🔄 SINCRONIZAR GITHUB

```bash
python sync_github.py
[1] Upload (Local → GitHub)
[2] Download (GitHub → Local)
[3] Comparar
```

---

## ⚡ COMANDOS RÁPIDOS

| Ação | Comando |
|------|---------|
| Gerar 5 chaves de 30 dias | `keymanager_completo.py` → 1 → 30 → 5 |
| Ver todas as chaves | `keymanager_completo.py` → 2 |
| Bloquear cliente | `keymanager_completo.py` → 5 |
| Renovar licença | `keymanager_completo.py` → 7 |
| Trocar PC do cliente | `keymanager_completo.py` → 8 |
| Testar sistema | `testar_sistema.py` |
| Sincronizar | `sync_github.py` |

---

## 🎯 CHECKLIST DIÁRIO

- [ ] Verificar chaves expiradas (`[2]`)
- [ ] Responder clientes com problemas
- [ ] Gerar chaves para novas vendas (`[1]`)
- [ ] Backup de keys.json (copiar arquivo)

---

## 🆘 EMERGÊNCIA

### Token vazou:
```
1. https://github.com/settings/tokens
2. Delete token comprometido
3. Gere novo
4. set GITHUB_TOKEN=novo_token
5. Recompile o cliente
```

### keys.json corrompeu:
```bash
python sync_github.py
[2] Download (recupera do GitHub)
```

### Sistema não funciona:
```bash
python testar_sistema.py
# Veja o que está errado
```

---

## 📱 MENSAGENS PRONTAS

### Venda:
```
Olá! BypassPro disponível!
💰 R$ 20 (30 dias)
⚡ Entrega imediata
Aceito PIX
```

### Pós-venda:
```
Sua chave: XXXXX-XXXXX-XXXXX-XXXXX
Download: [link]

1. Execute como Admin
2. Cole a chave
3. Pronto!
```

### Suporte:
```
Me envia print do erro que eu resolvo!
```

---

## 💡 DICAS

✅ **Sempre revogue antes de apagar**  
✅ **Faça backup de keys.json semanalmente**  
✅ **Use notas para identificar clientes**  
✅ **Cliente problemático? Revogue na hora!**  
✅ **Token = senha, nunca compartilhe**  

---

## 📁 ARQUIVOS PRINCIPAIS

```
keymanager_completo.py  ← Gerenciar tudo
sync_github.py          ← Sincronizar
testar_sistema.py       ← Testar
keys.json               ← Banco de dados
BypassPro.exe           ← Distribua este
```

---

## 🎓 APRENDA MAIS

- `GUIA_COMPLETO.md` - Manual completo
- `README_KEYMANAGER.md` - Detalhes do gerenciador
- `INSTRUCOES_COMPILAR.md` - Como compilar

---

**PRONTO! Agora é só vender!** 💰🚀
