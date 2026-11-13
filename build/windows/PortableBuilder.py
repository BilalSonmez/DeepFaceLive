"""
Builds a portable Windows folder of DeepFaceLive with an embedded Python 3.12.

No system Python is needed to run the result: unpack and double-click baslat.bat / start.bat.
Run this script itself with a 64-bit CPython 3.12 (it is used only to run pip):

    py -3.12 build\\windows\\PortableBuilder.py --backend cuda     --release-dir D:\\dfl_build\\DeepFaceLive_NVIDIA
    py -3.12 build\\windows\\PortableBuilder.py --backend directml --release-dir D:\\dfl_build\\DeepFaceLive_DirectX12

Optional: --pack-7zr path\\to\\7zr.exe --volume-size 1900m  -> split .7z volumes next to the release dir.

Layout of the release dir:
    baslat.bat / start.bat            launchers
    cihaz_kontrol.bat / check_devices.bat
    userdata\\                         settings, dfm_models (downloaded on demand), samples, output
    _internal\\python\\                 embedded CPython + Lib\\site-packages
    _internal\\DeepFaceLive\\           project code, merged onnx models, _tools\\ffmpeg
"""
import argparse
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PYTHON_VER = '3.12.10'
URL_PYTHON = f'https://www.python.org/ftp/python/{PYTHON_VER}/python-{PYTHON_VER}-embed-amd64.zip'
URL_FFMPEG = 'https://github.com/GyanD/codexffmpeg/releases/download/9.0.2/ffmpeg-9.0.2-essentials_build.zip'

REQUIREMENTS = {'cuda': 'requirements-rtx50.txt',
                'directml': 'requirements-directml.txt'}

# tracked paths that are not needed at runtime (or are not ours to redistribute in a binary package)
EXCLUDE_PREFIXES = ('build/samples/', 'build/animatables/', '__dev_archived/', 'doc/',
                    'modelhub/torch/', '_ekran/', '.github/')

# MSVC runtime DLLs copied app-local next to python.exe (VC++ redistributable files)
MSVC_DLLS = ('msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll', 'concrt140.dll',
             'vcruntime140.dll', 'vcruntime140_1.dll', 'vcomp140.dll')


def log(*a):
    print('[build]', *a, flush=True)


def download(url: str, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / url.rsplit('/', 1)[-1]
    if out.exists() and out.stat().st_size > 0:
        log('cached', out.name)
        return out
    log('downloading', url)
    tmp = out.with_suffix(out.suffix + '.tmp')
    with urllib.request.urlopen(url) as r, open(tmp, 'wb') as f:
        shutil.copyfileobj(r, f, 1024 * 1024)
    tmp.replace(out)
    return out


def run(args, cwd=None, env=None):
    log('run:', ' '.join(str(x) for x in args))
    subprocess.run([str(x) for x in args], cwd=cwd, env=env, check=True)


def install_python(python_dir: Path, cache_dir: Path):
    zp = download(URL_PYTHON, cache_dir)
    with zipfile.ZipFile(zp) as z:
        z.extractall(python_dir)
    # ._pth: relative entries are resolved against python_dir
    pth = next(python_dir.glob('python3*._pth'))
    zipname = next(python_dir.glob('python3*.zip')).name
    pth.write_text('\n'.join([zipname, '.', r'Lib\site-packages', r'..\DeepFaceLive', 'import site', '']),
                   encoding='utf-8')
    (python_dir / 'Lib' / 'site-packages').mkdir(parents=True, exist_ok=True)
    sysdir = Path(r'C:\Windows\System32')
    for name in MSVC_DLLS:
        src = sysdir / name
        if src.exists() and not (python_dir / name).exists():
            shutil.copy2(src, python_dir / name)


def install_packages(python_dir: Path, req_file: Path, cache_dir: Path):
    site = python_dir / 'Lib' / 'site-packages'
    run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-warn-script-location',
         '--only-binary=:all:', '--platform', 'win_amd64', '--python-version', '3.12',
         '--implementation', 'cp', '--target', site, '-r', req_file])
    # console-script launchers in bin\ point at the build machine's python; drop them
    shutil.rmtree(site / 'bin', ignore_errors=True)
    for p in site.rglob('__pycache__'):
        shutil.rmtree(p, ignore_errors=True)


def copy_project(dst: Path):
    files = subprocess.run(['git', '-C', str(REPO_ROOT), 'ls-files', '-z'], check=True,
                           capture_output=True).stdout.decode('utf-8').split('\0')
    n = 0
    for rel in files:
        if not rel or rel.startswith(EXCLUDE_PREFIXES):
            continue
        src = REPO_ROOT / rel
        if not src.is_file():
            continue
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        n += 1
    log(f'copied {n} tracked files')


def install_ffmpeg(dst: Path, cache_dir: Path):
    zp = download(URL_FFMPEG, cache_dir)
    dst.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zp) as z:
        for e in z.infolist():
            name = Path(e.filename).name
            if name in ('ffmpeg.exe', 'ffprobe.exe') or (name == 'LICENSE' and not (dst / 'LICENSE').exists()):
                (dst / name).write_bytes(z.read(e))


