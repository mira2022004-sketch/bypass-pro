# 🚀 GUIA COMPLETO - BYPASS PRO

## 📦 O QUE FOI CRIADO/ATUALIZADO

### ✅ Sistema de Gerenciamento de Chaves
- **`keymanager_completo.py`** - Gerenciador completo com 10 funcionalidades
- **`sync_github.py`** - Sincroniza keys.json com GitHub
- **`testar_sistema.py`** - Testa se tudo está configurado

### ✅ Cliente Atualizado
- **`client/BypassPro_v2.ps1`** - NOVO! Verifica expiração a cada uso
  - ❌ Bloqueia se chave expirou
  - ❌ Bloqueia se chave foi revogada
  - ❌ Bloqueia se hardware mudou
  - ✅ Avisa quando faltam 7 dias para expirar
  - ✅ Mostra dias restantes no menu

### ✅ Arquivos Corrigidos
- **`keys.json`** - Formatação corrigida

### ✅ Documentação
- **`README_KEYMANAGER.md`** - Manual completo do gerenciador
- **`GUIA_COMPLETO.md`** - Este arquivo

### ✅ Mensagens para Anúncios
- **`textos_anuncio.txt`** - 6 versões de título + descrição
- **`mensagens_automaticas.txt`** - 9 mensagens para clientes
- **`mensagem_automatica_compra.txt`** - 6 versões pós-compra
- **`prompt_gemini_anuncio.txt`** - Prompt para IA criar imagem
- **`prompts_gemini_versoes.txt`** - 3 versões de prompts

---

## 🔧 CONFIGURAÇÃO INICIAL (PASSO A PASSO)

### 1️⃣ Instalar Python
```bash
# Baixe em: https://www.python.org/downloads/
# Marque "Add Python to PATH"
```

### 2️⃣ Instalar dependências
```bash
pip install requests
```

### 3️⃣ Configurar Token GitHub

#### Gerar token:
1. https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Nome: `bypass-pro`
4. Permissão: **`repo`** ✅
5. Generate e copie o token

#### Configurar (Windows):
```bash
# Temporário (só esta sessão)
set GITHUB_TOKEN=ghp_seu_token_aqui

# Permanente
setx GITHUB_TOKEN "ghp_seu_token_aqui"
```

### 4️⃣ Testar instalação
```bash
python testar_sistema.py
```

---

## 💻 USO DIÁRIO

### 📊 GERENCIAR CHAVES

```bash
python keymanager_completo.py
```

**Menu:**
```
[1]  Gerar chaves           - Cria novas licenças
[2]  Listar todas           - Ver todas + estatísticas
[3]  Ativar chave          - Vincular hardware manualmente
[4]  Apagar chave          - Deletar permanentemente
[5]  Revogar chave         - Bloquear (reversível)
[6]  Reativar revogada     - Desbloquear
[7]  Estender validade     - Adicionar dias
[8]  Desvincular hardware  - Liberar para outro PC
[9]  Buscar chave          - Encontrar e ver detalhes
[10] Configurar token      - Mudar credenciais GitHub
[0]  Sair
```

### 🔄 SINCRONIZAR COM GITHUB

```bash
python sync_github.py
```

**Opções:**
- **[1] Upload** - Local → GitHub (sobrescreve GitHub)
- **[2] Download** - GitHub → Local (sobrescreve local)
- **[3] Comparar** - Ver diferenças

⚠️ **Use isso se:**
- Editou keys.json manualmente
- GitHub está desatualizado
- Quer backup local

---

## 🎯 FLUXO DE VENDA COMPLETO

### 1️⃣ Cliente compra
```bash
python keymanager_completo.py
Opção: 1 (Gerar chaves)
Dias: 30
Quantidade: 1
```

**Resultado:**
```
XXXXX-XXXXX-XXXXX-XXXXX (expira: 27/07/2026)
```

### 2️⃣ Enviar ao cliente
Copie a mensagem de `mensagem_automatica_compra.txt` (versão 5):

```
🔥 COMPRA CONFIRMADA! 🔥

Sua chave: XXXXX-XXXXX-XXXXX-XXXXX

📥 Download: [link]
📖 Tutorial: [instruções]
```

### 3️⃣ Cliente ativa
- Baixa o `BypassPro.exe` (compilado do v2)
- Executa como admin
- Cola a chave
- Sistema vincula automaticamente ao hardware

### 4️⃣ Verificar ativação
```bash
python keymanager_completo.py
Opção: 2 (Listar)
```

