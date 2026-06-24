#Requires -Version 5.0

# ============================================================
#  BYPASS PRO - Ativação via GitHub
# ============================================================
$script:GITHUB_TOKEN = "SEU_GITHUB_TOKEN_AQUI"
$script:GITHUB_OWNER = "mira2022004-sketch"
$script:GITHUB_REPO = "bypass-pro"
$script:KEYS_FILE = "keys.json"
# ============================================================

$script:ACTIVATION_FILE = "$env:APPDATA\BypassPro\activation.dat"
$script:RULE_NAME = "7XnIUxGt4Tw13Lzm"
$script:API = "https://api.github.com/repos/$($script:GITHUB_OWNER)/$($script:GITHUB_REPO)/contents/$($script:KEYS_FILE)"
$script:GITHUB_HEADERS = @{ Authorization = "Bearer $($script:GITHUB_TOKEN)"; Accept = "application/vnd.github.v3+json" }

# --- Hardware ID ---
function Get-HardwareId {
    $mac = (Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | Select-Object -First 1).MacAddress
    if (-not $mac) { $mac = '00-00-00-00-00-00' }
    $vol = (Get-Volume -DriveLetter C).SerialNumber
    if (-not $vol) { $vol = '0000-0000' }
    $raw = "$mac|$vol"
    $hash = [System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($raw))
    ).Replace('-', '').Substring(0, 32)
    return $hash
}

# --- DPAPI ---
function Protect-Data {
    param([string]$Text)
    Add-Type -AssemblyName System.Security
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $encrypted = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, 'CurrentUser')
    return [Convert]::ToBase64String($encrypted)
}

function Unprotect-Data {
    param([string]$Base64)
    Add-Type -AssemblyName System.Security
    $bytes = [Convert]::FromBase64String($Base64)
    $decrypted = [System.Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, 'CurrentUser')
    return [System.Text.Encoding]::UTF8.GetString($decrypted)
}

# --- Ativação local ---
function Get-LocalActivation {
    if (-not (Test-Path $script:ACTIVATION_FILE)) { return $null }
    try {
        $encrypted = Get-Content $script:ACTIVATION_FILE -Raw -ErrorAction Stop
        $data = Unprotect-Data -Base64 $encrypted
        $parts = $data -split '\|'
        if ($parts.Length -ne 2) { return $null }
        return @{ HardwareId = $parts[0]; Key = $parts[1] }
    } catch { return $null }
}

function Save-LocalActivation {
    param([string]$LicenseKey)
    $hwId = Get-HardwareId
    $data = "$hwId|$LicenseKey"
    $encrypted = Protect-Data -Text $data
    $dir = Split-Path $script:ACTIVATION_FILE -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $script:ACTIVATION_FILE -Value $encrypted -Force
}

# --- GitHub API ---
function Get-KeysFromGitHub {
    try {
        $response = Invoke-RestMethod -Uri $script:API -Headers $script:GITHUB_HEADERS -ErrorAction Stop
        $content = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($response.content))
        return @{ Keys = ($content | ConvertFrom-Json); Sha = $response.sha }
    } catch {
        Write-Host "ERRO: Nao foi possivel conectar ao servidor de ativacao." -ForegroundColor Red
        Write-Host "Detalhes: $_" -ForegroundColor DarkRed
        return $null
    }
}

function Write-KeyToGitHub {
    param([string]$KeyId, [string]$HardwareId)
    $result = Get-KeysFromGitHub
    if (-not $result) { return $false }
    $keys = $result.Keys
    $sha = $result.Sha
    if (-not $keys.$KeyId) { return $false }
    if ($keys.$KeyId.hardware) { return $false }
    $keys.$KeyId.hardware = $HardwareId
    $newContent = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes(($keys | ConvertTo-Json -Depth 5)))
    $body = @{ message = "ativacao: $KeyId"; content = $newContent; sha = $sha } | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri $script:API -Method Put -Body $body -Headers $script:GITHUB_HEADERS -ErrorAction Stop | Out-Null
        return $true
    } catch { return $false }
}

# --- Validação ---
function Test-KeyRemote {
    param([string]$LicenseKey, [string]$HardwareId)
    Write-Host "Verificando chave..." -ForegroundColor Yellow
    $result = Get-KeysFromGitHub
    if (-not $result) { return $false }
    $keys = $result.Keys
    if (-not $keys.$LicenseKey) {
        Write-Host "Chave nao encontrada no servidor." -ForegroundColor Red
        return $false
    }
    $entry = $keys.$LicenseKey
    if ($entry.revoked -eq $true) {
        Write-Host "Esta chave foi revogada." -ForegroundColor Red
        return $false
    }
    try {
        $expires = [DateTime]::ParseExact($entry.expires, "yyyy-MM-dd", $null)
        if ((Get-Date) -gt $expires) {
            Write-Host "Chave expirada em $($entry.expires)." -ForegroundColor Red
            return $false
        }
    } catch { return $false }
    if ($entry.hardware -and $entry.hardware -ne $HardwareId) {
        Write-Host "Chave ja ativada em outro computador." -ForegroundColor Red
        return $false
    }
    if (-not $entry.hardware) {
        Write-Host "Vinculando chave a este computador..." -ForegroundColor Yellow
        $ok = Write-KeyToGitHub -KeyId $LicenseKey -HardwareId $HardwareId
        if (-not $ok) {
            Write-Host "Falha ao vincular chave. Tente novamente." -ForegroundColor Red
            return $false
        }
    }
    Write-Host "Chave validada com sucesso!" -ForegroundColor Green
    return $true
}

