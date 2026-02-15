@echo off
chcp 65001 >nul 2>&1
title Audio to Text - Criar Executavel
color 0E

echo.
echo  ========================================
echo     CRIAR EXECUTAVEL - Audio to Text
echo     Ruan Almeida - @ruanalmeidar
echo  ========================================
echo.
echo  AVISO:
echo    - O executavel tera entre 2 e 5 GB
echo    - A criacao demora 10-30 minutos
echo    - Requer bastante espaco em disco
echo.
echo  Pressione qualquer tecla para continuar
echo  ou FECHE esta janela para cancelar.
echo.
pause >nul

set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%mt.py" (
    echo  [ERRO] mt.py nao encontrado na mesma pasta!
    echo.
    echo  Coloque este .bat na MESMA PASTA
    echo  que o arquivo mt.py
    echo.
    pause
    exit /b 1
)

echo.
echo  [OK] mt.py encontrado
echo.

REM ══════════════════════════════════════════
REM  Verificar Python
REM ══════════════════════════════════════════
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado!
    echo  Instale o Python ou rode INSTALAR.bat primeiro.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK] %%v
echo.

REM ══════════════════════════════════════════
REM  Verificar whisper
REM ══════════════════════════════════════════
python -c "import whisper" >nul 2>&1
if errorlevel 1 (
    echo  [!] Whisper nao encontrado. Instalando...
    pip install openai-whisper
    echo.
)

REM ══════════════════════════════════════════
REM  Instalar PyInstaller
REM ══════════════════════════════════════════
echo  [1/6] Instalando PyInstaller...
pip install pyinstaller 2>&1 | findstr /i /c:"Successfully" /c:"already satisfied" /c:"Requirement"
if errorlevel 1 (
    pip install pyinstaller
)
echo  [OK] PyInstaller pronto
echo.

REM ══════════════════════════════════════════
REM  Detectar Desktop real
REM ══════════════════════════════════════════
echo  [2/6] Detectando Desktop...

for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"

if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Área de Trabalho"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Desktop"

echo        Desktop: %DESKTOP%
echo.

REM ══════════════════════════════════════════
REM  Limpar build anterior
REM ══════════════════════════════════════════
echo  [3/6] Limpando build anterior...

if exist "%SCRIPT_DIR%build" (
    rmdir /s /q "%SCRIPT_DIR%build" >nul 2>&1
    echo        Pasta build/ removida
)
if exist "%SCRIPT_DIR%dist\AudioToText" (
    rmdir /s /q "%SCRIPT_DIR%dist\AudioToText" >nul 2>&1
    echo        Pasta dist/AudioToText/ removida
)
if exist "%SCRIPT_DIR%AudioToText.spec" (
    del "%SCRIPT_DIR%AudioToText.spec" >nul 2>&1
    echo        AudioToText.spec removido
)

echo  [OK] Limpo
echo.

REM ══════════════════════════════════════════
REM  Criar executavel
REM ══════════════════════════════════════════
echo  [4/6] Criando executavel...
echo        Isso vai demorar bastante, aguarde...
echo        (NAO feche esta janela)
echo.
echo  ----------------------------------------

pyinstaller ^
    --noconfirm ^
    --windowed ^
    --name "AudioToText" ^
    --collect-all whisper ^
    --collect-all torch ^
    "%SCRIPT_DIR%mt.py"

echo  ----------------------------------------
echo.

if errorlevel 1 (
    echo  [ERRO] Falha ao criar executavel.
    echo.
    echo  Possiveis causas:
    echo    - Falta de espaco em disco
    echo    - Antivirus bloqueando
    echo    - Dependencia corrompida
    echo.
    echo  Tente:
    echo    1. Desativar antivirus temporariamente
    echo    2. pip install --upgrade pyinstaller
    echo    3. Rodar novamente
    echo.
    pause
    exit /b 1
)

REM Verificar se o exe foi criado
if not exist "%SCRIPT_DIR%dist\AudioToText\AudioToText.exe" (
    echo  [ERRO] Executavel nao foi gerado.
    echo         Verifique os erros acima.
    echo.
    pause
    exit /b 1
)

echo  [OK] Executavel criado com sucesso!
echo.

