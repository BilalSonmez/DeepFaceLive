@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem Kullanım: kurulum.bat            -> NVIDIA CUDA ortamı (.venv)
rem           kurulum.bat directml   -> DirectX 12 yedek ortamı (.venv-dml)
set "VENV=.venv"
set "REQ=requirements-rtx50.txt"
if /i "%~1"=="directml" set "VENV=.venv-dml"
if /i "%~1"=="directml" set "REQ=requirements-directml.txt"

where py >nul 2>nul
if errorlevel 1 goto :nopy
py -3.12 --version
if errorlevel 1 goto :nopy

if not exist "%VENV%\Scripts\python.exe" (
    echo [1/5] Sanal ortam oluşturuluyor: %VENV%
    py -3.12 -m venv "%VENV%"
    if errorlevel 1 goto :err
)

echo [2/5] pip güncelleniyor
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :err

echo [3/5] Paketler kuruluyor: %REQ% - CUDA/cuDNN paketleri büyüktür, birkaç dakika sürebilir
"%VENV%\Scripts\python.exe" -m pip install -r "%REQ%"
if errorlevel 1 goto :err

echo [4/5] Parçalı model dosyaları birleştiriliyor
"%VENV%\Scripts\python.exe" main.py dev merge_large_files
if errorlevel 1 goto :err

if exist "_tools\ffmpeg\ffprobe.exe" goto :ffok
echo [5/5] ffmpeg/ffprobe proje içine indiriliyor: _tools\ffmpeg
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $u='https://github.com/GyanD/codexffmpeg/releases/download/9.0.2/ffmpeg-9.0.2-essentials_build.zip'; $t=Join-Path $env:TEMP ('dfl_ffmpeg_'+[guid]::NewGuid()); New-Item -ItemType Directory -Force $t | Out-Null; Invoke-WebRequest $u -OutFile (Join-Path $t 'ff.zip'); Expand-Archive (Join-Path $t 'ff.zip') $t -Force; New-Item -ItemType Directory -Force '_tools\ffmpeg' | Out-Null; Get-ChildItem $t -Recurse -Include ffmpeg.exe,ffprobe.exe | Copy-Item -Destination '_tools\ffmpeg' -Force; Get-ChildItem $t -Recurse -Filter LICENSE | Select-Object -First 1 | Copy-Item -Destination '_tools\ffmpeg' -Force; Remove-Item $t -Recurse -Force"
if errorlevel 1 goto :err
goto :check
:ffok
echo [5/5] ffmpeg zaten var: _tools\ffmpeg

:check
echo.
echo Kontrol:
"%VENV%\Scripts\python.exe" -X utf8 -c "from xlib import onnxruntime as o; import onnxruntime as r; print('onnxruntime', r.__version__); [print('  aygıt:', d) for d in o.get_available_devices_info()]"
echo.
echo Kurulum tamamlandı. Uygulamayı baslat.bat ile açın.
if /i "%~1"=="directml" echo DirectML için: baslat.bat directml
pause
exit /b 0

:nopy
echo [HATA] Python 3.12 bulunamadı. https://www.python.org/downloads/ adresinden Python 3.12 kurun, "py launcher" seçeneği açık olsun.
pause
exit /b 1

:err
echo [HATA] Kurulum yarıda kaldı. Yukarıdaki hata mesajına bakın.
pause
exit /b 1