# --- Tela de Ativação ---
function Show-ActivationScreen {
    cls
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "           BYPASS PRO - ATIVACAO                    " -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Este programa requer ativacao." -ForegroundColor Yellow
    Write-Host "Digite sua chave de licenca para continuar." -ForegroundColor Yellow
    Write-Host ""

    $key = Read-Host "Chave de licenca"
    if ([string]::IsNullOrWhiteSpace($key)) {
        Write-Host "Chave invalida." -ForegroundColor Red
        Start-Sleep -Seconds 2; return $false
    }

    $hwId = Get-HardwareId
    $valid = Test-KeyRemote -LicenseKey $key.Trim() -HardwareId $hwId

    if ($valid) {
        Save-LocalActivation -LicenseKey $key.Trim()
        Write-Host ""
        Write-Host "ATIVADO COM SUCESSO!" -ForegroundColor Green
        Write-Host "O menu sera exibido em instantes..." -ForegroundColor Green
        Start-Sleep -Seconds 2; return $true
    } else {
        Write-Host ""
        Write-Host "Falha na ativacao." -ForegroundColor Red
        Start-Sleep -Seconds 3; return $false
    }
}

# --- Menu principal ---
function Show-MainMenu {
    $steamPath = "C:\Program Files (x86)\Steam\steam.exe"
    try {
        $reg = Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -Name "SteamExe" -ErrorAction Stop
        $steamPath = $reg.SteamExe
    } catch {}

    $n = "$env:windir\system32\netsh.exe"
    cls
    $ruleExists = $null -ne (& $n advfirewall firewall show rule name="$script:RULE_NAME" 2>$null)

    Write-Host "===================================================" -ForegroundColor White
    Write-Host "               RECONNECT BYPASS PRO                 " -ForegroundColor White
    Write-Host "===================================================" -ForegroundColor White
    Write-Host " Steam: $steamPath" -ForegroundColor Gray
    Write-Host "===================================================" -ForegroundColor White
    Write-Host ""

    if ($ruleExists) {
        Write-Host " [STATUS] STEAM BLOQUEADO (Bypass Ativo!)" -ForegroundColor Red
    } else {
        Write-Host " [STATUS] STEAM LIBERADO (Normal / Seguro)" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host " [1] ATIVAR Bloqueio (Cair da partida)" -ForegroundColor Yellow
    Write-Host " [2] DESATIVAR Bloqueio (Reconectar)" -ForegroundColor Yellow
    Write-Host " [3] Sair" -ForegroundColor Yellow
    Write-Host "===================================================" -ForegroundColor White
    Write-Host ""
    Write-Host "Pressione a tecla correspondente..." -NoNewline

    $k = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    switch ($k.Character) {
        '1' { Invoke-Block }
        '2' { Invoke-Unblock }
        '3' { return $false }
    }
    return $true
}

function Invoke-Block {
    $n = "$env:windir\system32\netsh.exe"
    $steamPath = "C:\Program Files (x86)\Steam\steam.exe"
    try { $reg = Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -Name "SteamExe" -ErrorAction Stop; $steamPath = $reg.SteamExe } catch {}
    & $n advfirewall firewall delete rule name="$script:RULE_NAME" | Out-Null
    & $n advfirewall firewall add rule name="$script:RULE_NAME" dir=out action=block program="$steamPath" enable=yes | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "STEAM BLOQUEADO com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Falha ao bloquear. Execute como Administrador." -ForegroundColor Red
    }
    Start-Sleep -Seconds 1
}

function Invoke-Unblock {
    $n = "$env:windir\system32\netsh.exe"
    & $n advfirewall firewall delete rule name="$script:RULE_NAME" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "STEAM LIBERADO com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Falha ao liberar. Execute como Administrador." -ForegroundColor Red
    }
    Start-Sleep -Seconds 1
}

# ===================== MAIN =====================
# O ps2exe com -requireAdmin já garante execução como admin
# Não precisa do bloco de restart manual

# Verificar ativação
$local = Get-LocalActivation
$needActivation = $true

if ($local) {
    $currentHw = Get-HardwareId
    if ($local.HardwareId -eq $currentHw) {
        try {
            $result = Get-KeysFromGitHub
            if ($result -and $result.Keys.$($local.Key)) {
                $entry = $result.Keys.$($local.Key)
                if ($entry.revoked -ne $true) {
                    $expires = [DateTime]::ParseExact($entry.expires, "yyyy-MM-dd", $null)
                    if ((Get-Date) -le $expires) {
                        $needActivation = $false
                    }
                }
            }
        } catch {}
    }
}

if ($needActivation) {
    for ($i = 0; $i -lt 3; $i++) {
        if (Show-ActivationScreen) { $needActivation = $false; break }
        if ($i -eq 2) {
            Write-Host "Numero maximo de tentativas excedido." -ForegroundColor Red
            Start-Sleep -Seconds 3; exit
        }
    }
    if ($needActivation) { exit }
}

# Loop principal
while (Show-MainMenu) {}