Verá:
```
XXXXX-XXXXX-XXXXX-XXXXX  27/06/26  27/07/26  ABC12345  ATIVADA
```

---

## 🔥 CENÁRIOS COMUNS

### ✅ Cliente quer trocar de PC
```
Menu > 8 (Desvincular hardware)
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Confirmar: S
```

Cliente pode ativar no novo PC normalmente.

---

### ❌ Cliente problemático
```
Menu > 5 (Revogar)
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Motivo: Reembolso solicitado
```

Software para de funcionar imediatamente! ⛔

---

### 📅 Renovar licença
```
Menu > 7 (Estender)
Digite a chave: XXXXX-XXXXX-XXXXX-XXXXX
Dias adicionais: 30
```

---

### 🗑️ Limpar chaves expiradas
```
Menu > 2 (Listar) - anote as expiradas
Menu > 4 (Apagar) - delete uma por vez
```

---

## 🛡️ COMO O V2 PROTEGE CONTRA PIRATARIA

### ❌ Cliente NÃO pode usar se:

1. **Chave expirou**
   ```
   ========================================
    ERRO: LICENCA EXPIRADA!
   ========================================
   Sua licenca expirou em: 27/07/2026
   ```

2. **Chave foi revogada**
   ```
   ========================================
    ERRO: LICENCA REVOGADA!
   ========================================
   Sua licenca foi cancelada.
   ```

3. **Hardware diferente**
   ```
   ========================================
    ERRO: HARDWARE DIFERENTE!
   ========================================
   Esta chave esta vinculada a outro computador.
   ```

4. **Chave não existe no GitHub**
   ```
   ========================================
    ERRO: LICENCA INVALIDA!
   ========================================
   Sua chave nao existe mais no servidor.
   ```

### ✅ Validação acontece:
- Na inicialização
- **A CADA USO do menu** (opções 1, 2, 3)
- Antes de bloquear/desbloquear Steam

### 📡 Modo Offline:
- Se não conectar ao GitHub: permite uso
- Mas na próxima conexão, valida tudo!

---

## 🔨 COMPILAR O CLIENTE V2

### Instalar ps2exe:
```powershell
Install-Module ps2exe -Scope CurrentUser
```

### Compilar:
```powershell
Invoke-ps2exe `
  -inputFile "client/BypassPro_v2.ps1" `
  -outputFile "BypassPro.exe" `
  -requireAdmin `
  -title "Bypass Pro" `
  -company "Seu Nome" `
  -version "2.0.0.0" `
  -iconFile "icon.ico"
```

**Substitua antes de compilar:**
```powershell
$script:GITHUB_TOKEN = "SEU_TOKEN_AQUI"
```

---

## 📊 ESTATÍSTICAS

### Ver estatísticas:
```bash
python keymanager_completo.py
Opção: 2 (Listar)
```

**Mostra:**
```
Total: 50 | Ativadas: 32 | Disponiveis: 10 | Revogadas: 5 | Expiradas: 3
```

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### ❌ "Token não configurado"
```bash
set GITHUB_TOKEN=ghp_seu_token
```

### ❌ "401 Unauthorized"
- Token inválido
- Gere novo em: https://github.com/settings/tokens

### ❌ "404 Not Found"
- Arquivo keys.json não existe no GitHub
- Use `sync_github.py` opção 1 para criar

### ❌ "409 Conflict"
- Arquivo foi modificado
- Use `sync_github.py` opção 3 para comparar

### ❌ Cliente: "Chave não funciona"
```bash
python keymanager_completo.py
Opção: 9 (Buscar)
# Verifique status da chave
```

Possíveis causas:
- Expirada
- Revogada
- Já vinculada a outro PC
- Cliente não está com internet

---

## 📁 ESTRUTURA DO PROJETO

```
bypass-pro/
│
├── 🔑 GERENCIAMENTO
│   ├── keymanager_completo.py    ← Principal! Use este
│   ├── keymanager.py              ← Antigo (básico)
│   ├── sync_github.py             ← Sincronizar GitHub
│   ├── testar_sistema.py          ← Testar configuração
│   └── keys.json                  ← Banco de dados
│
├── 💻 CLIENTE (Software vendido)
│   ├── client/BypassPro_v2.ps1    ← NOVO! Com verificação
│   ├── client/BypassPro.ps1       ← Antigo (sem verificação)
│   └── BypassPro.exe              ← Compilado (distribua este)
│
├── 🌐 SERVIDOR (Opcional)
│   ├── server/index.js            ← API REST
│   └── server/package.json
│
├── 📝 ANÚNCIOS
│   ├── textos_anuncio.txt
│   ├── mensagens_automaticas.txt
│   ├── mensagem_automatica_compra.txt
│   ├── prompt_gemini_anuncio.txt
│   └── prompts_gemini_versoes.txt
│
└── 📖 DOCUMENTAÇÃO
    ├── README_KEYMANAGER.md
    └── GUIA_COMPLETO.md           ← Este arquivo
