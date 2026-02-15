@echo off
chcp 65001 >nul 2>&1
title Audio to Text - Instalador
color 0B

echo.
echo  ========================================
echo     INSTALADOR - Audio to Text
echo     Ruan Almeida - @ruanalmeidar
echo  ========================================
echo.

REM ══════════════════════════════════════════
REM  Detectar pasta do script
REM ══════════════════════════════════════════
set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%mt.py" (
    echo  [ERRO] Arquivo mt.py nao encontrado!
    echo.
    echo  Coloque este .bat na MESMA PASTA
    echo  que o arquivo mt.py
    echo.
    pause
    exit /b 1
)
echo  [OK] mt.py encontrado em:
echo       %SCRIPT_DIR%
echo.

REM ══════════════════════════════════════════
REM  Verificar Python
REM ══════════════════════════════════════════
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado!
    echo.
    echo  Instale o Python ou Anaconda primeiro.
    echo  https://www.anaconda.com/download
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK] %%v
echo.

REM ══════════════════════════════════════════
REM  Instalar dependencias
REM ══════════════════════════════════════════
echo  [1/5] Instalando dependencias...
echo        (pode demorar na primeira vez)
echo.

pip install openai-whisper 2>&1 | findstr /i /c:"Successfully" /c:"already satisfied" /c:"Requirement"
if errorlevel 1 (
    echo        Instalando...
    pip install openai-whisper
)

echo.
echo  [OK] Dependencias instaladas
echo.

REM ══════════════════════════════════════════
REM  Detectar Anaconda / Miniconda
REM ══════════════════════════════════════════
set "CONDA_ACTIVATE="
set "CONDA_PREFIX="

for %%d in (
    "%USERPROFILE%\anaconda3"
    "%USERPROFILE%\Anaconda3"
    "%USERPROFILE%\miniconda3"
    "%USERPROFILE%\Miniconda3"
    "%LOCALAPPDATA%\anaconda3"
    "%LOCALAPPDATA%\Anaconda3"
    "%LOCALAPPDATA%\miniconda3"
    "%LOCALAPPDATA%\Miniconda3"
    "%PROGRAMDATA%\anaconda3"
    "%PROGRAMDATA%\Anaconda3"
    "C:\anaconda3"
    "C:\Anaconda3"
    "C:\ProgramData\anaconda3"
) do (
    if exist "%%~d\Scripts\activate.bat" (
        if not defined CONDA_ACTIVATE (
            set "CONDA_ACTIVATE=%%~d\Scripts\activate.bat"
            set "CONDA_PREFIX=%%~d"
        )
    )
)

REM ══════════════════════════════════════════
REM  Detectar pythonw.exe
REM ══════════════════════════════════════════
set "PYTHONW_PATH="
for /f "delims=" %%i in ('where pythonw 2^>nul') do (
    if not defined PYTHONW_PATH set "PYTHONW_PATH=%%i"
)
if not defined PYTHONW_PATH (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if not defined PYTHONW_PATH set "PYTHONW_PATH=%%i"
    )
)

REM ══════════════════════════════════════════
REM  Criar lancador (AudioToText.bat)
REM ══════════════════════════════════════════
echo  [2/5] Criando lancador...

set "LAUNCHER=%SCRIPT_DIR%AudioToText.bat"

if defined CONDA_ACTIVATE (
    echo        Anaconda detectado: %CONDA_PREFIX%

    (
        echo @echo off
        echo call "%CONDA_ACTIVATE%" "%CONDA_PREFIX%" ^>nul 2^>^&1
        echo cd /d "%SCRIPT_DIR%"
        echo start "" /b pythonw "%SCRIPT_DIR%mt.py"
        echo exit /b
    ) > "%LAUNCHER%"
) else (
    echo        Python regular: %PYTHONW_PATH%

    (
        echo @echo off
        echo cd /d "%SCRIPT_DIR%"
        echo start "" /b "%PYTHONW_PATH%" "%SCRIPT_DIR%mt.py"
        echo exit /b
    ) > "%LAUNCHER%"
)

if exist "%LAUNCHER%" (
    echo  [OK] Lancador criado: AudioToText.bat
) else (
    echo  [ERRO] Falha ao criar lancador!
    echo         Verifique permissoes da pasta.
    pause
    exit /b 1
)

echo.

REM ══════════════════════════════════════════
REM  Criar atalho via VBScript (mais confiavel)
REM ══════════════════════════════════════════
echo  [3/5] Criando atalho na area de trabalho...

REM Detectar pasta Desktop real do Windows
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"

REM Fallback se powershell falhar
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Área de Trabalho"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Desktop"

