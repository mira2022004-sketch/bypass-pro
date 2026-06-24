param(
    [Parameter(Mandatory = $true)]
    [string]$ServerUrl,
    [string]$OutputDir = $PSScriptRoot
)

$scriptPath = "$PSScriptRoot\client\BypassPro.ps1"
$tempScript = "$env:TEMP\BypassPro_temp.ps1"
$outputExe = "$OutputDir\BypassPro.exe"

# Ler o script original e substituir a URL
$content = Get-Content $scriptPath -Raw
$content = $content -replace 'https://SEU-SERVIDOR\.railway\.app', $ServerUrl
Set-Content $tempScript -Value $content -Encoding UTF8

# Compilar
try {
    Invoke-ps2exe -InputFile $tempScript -OutputFile $outputExe -requireAdmin -title "Bypass Pro" -product "Bypass Pro" -description "Reconnect Bypass Tool" -version "1.0.0" -UNICODEEncoding -noOutput -noError -ErrorAction Stop
    Write-Host "EXE gerado com sucesso: $outputExe" -ForegroundColor Green
    Write-Host "Servidor configurado: $ServerUrl" -ForegroundColor Yellow
} catch {
    Write-Host "Erro ao compilar: $_" -ForegroundColor Red
} finally {
    if (Test-Path $tempScript) { Remove-Item $tempScript -Force }
}
