# 🔨 COMO COMPILAR O CLIENTE V2

## ⚠️ IMPORTANTE: TROCAR O TOKEN ANTES!

Antes de compilar, **OBRIGATORIAMENTE** troque o token no arquivo!

---

## 📝 PASSO 1: EDITAR O TOKEN

Abra `client/BypassPro_v2.ps1` e encontre esta linha:

```powershell
$script:GITHUB_TOKEN = "SEU_GITHUB_TOKEN_AQUI"
```

**Substitua por:**
```powershell
$script:GITHUB_TOKEN = "ghp_seu_token_real_aqui"
```

⚠️ **NUNCA compile sem trocar! O token é necessário para validar licenças.**

---

## 🔧 PASSO 2: INSTALAR PS2EXE

### Abra PowerShell como Administrador:

```powershell
# Permitir scripts
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar ps2exe
Install-Module -Name ps2exe -Scope CurrentUser -Force
```

Se pedir confirmação, digite **Y** e Enter.

---

## 🎨 PASSO 3: CRIAR ÍCONE (Opcional)

Coloque um arquivo `icon.ico` na pasta raiz do projeto.

Pode baixar ícones gratuitos em:
- https://www.iconarchive.com
- https://icons8.com

---

## 🚀 PASSO 4: COMPILAR

### Navegue até a pasta do projeto:
```powershell
cd "C:\Users\Administrador\Desktop\progrma anti kick"
```

### Compile COM ícone:
```powershell
Invoke-ps2exe `
  -inputFile "client/BypassPro_v2.ps1" `
  -outputFile "BypassPro.exe" `
  -requireAdmin `
  -noConsole `
  -title "Bypass Pro" `
  -description "Reconnect Tool Profissional" `
  -company "Seu Nome" `
  -product "BypassPro" `
  -copyright "© 2026 Seu Nome" `
  -version "2.0.0.0" `
  -iconFile "icon.ico"
```

### Compile SEM ícone:
```powershell
Invoke-ps2exe `
  -inputFile "client/BypassPro_v2.ps1" `
  -outputFile "BypassPro.exe" `
  -requireAdmin `
  -noConsole `
  -title "Bypass Pro" `
  -description "Reconnect Tool Profissional" `
  -company "Seu Nome" `
  -product "BypassPro" `
  -copyright "© 2026 Seu Nome" `
  -version "2.0.0.0"
```

---

## ✅ PASSO 5: TESTAR

### Execute o .exe gerado:
```powershell
.\BypassPro.exe
```

**Deve:**
1. Pedir permissão de administrador
2. Mostrar tela de ativação
3. Validar chave online

### Teste com chave de teste:
```bash
# Gere uma chave de 1 dia para teste
python keymanager_completo.py
Opção: 1
Dias: 1
Quantidade: 1
```

---

## 🎯 OPÇÕES DE COMPILAÇÃO

### Explicação dos parâmetros:

| Parâmetro | O que faz |
|-----------|-----------|
| `-requireAdmin` | Força execução como admin |
| `-noConsole` | Sem janela preta (interface limpa) |
| `-title` | Título na barra de tarefas |
| `-description` | Descrição nas propriedades |
| `-company` | Seu nome/empresa |
| `-version` | Versão do programa |
| `-iconFile` | Ícone do executável |

### Modos de console:

**Com console** (para debug):
```powershell
Invoke-ps2exe -inputFile "client/BypassPro_v2.ps1" -outputFile "BypassPro_debug.exe" -requireAdmin
```

**Sem console** (para venda):
```powershell
Invoke-ps2exe -inputFile "client/BypassPro_v2.ps1" -outputFile "BypassPro.exe" -requireAdmin -noConsole
```

---

## 🔐 SEGURANÇA DO TOKEN

### ⚠️ ATENÇÃO:

O token fica **HARDCODED** no executável!

Isso significa:
- ✅ Funciona sem configuração do cliente
- ❌ Alguém pode extrair o token do .exe

### Proteções:

1. **Use token com permissão mínima**
   - Apenas acesso ao repositório `bypass-pro`
   - Não dê acesso a outros repos

2. **Monitore o uso**
   - GitHub mostra uso da API
   - Se houver abuso, revogue e gere novo

3. **Criptografia extra (avançado)**
   ```powershell
   # Ofuscar o token no código
   $script:GITHUB_TOKEN = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("Z2hwX3NldV90b2tlbl9hcXVp"))
   ```

---

## 📦 DISTRIBUIÇÃO

### Criar pacote para cliente:

```
BypassPro_v2.0/
├── BypassPro.exe          ← Executável
├── LEIA-ME.txt            ← Instruções de instalação
└── Licenca.txt            ← Termos de uso
```

### LEIA-ME.txt:
```
BYPASS PRO - INSTALAÇÃO