```

---

## 🎯 CHECKLIST PRÉ-VENDA

Antes de vender, certifique-se:

- [ ] Token GitHub configurado
- [ ] `testar_sistema.py` passou todos os testes
- [ ] keys.json sincronizado com GitHub
- [ ] Cliente v2 compilado com SEU token
- [ ] Testou gerar chave
- [ ] Testou ativar chave
- [ ] Testou expiração (mude data no GitHub)
- [ ] Mensagens automáticas configuradas
- [ ] Link de download funcionando

---

## 💰 PREÇOS SUGERIDOS

### Baseado em concorrência:
- **7 dias:** R$ 5-10
- **30 dias:** R$ 15-25
- **90 dias:** R$ 40-60
- **Vitalício (1 ano):** R$ 80-120

### Estratégia:
- Comece com 30 dias
- Ofereça desconto na renovação
- Vitalício = 365+ dias

---

## 📈 CRESCIMENTO

### Automatizar ainda mais:

1. **Bot Telegram/Discord**
   - Cliente compra via bot
   - Bot gera chave automaticamente
   - Bot envia chave + download

2. **Site próprio**
   - Pagseguro/Mercado Pago integrado
   - Gera chave após pagamento
   - Email automático

3. **Dashboard web**
   - Ver estatísticas em tempo real
   - Gerenciar chaves pelo navegador

---

## 🎓 DICAS FINAIS

### ✅ FAÇA:
- Sempre use `keymanager_completo.py`
- Faça backup de keys.json semanalmente
- Revogue antes de apagar
- Use notas para identificar clientes
- Teste com chave de 1 dia primeiro

### ❌ NÃO FAÇA:
- Não compartilhe seu token
- Não edite keys.json manualmente
- Não delete chaves sem revogar
- Não compile cliente sem trocar o token
- Não deixe token no código público

---

## 📞 SUPORTE AO CLIENTE

### Script de suporte:

**Cliente: "Não funciona"**
```
Você: Qual erro aparece na tela?
[Cliente envia print]

Se "EXPIRADA": Renove a licença
Se "REVOGADA": Verifique pagamento
Se "HARDWARE DIFERENTE": Desvincule e reative
Se "NÃO CONECTA": Verifique internet
```

**Cliente: "Quero trocar de PC"**
```
Você: 
1. Me passa a chave
2. [Você desvincula]
3. Ative no novo PC normalmente
```

**Cliente: "Expirou, e agora?"**
```
Você:
1. Faça novo pagamento
2. Gero nova chave ou estendo a atual
3. Reative o programa
```

---

## 🔐 SEGURANÇA

### Proteja seu token:
```bash
# Nunca faça:
git add keymanager_completo.py  # Se tem token hardcoded
git push  # Expõe seu token!

# Sempre use variável de ambiente:
set GITHUB_TOKEN=...
```

### Revogue token comprometido:
1. https://github.com/settings/tokens
2. Delete o token antigo
3. Gere novo
4. Atualize: `set GITHUB_TOKEN=novo_token`

---

## ✨ CHANGELOG

### v2.0 - Sistema Completo
- ✅ Gerenciador com 10 funcionalidades
- ✅ Cliente v2 com verificação em tempo real
- ✅ Bloqueio por expiração
- ✅ Bloqueio por revogação
- ✅ Sincronizador GitHub
- ✅ Teste automático
- ✅ 15+ documentos

### v1.0 - Sistema Básico
- Gerenciamento simples
- Cliente sem verificação contínua

---

## 🚀 PRÓXIMOS PASSOS

1. **Configure o token** (`set GITHUB_TOKEN=...`)
2. **Teste o sistema** (`python testar_sistema.py`)
3. **Gere uma chave de teste** (1 dia)
4. **Compile o cliente v2** (troque o token antes!)
5. **Ative em seu PC** (teste completo)
6. **Configure os anúncios** (use os textos prontos)
7. **Faça primeira venda!** 💰

---

**Desenvolvido para BypassPro**  
**Versão 2.0 - Sistema Completo com Verificação em Tempo Real**  

🔥 **Agora suas chaves são protegidas contra pirataria!** 🔥
