@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem Kullanım: baslat.bat            -> NVIDIA CUDA (.venv)
rem           baslat.bat directml   -> DirectX 12 yedek yolu (.venv-dml)
set "VENV=.venv"
set "EXTRA="
if /i "%~1"=="directml" set "VENV=.venv-dml"
if /i "%~1"=="directml" set "EXTRA=--no-cuda"

if not exist "%VENV%\Scripts\python.exe" (
    echo [HATA] "%VENV%" sanal ortamı bulunamadı. Önce kurulum.bat dosyasını çalıştırın.
    pause
    exit /b 1
)

set "PATH=%~dp0_tools\ffmpeg;%PATH%"
echo DeepFaceLive başlatılıyor... Bu pencereyi kapatmayın, uygulama günlükleri burada görünür.
"%VENV%\Scripts\python.exe" main.py run DeepFaceLive --userdata-dir "%~dp0userdata" %EXTRA%
if errorlevel 1 (
    echo.
    echo [HATA] Uygulama hata koduyla kapandı. Yukarıdaki mesajlara bakın.
    pause
)