echo        Desktop: %DESKTOP%

REM Criar VBScript temporario para gerar o atalho
set "VBS_TEMP=%TEMP%\criar_atalho_att.vbs"

(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo Set lnk = WshShell.CreateShortcut^("%DESKTOP%\Audio to Text.lnk"^)
    echo lnk.TargetPath = "%LAUNCHER%"
    echo lnk.WorkingDirectory = "%SCRIPT_DIR%"
    echo lnk.Description = "Audio to Text - Ruan Almeida"
    echo lnk.WindowStyle = 7
    echo lnk.Save
) > "%VBS_TEMP%"

REM Executar VBScript
cscript //nologo "%VBS_TEMP%" >nul 2>&1

REM Verificar resultado
if exist "%DESKTOP%\Audio to Text.lnk" (
    echo  [OK] Atalho "Audio to Text" criado com sucesso!
) else (
    echo  [!] Metodo VBS falhou. Tentando metodo alternativo...

    REM Tentativa alternativa: copiar o .bat direto pro desktop
    copy "%LAUNCHER%" "%DESKTOP%\Audio to Text.bat" >nul 2>&1

    if exist "%DESKTOP%\Audio to Text.bat" (
        echo  [OK] Lancador copiado para o Desktop.
        echo       Use "Audio to Text.bat" no Desktop.
    ) else (
        echo.
        echo  [!] Nao conseguiu criar atalho automaticamente.
        echo.
        echo      CRIE MANUALMENTE:
        echo      1. Clique com botao direito no Desktop
        echo      2. Novo ^> Atalho
        echo      3. Cole este caminho:
        echo         "%LAUNCHER%"
        echo      4. Nomeie como "Audio to Text"
        echo.
    )
)

REM Limpar VBS temporario
del "%VBS_TEMP%" >nul 2>&1

echo.

REM ══════════════════════════════════════════
REM  Teste rapido
REM ══════════════════════════════════════════
echo  [4/5] Verificando instalacao...
echo.

python -c "import whisper; print('        whisper:', whisper.__version__)" 2>nul
if errorlevel 1 echo        [!] whisper nao importou corretamente

python -c "import torch; print('        torch:', torch.__version__); print('        CUDA:', torch.cuda.is_available())" 2>nul
if errorlevel 1 echo        [!] torch nao importou corretamente

echo.

REM ══════════════════════════════════════════
REM  Teste de execucao
REM ══════════════════════════════════════════
echo  [5/5] Testando programa...

python -c "import tkinter; print('        tkinter: OK')" 2>nul
if errorlevel 1 echo        [!] tkinter nao disponivel

echo.

REM ══════════════════════════════════════════
REM  Resumo final
REM ══════════════════════════════════════════
echo  ========================================
echo     RESULTADO DA INSTALACAO
echo  ========================================
echo.

if exist "%SCRIPT_DIR%mt.py" (
    echo     [OK] mt.py
) else (
    echo     [X]  mt.py NAO ENCONTRADO
)

if exist "%LAUNCHER%" (
    echo     [OK] Lancador AudioToText.bat
) else (
    echo     [X]  Lancador NAO CRIADO
)

if exist "%DESKTOP%\Audio to Text.lnk" (
    echo     [OK] Atalho no Desktop (.lnk)
) else if exist "%DESKTOP%\Audio to Text.bat" (
    echo     [OK] Lancador no Desktop (.bat)
) else (
    echo     [!]  Atalho no Desktop NAO CRIADO
    echo          Crie manualmente (veja acima)
)

echo.
echo  ========================================
echo.

if exist "%DESKTOP%\Audio to Text.lnk" (
    echo     Tudo pronto!
    echo     Dois cliques em "Audio to Text"
    echo     no Desktop para usar.
) else if exist "%DESKTOP%\Audio to Text.bat" (
    echo     Tudo pronto!
    echo     Dois cliques em "Audio to Text"
    echo     no Desktop para usar.
) else (
    echo     Programa instalado com sucesso.
    echo     Crie o atalho manualmente.
)

echo.
echo  ========================================
echo.

set /p ABRIR="  Deseja abrir o programa agora? (S/N): "
if /i "%ABRIR%"=="S" (
    echo.
    echo  Abrindo...
    cd /d "%SCRIPT_DIR%"
    if defined CONDA_ACTIVATE (
        call "%CONDA_ACTIVATE%" "%CONDA_PREFIX%" >nul 2>&1
    )
    start "" pythonw "%SCRIPT_DIR%mt.py"
    echo  [OK] Programa iniciado!
    echo.
    timeout /t 3 >nul
) else (
    echo.
    pause
)