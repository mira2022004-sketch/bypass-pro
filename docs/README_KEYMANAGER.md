# 🔑 BYPASS PRO - GERENCIADOR COMPLETO DE CHAVES

Sistema profissional de gerenciamento de licenças com GitHub como backend.

---

## 📋 FUNCIONALIDADES

✅ **Gerar chaves** - Cria novas chaves com validade customizada  
✅ **Listar chaves** - Visualiza todas as chaves com estatísticas  
✅ **Ativar chave** - Vincula chave a um hardware específico  
✅ **Apagar chave** - Remove permanentemente uma chave  
✅ **Revogar chave** - Bloqueia sem apagar (reversível)  
✅ **Reativar chave** - Reativa chaves revogadas  
✅ **Estender validade** - Adiciona dias à expiração  
✅ **Desvincular hardware** - Remove vinculação para reutilizar  
✅ **Buscar chave** - Encontra e exibe detalhes  
✅ **Configurar token** - Gerencia credenciais GitHub  

---

## 🚀 INSTALAÇÃO

### 1. Instalar Python
- Baixe em: https://www.python.org/downloads/
- Marque "Add Python to PATH" durante instalação

### 2. Instalar dependências
```bash
pip install requests
```

### 3. Configurar token GitHub

#### Gerar token:
1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Dê um nome: `bypass-pro-manager`
4. Marque permissão: **`repo`** (acesso completo aos repositórios)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (só aparece uma vez!)

#### Configurar no Windows:
```bash
set GITHUB_TOKEN=ghp_seu_token_aqui
```

#### Configurar permanentemente:
```bash
setx GITHUB_TOKEN "ghp_seu_token_aqui"
```

---

## 💻 USO

### Executar o gerenciador:
```bash
python keymanager_completo.py
```

### Menu Principal:
```
[1]  Gerar chaves
[2]  Listar todas as chaves
[3]  Ativar chave (vincular hardware)
[4]  Apagar chave permanentemente
[5]  Revogar chave (bloquear)
[6]  Reativar chave revogada
[7]  Estender validade
[8]  Desvincular hardware
[9]  Buscar chave
[10] Configurar token GitHub
[0]  Sair
```

---

## 📖 EXEMPLOS DE USO

### 1️⃣ Gerar 5 chaves com 30 dias de validade:
```
Menu > 1
Dias de validade: 30
Quantidade: 5
```

### 2️⃣ Ativar uma chave:
```
Menu > 3
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Digite o Hardware ID: ABC123DEF456...
```

### 3️⃣ Revogar chave de cliente problema:
```
Menu > 5
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Motivo: Cliente solicitou reembolso
```

### 4️⃣ Estender validade em 30 dias:
```
Menu > 7
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Dias adicionais: 30
```

### 5️⃣ Desvincular para trocar de PC:
```
Menu > 8
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Deseja desvincular? S
```

### 6️⃣ Apagar chave expirada:
```
Menu > 4
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Tem CERTEZA? SIM
```

---

## 🔐 SEGURANÇA

### ⚠️ IMPORTANTE:
- **NUNCA compartilhe seu token GitHub**
- Token tem acesso total aos seus repositórios
- Revogue tokens comprometidos imediatamente
- Use tokens com escopo mínimo necessário

### Revogar token comprometido:
1. https://github.com/settings/tokens
2. Encontre o token
3. Clique em "Delete"
4. Gere um novo

---

## 📊 ESTRUTURA DO KEYS.JSON

```json
{
  "XXXXX-XXXXX-XXXXX-XXXXX": {
    "created": "2026-06-27",
    "expires": "2026-07-27",
    "days": 30,
    "hardware": "ABC123DEF456...",
    "revoked": false,
    "notes": "Cliente VIP",
    "activated_at": "2026-06-27 14:30:00",
    "revoked_at": null,
    "revoked_reason": null,
    "extended_at": null,
    "unlinked_at": null,
    "unlinked_from": null
  }
}
```

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### Erro: "Token não configurado"
**Solução:**
```bash
set GITHUB_TOKEN=seu_token
```

### Erro: "401 Unauthorized"
**Causa:** Token inválido ou expirado  
**Solução:** Gere novo token no GitHub

### Erro: "404 Not Found"
**Causa:** Repositório ou arquivo não encontrado  
**Solução:** Verifique nome do repositório no código

### Erro: "409 Conflict"
**Causa:** Arquivo foi modificado por outro processo  
**Solução:** Tente novamente