REM ══════════════════════════════════════════
REM  Copiar para o Desktop
REM ══════════════════════════════════════════
echo  [5/6] Copiando para o Desktop...

set "DEST=%DESKTOP%\AudioToText"

REM Remover destino anterior se existir
if exist "%DEST%" (
    echo        Removendo versao anterior...
    rmdir /s /q "%DEST%" >nul 2>&1
)

xcopy /E /I /Y /Q "%SCRIPT_DIR%dist\AudioToText" "%DEST%" >nul 2>&1

if not exist "%DEST%\AudioToText.exe" (
    echo  [!] Falha ao copiar para Desktop.
    echo      O executavel esta em:
    echo      %SCRIPT_DIR%dist\AudioToText\AudioToText.exe
    echo.
    echo      Copie manualmente a pasta "dist\AudioToText"
    echo      para onde desejar.
    echo.
    pause
    exit /b 1
)

echo  [OK] Copiado para: %DEST%\
echo.

REM ══════════════════════════════════════════
REM  Criar atalho via VBScript
REM ══════════════════════════════════════════
echo  [6/6] Criando atalho no Desktop...

set "VBS_TEMP=%TEMP%\criar_atalho_exe.vbs"
set "LNK_PATH=%DESKTOP%\Audio to Text.lnk"
set "EXE_PATH=%DEST%\AudioToText.exe"

(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo Set lnk = WshShell.CreateShortcut^("%LNK_PATH%"^)
    echo lnk.TargetPath = "%EXE_PATH%"
    echo lnk.WorkingDirectory = "%DEST%"
    echo lnk.Description = "Audio to Text - Ruan Almeida"
    echo lnk.WindowStyle = 1
    echo lnk.Save
) > "%VBS_TEMP%"

cscript //nologo "%VBS_TEMP%" >nul 2>&1

del "%VBS_TEMP%" >nul 2>&1

if exist "%LNK_PATH%" (
    echo  [OK] Atalho "Audio to Text" criado no Desktop!
) else (
    echo  [!] Atalho nao criado automaticamente.
    echo      Use diretamente:
    echo      %EXE_PATH%
)

echo.

REM ══════════════════════════════════════════
REM  Resumo final
REM ══════════════════════════════════════════
echo  ========================================
echo     RESULTADO
echo  ========================================
echo.

if exist "%EXE_PATH%" (
    echo     [OK] Executavel:
    echo          %EXE_PATH%
) else (
    echo     [X]  Executavel NAO ENCONTRADO
)

if exist "%LNK_PATH%" (
    echo     [OK] Atalho no Desktop
) else (
    echo     [!]  Atalho NAO CRIADO
)

REM Mostrar tamanho da pasta
for /f "tokens=3" %%s in ('dir /s "%DEST%" 2^>nul ^| findstr /i "bytes" ^| findstr /v /i "free"') do (
    set "TOTAL_SIZE=%%s"
)
if defined TOTAL_SIZE (
    echo.
    echo     Tamanho total: %TOTAL_SIZE% bytes
)

echo.
echo  ========================================
echo.
echo     Para usar: dois cliques em
echo     "Audio to Text" no Desktop
echo.
echo     Ou abra diretamente:
echo     %EXE_PATH%
echo.
echo  ========================================
echo.

REM ══════════════════════════════════════════
REM  Limpeza opcional
REM ══════════════════════════════════════════
echo  Deseja remover arquivos temporarios de build?
echo  (pasta build/, dist/ e .spec na pasta do script)
echo.
set /p LIMPAR="  Limpar? (S/N): "
if /i "%LIMPAR%"=="S" (
    rmdir /s /q "%SCRIPT_DIR%build" 2>nul
    rmdir /s /q "%SCRIPT_DIR%dist" 2>nul
    del "%SCRIPT_DIR%AudioToText.spec" 2>nul
    echo.
    echo  [OK] Arquivos temporarios removidos.
)

echo.

REM ══════════════════════════════════════════
REM  Abrir agora?
REM ══════════════════════════════════════════
set /p ABRIR="  Deseja testar o executavel agora? (S/N): "
if /i "%ABRIR%"=="S" (
    echo.
    echo  Abrindo...
    start "" "%EXE_PATH%"
    echo  [OK] Executavel iniciado!
    echo.
    timeout /t 3 >nul
) else (
    echo.
    pause
)