#Requires -Version 5.0

# ============================================================
#  BYPASS PRO V2 - COM VERIFICAÇÃO DE EXPIRAÇÃO EM TEMPO REAL
# ============================================================
Import-Module NetSecurity -ErrorAction SilentlyContinue
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
        $response = Invoke-RestMethod -Uri $script:API -Headers $script:GITHUB_HEADERS -TimeoutSec 10 -ErrorAction Stop
        $content = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($response.content))
        return @{ Keys = ($content | ConvertFrom-Json); Sha = $response.sha }
    } catch {
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
    $keys.$KeyId.hardware = $HardwareId
    $keys.$KeyId.activated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
    $newContent = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes(($keys | ConvertTo-Json -Depth 5 -Compress)))
    $body = @{ message = "ativacao: $KeyId"; content = $newContent; sha = $sha } | ConvertTo-Json -Compress
    try {
        Invoke-RestMethod -Uri $script:API -Method Put -Body $body -Headers $script:GITHUB_HEADERS -TimeoutSec 10 -ErrorAction Stop | Out-Null
        return $true
    } catch { return $false }
}

# --- Validação COMPLETA (usado na ativação inicial) ---
function Test-KeyRemote {
    param([string]$LicenseKey, [string]$HardwareId)
    Write-Host "Verificando chave..." -ForegroundColor Yellow
    $result = Get-KeysFromGitHub
    if (-not $result) { 
        Write-Host "ERRO: Nao foi possivel conectar ao servidor de ativacao." -ForegroundColor Red
        return $false 
    }
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
    if (-not $entry.expires) {
        Write-Host "Chave ainda nao ativada pelo suporte." -ForegroundColor Red
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

# --- Validação RÁPIDA em tempo real (usado a cada uso) ---
function Test-LicenseStillValid {
    param([string]$LicenseKey, [string]$HardwareId)
    
    $result = Get-KeysFromGitHub
    if (-not $result) { 
        return $true
    }
    
    $keys = $result.Keys
    if (-not $keys.$LicenseKey) {
        Write-Host "`n========================================" -ForegroundColor Red
        Write-Host " ERRO: LICENCA INVALIDA!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "Sua chave nao existe mais no servidor." -ForegroundColor Yellow
        Write-Host "Entre em contato com o suporte." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        return $false
    }
    
    $entry = $keys.$LicenseKey
    
    if ($entry.revoked -eq $true) {
        Write-Host "`n========================================" -ForegroundColor Red
        Write-Host " ERRO: LICENCA REVOGADA!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "Sua licenca foi cancelada." -ForegroundColor Yellow
        Write-Host "Entre em contato com o suporte." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        return $false
    }
    
    if (-not $entry.expires) {
        Write-Host "`n========================================" -ForegroundColor Red
        Write-Host " ERRO: CHAVE NAO ATIVADA!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "Esta chave ainda nao possui data de expiracao." -ForegroundColor Yellow
        Write-Host "Entre em contato com o suporte para ativar." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        return $false
    }
    
    try {
        $expires = [DateTime]::ParseExact($entry.expires, "yyyy-MM-dd", $null)
        $now = Get-Date
        
        if ($now -gt $expires) {
            Write-Host "`n========================================" -ForegroundColor Red
            Write-Host " ERRO: LICENCA EXPIRADA!" -ForegroundColor Red
            Write-Host "========================================" -ForegroundColor Red
            Write-Host "Sua licenca expirou em: $($expires.ToString('dd/MM/yyyy'))" -ForegroundColor Yellow
            Write-Host "Renove sua licenca para continuar usando." -ForegroundColor Yellow
            Write-Host "Entre em contato com o suporte." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            return $false
        }
        
        $daysLeft = ($expires - $now).Days
        if ($daysLeft -le 7 -and $daysLeft -gt 0) {
            Write-Host "`nAVISO: Sua licenca expira em $daysLeft dia(s)!" -ForegroundColor Yellow
            Write-Host "Renove em breve para nao perder acesso." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    } catch {
        Write-Host "ERRO: Data de expiracao invalida!" -ForegroundColor Red
        return $false
    }
    
    if (-not $entry.hardware) {
        Write-Host "`nVinculando chave a este computador..." -ForegroundColor Yellow
        $ok = Write-KeyToGitHub -KeyId $LicenseKey -HardwareId $HardwareId
        if (-not $ok) {
            Write-Host "Falha ao vincular chave." -ForegroundColor Red
            Start-Sleep -Seconds 3
            return $false
        }
        Write-Host "Chave vinculada com sucesso!" -ForegroundColor Green
        Start-Sleep -Seconds 1
        return $true
    }
    
    if ($entry.hardware -ne $HardwareId) {
        Write-Host "`n========================================" -ForegroundColor Red
        Write-Host " ERRO: HARDWARE DIFERENTE!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "Esta chave esta vinculada a outro computador." -ForegroundColor Yellow
        Write-Host "Entre em contato com o suporte para desvincular." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        return $false
    }
    
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

# --- Menu principal COM VERIFICAÇÃO A CADA USO ---
function Show-MainMenu {
    $local = Get-LocalActivation
    if (-not $local) {
        Write-Host "ERRO: Dados de ativacao corrompidos!" -ForegroundColor Red
        Write-Host "Reative o programa." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        return $false
    }
    
    $currentHw = Get-HardwareId
    if ($local.HardwareId -ne $currentHw) {
        Write-Host "ERRO: Hardware alterado detectado!" -ForegroundColor Red
        Write-Host "Reative o programa com sua chave." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        return $false
    }
    
    if (-not (Test-LicenseStillValid -LicenseKey $local.Key -HardwareId $currentHw)) {
        Write-Host "`nPrograma sera encerrado..." -ForegroundColor Red
        Start-Sleep -Seconds 2
        return $false
    }
    
    $steamPath = Get-SteamPath
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    cls
    $ruleExists = $null -ne (Get-NetFirewallRule -DisplayName "$script:RULE_NAME" -ErrorAction SilentlyContinue)

    Write-Host "===================================================" -ForegroundColor White
    Write-Host "               RECONNECT BYPASS PRO                 " -ForegroundColor White
    Write-Host "===================================================" -ForegroundColor White
    Write-Host " Steam: $steamPath" -ForegroundColor Gray
    if (-not $isAdmin) { Write-Host " [!] NAO ESTA COMO ADMIN" -ForegroundColor Red }
    
    try {
        $result = Get-KeysFromGitHub
        if ($result -and $result.Keys.$($local.Key)) {
            $entry = $result.Keys.$($local.Key)
            if ($entry.expires) {
                $expires = [DateTime]::ParseExact($entry.expires, "yyyy-MM-dd", $null)
                $daysLeft = ($expires - (Get-Date)).Days
                Write-Host " Licenca: Valida ate $($expires.ToString('dd/MM/yyyy')) ($daysLeft dias)" -ForegroundColor Green
            } else {
                Write-Host " Licenca: Ativa" -ForegroundColor Green
            }
        } else {
            Write-Host " Licenca: Ativa (verificacao offline)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host " Licenca: Ativa (verificacao offline)" -ForegroundColor Yellow
    }
    
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

function Get-SteamPath {
    $p = "C:\Program Files (x86)\Steam\steam.exe"
    if (Test-Path $p) { return $p }
    try {
        $raw = (Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -Name "SteamExe" -ErrorAction Stop).SteamExe
        $raw = $raw.Trim('"', "'").Replace('/', '\')
        if ($raw -and (Test-Path $raw)) { return $raw }
    } catch {}
    return $p
}

function Invoke-Block {
    $steamPath = Get-SteamPath
    try {
        Remove-NetFirewallRule -DisplayName "$script:RULE_NAME" -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "$script:RULE_NAME" -Direction Outbound -Action Block -Program "$steamPath" -Enabled True -ErrorAction Stop | Out-Null
        Write-Host "`nSTEAM BLOQUEADO!" -ForegroundColor Green
    } catch {
        Write-Host "`nERRO:" -ForegroundColor Red -NoNewline
        Write-Host " $($_.Exception.Message)" -ForegroundColor White
    }
    Start-Sleep -Seconds 3
}

function Invoke-Unblock {
    try {
        Remove-NetFirewallRule -DisplayName "$script:RULE_NAME" -ErrorAction Stop
        Write-Host "`nSTEAM LIBERADO!" -ForegroundColor Green
    } catch {
        Write-Host "`nJA ESTA LIBERADO (nenhuma regra encontrada)." -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 2
}

# ===================== MAIN =====================

Write-Host "Iniciando Bypass Pro..." -ForegroundColor Cyan
Write-Host "Verificando licenca..." -ForegroundColor Cyan
Start-Sleep -Seconds 1

$local = Get-LocalActivation
$needActivation = $true

if ($local) {
    $currentHw = Get-HardwareId
    if ($local.HardwareId -eq $currentHw) {
        if (Test-LicenseStillValid -LicenseKey $local.Key -HardwareId $currentHw) {
            $needActivation = $false
        } else {
            Write-Host "`nLicenca invalida ou expirada." -ForegroundColor Red
            Write-Host "Sera necessario reativar." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    } else {
        Write-Host "Hardware diferente detectado." -ForegroundColor Yellow
        Write-Host "Sera necessario reativar." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if ($needActivation) {
    for ($i = 0; $i -lt 3; $i++) {
        if (Show-ActivationScreen) { 
            $needActivation = $false
            break 
        }
        if ($i -eq 2) {
            Write-Host "Numero maximo de tentativas excedido." -ForegroundColor Red
            Start-Sleep -Seconds 3
            exit
        }
    }
    if ($needActivation) { exit }
}

while (Show-MainMenu) {
}

Write-Host "`nEncerrando..." -ForegroundColor Cyan
Start-Sleep -Seconds 1