1. Execute BypassPro.exe como Administrador
2. Clique em "Sim" quando o Windows perguntar
3. Digite sua chave de licença
4. Pronto! Use as opções 1 e 2 no menu

REQUISITOS:
- Windows 10 ou 11
- Permissões de Administrador
- Internet (apenas na primeira ativação)

SUPORTE:
[seu email/WhatsApp]
```

---

## 🐛 PROBLEMAS COMUNS

### ❌ "ps2exe não reconhecido"
```powershell
# Reinstale o módulo
Install-Module -Name ps2exe -Scope CurrentUser -Force
Import-Module ps2exe
```

### ❌ "Arquivo não pode ser carregado"
```powershell
# Libere a execução de scripts
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ ".exe não executa"
- Clique com botão direito → "Executar como administrador"
- Windows Defender pode bloquear (adicione exceção)

### ❌ "Token inválido" no .exe
- Você esqueceu de trocar o token antes de compilar!
- Edite o .ps1, troque o token, compile novamente

---

## 📊 VERSÕES

### Debug (com console):
```powershell
Invoke-ps2exe -inputFile "client/BypassPro_v2.ps1" -outputFile "BypassPro_DEBUG.exe" -requireAdmin
```
**Use para:** Testar e ver erros

### Release (sem console):
```powershell
Invoke-ps2exe -inputFile "client/BypassPro_v2.ps1" -outputFile "BypassPro.exe" -requireAdmin -noConsole
```
**Use para:** Vender aos clientes

---

## 🎁 EXTRAS

### Adicionar splash screen:
```powershell
# No início do BypassPro_v2.ps1, adicione:
Write-Host @"
╔════════════════════════════════╗
║      BYPASS PRO v2.0           ║
║   Reconnect Tool Professional  ║
╚════════════════════════════════╝
"@ -ForegroundColor Cyan
Start-Sleep -Seconds 2
```

### Verificação de integridade:
```powershell
# Adicione no início:
$expectedHash = "ABC123..."  # Hash do próprio arquivo
# Detecta se foi modificado
```

---

## ✅ CHECKLIST FINAL

Antes de distribuir:

- [ ] Token substituído no código
- [ ] Compilado com `-noConsole`
- [ ] Testado em outro PC
- [ ] Testou ativação com chave real
- [ ] Testou expiração (mude data no GitHub)
- [ ] Testou revogação
- [ ] Windows Defender não bloqueia
- [ ] Ícone aplicado corretamente
- [ ] Criou LEIA-ME.txt
- [ ] Criou pasta de distribuição

---

## 🔄 ATUALIZAR CLIENTES

Quando lançar v3:

1. Compile novo executável
2. Avise clientes via email/WhatsApp
3. Disponibilize link de download
4. Opcionalmente: force atualização via GitHub
   ```json
   "min_version": "2.0.0"
   ```

---

**Agora está pronto para compilar e vender!** 🚀

Se tiver dúvidas, consulte:
- `GUIA_COMPLETO.md` - Manual geral
- `README_KEYMANAGER.md` - Gerenciamento de chaves
