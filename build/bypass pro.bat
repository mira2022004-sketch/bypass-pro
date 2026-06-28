@echo off
title Reconnect Bypass PRO
cls

:: Verifica e solicita privilégios de Administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set "RULE_NAME=7XnIUxGt4Tw13Lzm"

:: Pega o caminho do Steam direto do Registro do Windows (igual ao script Lua)
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v "SteamExe" 2^>nul') do set "STEAM_PATH=%%B"

:: Caso falhe por algum motivo, usa o caminho padrão
if "%STEAM_PATH%"=="" set "STEAM_PATH=C:\Program Files (x86)\Steam\steam.exe"
set "STEAM_PATH=%STEAM_PATH:/=\%"

:menu
cls
color 0F
echo ===================================================
echo               RECONNECT BYPASS PRO                 
echo ===================================================
echo  Diretorio: %STEAM_PATH%
echo ===================================================
echo.

:: Verifica se a regra já existe no Firewall para exibir o status em tempo real
netsh advfirewall firewall show rule name="%RULE_NAME%" >nul 2>&1
if %errorLevel% == 0 (
    color 0C
    echo  [STATUS] STEAM BLOQUEADO ^(Bypass Ativo!^)
) else (
    color 0A
    echo  [STATUS] STEAM LIBERADO ^(Normal / Seguro^)
)

color 0F
echo.
echo  [1] ATIVAR Bloqueio (Cair da partida)
echo  [2] DESATIVAR Bloqueio (Reconectar)
echo  [3] Sair
echo ===================================================
echo.
echo Pressione a tecla correspondente...

:: Captura o clique instantâneo (sem necessidade de dar ENTER)
choice /c 123 /n

if %errorLevel%==1 goto bloco_ativar
if %errorLevel%==2 goto bloco_desativar
if %errorLevel%==3 goto fim
goto menu

:bloco_ativar
netsh advfirewall firewall delete rule name="%RULE_NAME%" >nul 2>&1
netsh advfirewall firewall add rule name="%RULE_NAME%" dir=out action=block program="%STEAM_PATH%" enable=yes >nul 2>&1
goto menu

:bloco_desativar
netsh advfirewall firewall delete rule name="%RULE_NAME%" >nul 2>&1
goto menu

:fim
exit