LAUNCHER = r"""@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONNOUSERSITE=1"
set "PATH=%~dp0_internal\python;%~dp0_internal\DeepFaceLive\_tools\ffmpeg;%PATH%"
echo DeepFaceLive ({backend_title}) - this console shows the application log, do not close it.
echo Bu pencere uygulama gunluklerini gosterir, kapatmayin.
"%~dp0_internal\python\python.exe" "%~dp0_internal\DeepFaceLive\main.py" run DeepFaceLive --userdata-dir "%~dp0userdata"{extra}
if errorlevel 1 (
    echo.
    echo [ERROR/HATA] The application exited with an error, see the messages above.
    pause
)
"""

DEVICE_CHECK = r"""@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONHOME="
set "PYTHONPATH="
set "PATH=%~dp0_internal\python;%PATH%"
"%~dp0_internal\python\python.exe" -X utf8 -c "import sys, platform; print('Python', sys.version.split()[0], platform.machine()); import onnxruntime as r; print('onnxruntime', r.__version__, r.get_available_providers()); {nocuda}from xlib import onnxruntime as o; [print('  device:', d) for d in o.get_available_devices_info()]"
pause
"""


def write_launchers(release: Path, backend: str):
    extra = ' --no-cuda' if backend == 'directml' else ''
    title = 'NVIDIA CUDA' if backend == 'cuda' else 'DirectX 12 / DirectML'
    text = LAUNCHER.replace('{backend_title}', title).replace('{extra}', extra)
    for name in ('baslat.bat', 'start.bat'):
        (release / name).write_text(text.replace('\n', '\r\n'), encoding='utf-8')
    dc = DEVICE_CHECK.replace('{nocuda}', "from xlib import appargs; appargs.set_arg_bool('NO_CUDA', True); " if backend == 'directml' else '')
    for name in ('cihaz_kontrol.bat', 'check_devices.bat'):
        (release / name).write_text(dc.replace('\n', '\r\n'), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=['cuda', 'directml'], default='cuda')
    ap.add_argument('--release-dir', required=True, type=Path)
    ap.add_argument('--cache-dir', type=Path, default=None)
    ap.add_argument('--sample', type=Path, action='append', default=[],
                    help='file copied into userdata/samples (use only public-domain / synthetic media)')
    ap.add_argument('--pack-7zr', type=Path, default=None, help='path to 7zr.exe / 7z.exe to create split .7z volumes')
    ap.add_argument('--volume-size', default='1900m')
    args = ap.parse_args()

    if sys.version_info[:2] != (3, 12) or platform_bits() != 64:
        raise SystemExit('Run this builder with 64-bit CPython 3.12')

    release = args.release_dir.resolve()
    cache = (args.cache_dir or release.parent / '_cache').resolve()
    if release.exists():
        log('removing', release)
        shutil.rmtree(release)
    internal = release / '_internal'
    python_dir = internal / 'python'
    code_dir = internal / 'DeepFaceLive'

    install_python(python_dir, cache)
    install_packages(python_dir, REPO_ROOT / REQUIREMENTS[args.backend], cache)
    copy_project(code_dir)
    install_ffmpeg(code_dir / '_tools' / 'ffmpeg', cache)

    log('merging split model files')
    run([python_dir / 'python.exe', 'main.py', 'dev', 'merge_large_files', '--delete-parts'], cwd=code_dir)
    for p in code_dir.rglob('__pycache__'):
        shutil.rmtree(p, ignore_errors=True)

    for sub in ('dfm_models', 'animatables', 'output_sequence', 'samples', 'settings'):
        (release / 'userdata' / sub).mkdir(parents=True, exist_ok=True)
    for s in args.sample:
        shutil.copy2(s, release / 'userdata' / 'samples' / s.name)

    write_launchers(release, args.backend)
    for name in ('LICENSE', 'README.md', 'KURULUM.md'):
        if (REPO_ROOT / name).exists():
            shutil.copy2(REPO_ROOT / name, release / name)

    size = sum(f.stat().st_size for f in release.rglob('*') if f.is_file())
    log(f'release folder ready: {release} ({size / 2**30:.2f} GiB)')

    if args.pack_7zr:
        archive = release.parent / f'{release.name}.7z'
        for old in release.parent.glob(f'{release.name}.7z*'):
            old.unlink()
        run([args.pack_7zr, 'a', '-t7z', '-m0=LZMA2', '-mx=7', '-mmt=on', f'-v{args.volume_size}',
             archive, release], cwd=release.parent)
        for v in sorted(release.parent.glob(f'{release.name}.7z*')):
            log(f'  {v.name}  {v.stat().st_size / 2**20:.0f} MiB')


def platform_bits():
    import struct
    return struct.calcsize('P') * 8


if __name__ == '__main__':
    main()