### Erro: "Não foi possível conectar"
**Causa:** Sem internet ou GitHub fora do ar  
**Solução:** Verifique conexão

---

## 📝 DIFERENÇAS ENTRE AÇÕES

### REVOGAR vs APAGAR:
- **Revogar:** Bloqueia a chave mas mantém histórico (reversível)
- **Apagar:** Remove permanentemente do sistema (irreversível)

### ATIVAR vs VINCULAR:
- São a mesma coisa! "Ativar" = vincular hardware à chave

### DESVINCULAR vs REVOGAR:
- **Desvincular:** Remove hardware mas chave continua válida
- **Revogar:** Bloqueia completamente o uso da chave

---

## 🔄 FLUXO DE VENDA

```
1. Cliente compra
   ↓
2. Gera chave (Menu > 1)
   ↓
3. Envia chave ao cliente
   ↓
4. Cliente ativa no software
   ↓
5. Sistema vincula hardware automaticamente
   ↓
6. (Opcional) Verificar ativação (Menu > 2)
```

### Quando cliente troca de PC:
```
1. Cliente solicita desvínculo
   ↓
2. Você desvincula hardware (Menu > 8)
   ↓
3. Cliente ativa no novo PC
   ↓
4. Sistema vincula ao novo hardware
```

### Cliente problemático:
```
1. Revogar chave (Menu > 5)
   ↓
2. Cliente não consegue mais usar
   ↓
3. (Se resolver) Reativar (Menu > 6)
```

---

## 🎯 BOAS PRÁTICAS

### ✅ FAÇA:
- Sempre use opção 5 (Revogar) antes de apagar
- Mantenha backup do keys.json
- Use notas para identificar clientes
- Gere chaves com validade adequada
- Verifique status antes de ações críticas

### ❌ NÃO FAÇA:
- Não apague chaves sem revogar antes
- Não compartilhe seu token GitHub
- Não edite keys.json manualmente
- Não gere muitas chaves desnecessárias
- Não ignore conflitos do GitHub

---

## 📞 SUPORTE

### Problemas comuns:

**"Chave não funciona"**
1. Verifique se não está revogada (Menu > 2)
2. Verifique se não expirou
3. Verifique se não está vinculada a outro PC

**"Cliente quer trocar de PC"**
1. Desvincula hardware (Menu > 8)
2. Cliente ativa no novo PC

**"Vendi por engano"**
1. Revogue imediatamente (Menu > 5)
2. Gere nova chave
3. Depois apague a antiga (Menu > 4)

---

## 📦 ARQUIVOS DO PROJETO

```
bypass-pro/
├── keymanager_completo.py  ← NOVO! Gerenciador completo
├── keymanager.py           ← Antigo (simples)
├── keygen.js              ← Gerador Node.js
├── keys.json              ← Banco de dados de chaves
├── client/
│   └── BypassPro.ps1      ← Cliente (software vendido)
└── server/
    └── index.js           ← Servidor de validação
```

---

## 🔧 CONFIGURAÇÃO AVANÇADA

### Mudar repositório:
Edite no topo do `keymanager_completo.py`:
```python
GITHUB_OWNER = "seu-usuario"
GITHUB_REPO = "seu-repo"
KEYS_FILE = "keys.json"
```

### Mudar formato da chave:
```python
def generate_key():
    # Atual: XXXXX-XXXXX-XXXXX-XXXXX (20 caracteres)
    # Modifique aqui para mudar formato
```

---

## 📈 ESTATÍSTICAS

Execute opção 2 (Listar) para ver:
- Total de chaves
- Chaves ativadas
- Chaves disponíveis
- Chaves revogadas
- Chaves expiradas

---

## ⚡ ATALHOS RÁPIDOS

- `python keymanager_completo.py` - Abre o sistema
- `Ctrl + C` - Sair a qualquer momento
- `Enter` - Confirmar/Continuar
- `0` - Voltar ao menu ou sair

---

## 📄 LICENÇA

Uso pessoal. Não redistribuir sem autorização.

---

## ✨ CHANGELOG

### v2.0 (Completo) - 27/06/2026
- ✅ Sistema completo de gerenciamento
- ✅ 10 funcionalidades principais
- ✅ Interface melhorada
- ✅ Busca de chaves
- ✅ Estatísticas detalhadas
- ✅ Histórico de ações
- ✅ Confirmações de segurança

### v1.0 (Básico)
- Gerar, listar, revogar
- Estender, desvincular
- Configurar token

---

**Desenvolvido para BypassPro** 🚀
