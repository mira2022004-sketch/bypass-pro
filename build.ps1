param(
    [Parameter(Mandatory = $true)]
    [string]$GithubToken,
    [string]$Owner = "mira2022004-sketch",
    [string]$Repo = "bypass-pro",
    [string]$OutputDir = $PSScriptRoot
)

$scriptPath = "$PSScriptRoot\client\BypassPro.ps1"
$tempScript = "$env:TEMP\BypassPro_temp.ps1"
$outputExe = "$OutputDir\BypassPro.exe"

$content = Get-Content $scriptPath -Raw
$content = $content -replace 'SEU_GITHUB_TOKEN_AQUI', $GithubToken
$content = $content -replace '(?<=GITHUB_OWNER = ").*?(?=")', $Owner
$content = $content -replace '(?<=GITHUB_REPO = ").*?(?=")', $Repo

Set-Content $tempScript -Value $content -Encoding UTF8

try {
    Invoke-ps2exe -InputFile $tempScript -OutputFile $outputExe -requireAdmin -title "Bypass Pro" -product "Bypass Pro" -description "Reconnect Bypass Tool" -version "1.0.0" -UNICODEEncoding -noOutput -noError -ErrorAction Stop
    Write-Host "EXE gerado com sucesso: $outputExe" -ForegroundColor Green
    Write-Host "Token configurado: $($GithubToken.Substring(0, 8))..." -ForegroundColor Yellow
    Write-Host "Repositorio: $Owner/$Repo" -ForegroundColor Yellow
} catch {
    Write-Host "Erro ao compilar: $_" -ForegroundColor Red
} finally {
    if (Test-Path $tempScript) { Remove-Item $tempScript -Force }
}
