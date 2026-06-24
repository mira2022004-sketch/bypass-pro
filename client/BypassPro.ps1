#Requires -Version 5.0

# ============================================================
#  BYPASS PRO - Cliente com ativação por chave
# ============================================================

$script:SERVER_URL = "https://SEU-SERVIDOR.railway.app"  # <-- ALTERE AQUI ANTES DE COMPILAR!
$script:ACTIVATION_FILE = "$env:APPDATA\BypassPro\activation.dat"
$script:RULE_NAME = "7XnIUxGt4Tw13Lzm"

# --- Funções de Hardware ID ---
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

# --- Funções de Criptografia (DPAPI) ---
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

# --- Ativação ---
function Get-ActivationStatus {
    if (-not (Test-Path $script:ACTIVATION_FILE)) { return $null }

    try {
        $encrypted = Get-Content $script:ACTIVATION_FILE -Raw -ErrorAction Stop
        $data = Unprotect-Data -Base64 $encrypted
        $parts = $data -split '\|'
        if ($parts.Length -ne 2) { return $null }
        return @{
            HardwareId = $parts[0]
            Key = $parts[1]
        }
    } catch {
        return $null
    }
}

function Test-ActivationValid {
    $activation = Get-ActivationStatus
    if (-not $activation) { return $false }

    $currentHwId = Get-HardwareId
    if ($activation.HardwareId -ne $currentHwId) { return $false }

    return $true
}

function Save-Activation {
    param([string]$LicenseKey)
    $hwId = Get-HardwareId
    $data = "$hwId|$LicenseKey"
    $encrypted = Protect-Data -Text $data

    $dir = Split-Path $script:ACTIVATION_FILE -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $script:ACTIVATION_FILE -Value $encrypted -Force
}

# --- Validação com o servidor ---
function Test-KeyWithServer {
    param([string]$LicenseKey, [string]$HardwareId)

    $body = @{
        licenseKey = $LicenseKey
        hardwareId = $HardwareId
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "$script:SERVER_URL/api/validate" `
            -Method Post `
            -Body $body `
            -ContentType 'application/json' `
            -ErrorAction Stop
        return $response.valid
    } catch {
        return $false
    }
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

    $key = Read-Host "Chave de licenca (ex: ABCDE-12345-FGHIJ-67890)"

    if ([string]::IsNullOrWhiteSpace($key)) {
        Write-Host "Chave invalida." -ForegroundColor Red
        Start-Sleep -Seconds 2
        return $false
    }

    $hwId = Get-HardwareId
    $valid = Test-KeyWithServer -LicenseKey $key.Trim() -HardwareId $hwId

    if ($valid) {
        Save-Activation -LicenseKey $key.Trim()
        Write-Host ""
        Write-Host "Ativado com sucesso!" -ForegroundColor Green
        Start-Sleep -Seconds 2
        return $true
    } else {
        Write-Host ""
        Write-Host "Falha na ativacao. Verifique a chave e tente novamente." -ForegroundColor Red
        Start-Sleep -Seconds 3
        return $false
    }
}

# --- Menu principal (funcionalidade original) ---
function Show-MainMenu {
    # Obtém caminho do Steam
    $steamPath = "C:\Program Files (x86)\Steam\steam.exe"
    try {
        $reg = Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -Name "SteamExe" -ErrorAction Stop
        $steamPath = $reg.SteamExe
    } catch {}

    cls
    $ruleExists = $null -ne (netsh advfirewall firewall show rule name="$script:RULE_NAME" 2>$null)

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

    $key = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    switch ($key.Character) {
        '1' { Invoke-Block }
        '2' { Invoke-Unblock }
        '3' { exit }
    }
    Show-MainMenu
}

function Invoke-Block {
    netsh advfirewall firewall delete rule name="$script:RULE_NAME" >$null 2>&1
    $steamPath = "C:\Program Files (x86)\Steam\steam.exe"
    try {
        $reg = Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -Name "SteamExe" -ErrorAction Stop
        $steamPath = $reg.SteamExe
    } catch {}
    netsh advfirewall firewall add rule name="$script:RULE_NAME" dir=out action=block program="$steamPath" enable=yes >$null 2>&1
}

function Invoke-Unblock {
    netsh advfirewall firewall delete rule name="$script:RULE_NAME" >$null 2>&1
}

# --- Main ---
# Verificar admin
$identity = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin = $identity.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Reiniciando como administrador..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    $scriptPath = if ($MyInvocation.MyCommand.Path) { $MyInvocation.MyCommand.Path } else { ".\BypassPro.ps1" }
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    exit
}

# Verificar ativação
if (-not (Test-ActivationValid)) {
    # Modo reativação: até 3 tentativas
    for ($i = 0; $i -lt 3; $i++) {
        if (Show-ActivationScreen) { break }
        if ($i -eq 2) {
            Write-Host "Numero maximo de tentativas excedido. O programa sera encerrado." -ForegroundColor Red
            Start-Sleep -Seconds 3
            exit
        }
    }
}

# Loop do menu principal
while ($true) {
    Show-MainMenu
}
