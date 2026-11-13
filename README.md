# DeepFaceLive: community fork for RTX 50 and current Python

> **This is an unofficial community fork of [iperov/DeepFaceLive](https://github.com/iperov/DeepFaceLive)**, which has been archived by its author.
> All credit for DeepFaceLive goes to **iperov and the original contributors**. This fork only updates dependencies and fixes compatibility so the app runs on current hardware and software.
> The original README follows further below, unchanged.

**[English](#english)** | **[Türkçe](#türkçe)**

---

## English

### What changed

The original project was pinned to Python 3.8, onnxruntime-gpu 1.15 (CUDA 11.8 + cuDNN 8), numpy 1.21 and PyQt6 6.5. Those builds do not support RTX 50 series (Blackwell, sm_120) GPUs and have no Python 3.12 packages. This fork runs on:

| Component | Original | This fork |
|---|---|---|
| Python | 3.8 | **3.12.10** |
| onnxruntime-gpu | 1.15.1 (CUDA 11.8, cuDNN 8) | **1.31.1** (CUDA 13, cuDNN 9, from pip) |
| onnxruntime-directml (fallback) | 1.15.1 | **1.24.4** |
| numpy | 1.21.6 | **2.5.4** |
| OpenCV (contrib) | 4.8.0 | **5.0.0** |
| PyQt6 | 6.5.1 | **6.12.0** |
| ffmpeg | 4.4 | **9.0.2** |

Code changes are small compatibility fixes (Python 3.10+ `collections.abc`, removed numpy aliases, PyQt6 int arguments, OpenCV 5 API, CUDA DLL preloading from pip packages, duplicate DirectML adapters). See [KURULUM.md](KURULUM.md) (Turkish), section 10, for the full list.

### Supported GPUs

- **NVIDIA RTX 50 series (Blackwell)**: tested on an RTX 5070, about 30 FPS at 1280x720 in the full app.
- **NVIDIA RTX 30 / 40 series** and other NVIDIA GPUs supported by CUDA 13. Needs an NVIDIA driver with **CUDA 13 support (580 or newer)**. Check with `nvidia-smi`: `CUDA Version` must be 13.0 or higher.
- **Any DirectX 12 GPU (AMD, Intel, older NVIDIA)**: DirectML fallback package, or `kurulum.bat directml` from source.
- You do **not** need to install the CUDA Toolkit or cuDNN: the CUDA 13 / cuDNN 9 runtime comes as pip packages.

### Install

**Option A: portable package (no Python needed)**

1. Download all parts (`DeepFaceLive_NVIDIA.7z.001`, `.002`, ...) from the [latest release](https://github.com/BilalSonmez/DeepFaceLive/releases/latest) into one folder, or the smaller DirectX 12 package.
2. Install [7-Zip](https://www.7-zip.org/) (or NanaZip), right-click `DeepFaceLive_NVIDIA.7z.001` and choose **Extract here**. The other parts are read automatically.
3. Open the extracted folder and double-click **`start.bat`** (or `baslat.bat`). `check_devices.bat` lists the GPUs the app can see.

**Option B: from source**

1. Install [Python 3.12 (64-bit)](https://www.python.org/downloads/) with the "py launcher" option.
2. Clone this repository and double-click **`kurulum.bat`**. It creates `.venv`, installs `requirements-rtx50.txt`, merges the split model files and downloads ffmpeg. For DirectML: `kurulum.bat directml`.
3. Start with **`baslat.bat`** (DirectML: `baslat.bat directml`).

### Quick start

1. Turn on **File source** (video file) or **Camera source**. The portable package includes a public-domain sample: `userdata\samples\mona_lisa_pan.mp4`.
2. **Face detector**: YoloV5, device `[CUDA]`. **Face marker**: Google FaceMesh. **Face aligner**: defaults.
3. **Face swap (DFM)**: pick a model. It is downloaded automatically from the upstream releases into `userdata\dfm_models` (300-700 MB each).
4. **Face merger**: set the device to your GPU (OpenCL) for the best speed.
5. **Stream output**: Source = `Merged frame`, press **window**. Use OBS (Window Capture + Virtual Camera) to send it to video-call apps.

### Responsible use

Use DeepFaceLive **only with the faces of people who have given their consent, and only for lawful purposes**. Do **not** use it to impersonate anyone, to deceive or defraud people, to bypass identity verification, or to create non-consensual or misleading content. Laws on deepfakes, personality rights and fraud apply to you, and you are responsible for what you create with this software.

### License and attribution

DeepFaceLive is © iperov and contributors, licensed under **GPL-3.0** (see [LICENSE](LICENSE)). The original copyright notices are kept, and the changes in this fork are released under the same license. Upstream: <https://github.com/iperov/DeepFaceLive>. The portable packages bundle ffmpeg (GPL, <https://ffmpeg.org>, builds by [GyanD/codexffmpeg](https://github.com/GyanD/codexffmpeg)) and the Python, onnxruntime, NVIDIA CUDA/cuDNN, OpenCV and Qt runtimes under their own licenses.

---

## Türkçe

### Neler değişti

Bu depo, yazarı tarafından arşivlenmiş [iperov/DeepFaceLive](https://github.com/iperov/DeepFaceLive) projesinin **resmî olmayan topluluk fork'udur**. Emeğin tamamı **iperov'a ve orijinal katkıcılara** aittir. Bu fork yalnızca bağımlılıkları güncelliyor ve uygulamanın güncel donanım ve yazılımda çalışması için uyumluluk düzeltmeleri yapıyor.

Orijinal proje Python 3.8, onnxruntime-gpu 1.15 (CUDA 11.8 + cuDNN 8), numpy 1.21 ve PyQt6 6.5 sürümlerine sabitliydi. Bu sürümler RTX 50 serisi (Blackwell, sm_120) kartları desteklemiyor. Güncel sürümler yukarıdaki tabloda. Ayrıntılı Türkçe kurulum ve sorun giderme rehberi: **[KURULUM.md](KURULUM.md)**.

### Desteklenen GPU'lar

- **NVIDIA RTX 50 serisi (Blackwell)**: RTX 5070'te test edildi. Uygulamanın tamamında 1280x720'de yaklaşık 30 FPS.
- **NVIDIA RTX 30 / 40 serisi** ve CUDA 13'ün desteklediği diğer NVIDIA kartlar. **CUDA 13'ü destekleyen sürücü (580 veya üstü)** gerekir. `nvidia-smi` çıktısındaki `CUDA Version` 13.0 veya üstü olmalı.
- **DirectX 12 destekli her GPU (AMD, Intel, eski NVIDIA)**: DirectML yedek paketi ya da kaynaktan `kurulum.bat directml`.
- CUDA Toolkit ya da cuDNN kurmanız **gerekmez**. CUDA 13 / cuDNN 9 çalışma zamanı pip paketleriyle gelir.

### Kurulum

**Seçenek A: taşınabilir paket (Python gerekmez)**

1. [Son sürüm](https://github.com/BilalSonmez/DeepFaceLive/releases/latest) sayfasından bütün parçaları (`DeepFaceLive_NVIDIA.7z.001`, `.002`, ...) aynı klasöre indirin. İsterseniz daha küçük DirectX 12 paketini de kullanabilirsiniz.
2. [7-Zip](https://www.7-zip.org/) (ya da NanaZip) kurun, `DeepFaceLive_NVIDIA.7z.001` dosyasına sağ tıklayıp **Buraya çıkart** deyin. Diğer parçalar kendiliğinden okunur.
3. Çıkan klasörde **`baslat.bat`** dosyasına çift tıklayın. `cihaz_kontrol.bat` uygulamanın gördüğü GPU'ları listeler.

**Seçenek B: kaynaktan kurulum**

1. [Python 3.12 (64 bit)](https://www.python.org/downloads/) kurun, "py launcher" seçeneği açık olsun.
2. Depoyu indirip **`kurulum.bat`** dosyasına çift tıklayın. Betik `.venv` oluşturur, `requirements-rtx50.txt` paketlerini kurar, parçalı model dosyalarını birleştirir ve ffmpeg'i indirir. DirectML için: `kurulum.bat directml`.
3. **`baslat.bat`** ile başlatın (DirectML: `baslat.bat directml`).

### Hızlı başlangıç

1. **File source** (video dosyası) ya da **Camera source** modülünü açın. Taşınabilir pakette kamu malı bir örnek video var: `userdata\samples\mona_lisa_pan.mp4`.
2. **Face detector**: YoloV5, aygıt `[CUDA]`. **Face marker**: Google FaceMesh. **Face aligner**: varsayılan ayarlar.
3. **Face swap (DFM)**: bir model seçin. Model upstream sürümlerinden `userdata\dfm_models` klasörüne kendiliğinden iner (her biri 300-700 MB).
4. **Face merger**: en iyi hız için aygıtı GPU (OpenCL) yapın.
5. **Stream output**: Source = `Merged frame` seçip **window** düğmesine basın. Görüntüyü görüntülü arama uygulamalarına OBS ile (Pencere Yakalama + Sanal Kamera) verebilirsiniz.

### Sorumlu kullanım

DeepFaceLive'ı **yalnızca izin vermiş kişilerin yüzleriyle ve yalnızca yasal amaçlarla** kullanın. Başkasını taklit etmek, insanları kandırmak ya da dolandırmak, kimlik doğrulamayı atlatmak veya rızası olmayan ya da yanıltıcı içerik üretmek için **kullanmayın**. Deepfake, kişilik hakları ve dolandırıcılıkla ilgili yasalar sizin için de geçerlidir. Bu yazılımla ürettiğiniz içerikten siz sorumlusunuz.

### Lisans ve atıf

DeepFaceLive © iperov ve katkıda bulunanlar, **GPL-3.0** lisanslıdır ([LICENSE](LICENSE)). Orijinal telif bildirimleri korunmuştur. Bu fork'taki değişiklikler de aynı lisansla yayımlanır. Upstream: <https://github.com/iperov/DeepFaceLive>. Taşınabilir paketler ffmpeg (GPL, <https://ffmpeg.org>, [GyanD/codexffmpeg](https://github.com/GyanD/codexffmpeg) derlemesi) ile Python, onnxruntime, NVIDIA CUDA/cuDNN, OpenCV ve Qt çalışma zamanlarını kendi lisanslarıyla içerir.

---

<p align="center"><b>Original README (iperov/DeepFaceLive)</b></p>

<table align="center" border="0">

<tr><td colspan=2 align="center">

![](doc/deepfacelive_intro.png)

![](doc/logo_onnx.png)![](doc/logo_directx.png)![](doc/logo_python.png)

</td></tr>
</table>
<table align="center" border="0">

<tr><td colspan=2 align="center">

## Face Swap (DFM)

You can swap your face from a webcam or the face in the video using trained face models.

Here is a list of available ready-to-use public face models.

These persons do not exists. Similarities with real people are accidental. Except Keanu Reeves. He exists, and he's breathtaking!
</td></tr>

<tr><td colspan=2 align="center">

<table align="center" border="0">
<tr><td align="center">
Keanu Reeves

<img src="doc/celebs/Keanu_Reeves/Keanu_Reeves.png" width=128></img>

<a href="doc/celebs/Keanu_Reeves/examples.md">examples</a>
</td><td align="center">
Irina Arty

<img src="doc/celebs/Irina_Arty/Irina_Arty.png" width=128></img>

examples
</td><td align="center">
Millie Park

<img src="doc/celebs/Millie_Park/Millie_Park.png" width=128></img>

examples
</td><td align="center">
Rob Doe

<img src="doc/celebs/Rob_Doe/Rob_Doe.png" width=128></img>

<a href="doc/celebs/Rob_Doe/examples.md">examples</a>
</td><td align="center">
Jesse Stat

<img src="doc/celebs/Jesse_Stat/Jesse_Stat.png" width=128></img>

examples
</td></tr>

</table>

<table align="center" border="0">
<tr><td align="center">
Bryan Greynolds

<img src="doc/celebs/Bryan_Greynolds/Bryan_Greynolds.png" width=128></img>

<a href="doc/celebs/Bryan_Greynolds/examples.md">examples</a>
</td><td align="center">
Mr. Bean

<img src="doc/celebs/Mr_Bean/Mr_Bean.png" width=128></img>

examples
</td><td align="center">
Ewon Spice

<img src="doc/celebs/Ewon_Spice/Ewon_Spice.png" width=128></img>

<a href="doc/celebs/Ewon_Spice/examples.md">examples</a>

</td><td align="center">
Natasha Former

<img src="doc/celebs/Natasha_Former/Natasha_Former.png" width=128></img>

<a href="doc/celebs/Natasha_Former/examples.md">examples</a>

</td><td align="center">
Emily Winston

<img src="doc/celebs/Emily_Winston/Emily_Winston.png" width=128></img>

<a href="doc/celebs/Emily_Winston/examples.md">examples</a>

</td></tr></table>
<table align="center" border="0">
<tr><td align="center">
Ava de Addario

<img src="doc/celebs/Ava_de_Addario/Ava_de_Addario.png" width=128></img>

<a href="doc/celebs/Ava_de_Addario/examples.md">examples</a>
</td><td align="center">
Dilraba Dilmurat

<img src="doc/celebs/Dilraba_Dilmurat/Dilraba_Dilmurat.png" width=128></img>

examples
</td><td align="center">
Matilda Bobbie

<img src="doc/celebs/Matilda_Bobbie/Matilda_Bobbie.png" width=128></img>

<a href="doc/celebs/Matilda_Bobbie/examples.md">examples</a>
</td><td align="center">
Yohanna Coralson

<img src="doc/celebs/Yohanna_Coralson/Yohanna_Coralson.png" width=128></img>

<a href="doc/celebs/Yohanna_Coralson/examples.md">examples</a>

</td><td align="center">
Amber Song

<img src="doc/celebs/Amber_Song/Amber_Song.png" width=128></img>

examples

</td></tr></table>
<table align="center" border="0">
<tr align="center"><td align="center">
Kim Jarrey

<img src="doc/celebs/Kim_Jarrey/Kim_Jarrey.png" width=128></img>

<a href="doc/celebs/Kim_Jarrey/examples.md">examples</a>
</td><td align="center">
David Kovalniy

<img src="doc/celebs/David_Kovalniy/David_Kovalniy.png" width=128></img>

<a href="doc/celebs/David_Kovalniy/examples.md">examples</a>
</td><td align="center">
Jackie Chan

<img src="doc/celebs/Jackie_Chan/Jackie_Chan.png" width=128></img>

examples
</td><td align="center">
Nicola Badge

<img src="doc/celebs/Nicola_Badge/Nicola_Badge.png" width=128></img>

<a href="doc/celebs/Nicola_Badge/examples.md">examples</a>
</td><td align="center">
Joker

<img src="doc/celebs/Joker/Joker.png" width=128></img>

examples
</td></tr></table>
<table align="center" border="0">
<tr align="center"><td>
Dean Wiesel

<img src="doc/celebs/Dean_Wiesel/Dean_Wiesel.png" width=128></img>

<a href="doc/celebs/Dean_Wiesel/examples.md">examples</a>
</td><td align="center">
Silwan Stillwone

<img src="doc/celebs/Silwan_Stillwone/Silwan_Stillwone.png" width=128></img>

<a href="doc/celebs/Silwan_Stillwone/examples.md">examples</a>
</td><td align="center">
Tim Chrys

<img src="doc/celebs/Tim_Chrys/Tim_Chrys.png" width=128></img>

<a href="doc/celebs/Tim_Chrys/examples.md">examples</a>

</td><td align="center">
Zahar Lupin

<img src="doc/celebs/Zahar_Lupin/Zahar_Lupin.png" width=128></img>

<a href="doc/celebs/Zahar_Lupin/examples.md">examples</a>
</td><td align="center">
Tim Norland

<img src="doc/celebs/Tim_Norland/Tim_Norland.png" width=128></img>

<a href="doc/celebs/Tim_Norland/examples.md">examples</a>
</td></tr></table>


<table align="center" border="0">
<tr align="center"><td>
Natalie Fatman

<img src="doc/celebs/Natalie_Fatman/Natalie_Fatman.png" width=128></img>

<a href="doc/celebs/Natalie_Fatman/examples.md">examples</a>
</td><td align="center">
Liu Lice

<img src="doc/celebs/Liu_Lice/Liu_Lice.png" width=128></img>

<a href="doc/celebs/Liu_Lice/examples.md">examples</a>
</td><td align="center">
Albica Johns

<img src="doc/celebs/Albica_Johns/Albica_Johns.png" width=128></img>

<a href="doc/celebs/Albica_Johns/examples.md">examples</a>

</td><td align="center">
Meggie Merkel

<img src="doc/celebs/Meggie_Merkel/Meggie_Merkel.png" width=128></img>

<a href="doc/celebs/Meggie_Merkel/examples.md">examples</a>
</td><td align="center">
Tina Shift

<img src="doc/celebs/Tina_Shift/Tina_Shift.png" width=128></img>

<a href="doc/celebs/Tina_Shift/examples.md">examples</a>
</td></tr></table>

</td></tr>

<tr><td colspan=2 align="center">
If you want a higher quality or better face match, you can train your own face model using <a href="https://github.com/iperov/DeepFaceLab">DeepFaceLab</a>

Here is an <a href="https://www.tiktok.com/@arnoldschwarzneggar/video/6995538782204300545">example</a> of Arnold Schwarzneggar trained on a particular face and used in a video call. Read the FAQ for more information.

</td></tr>

</table>
<table align="center" border="0">

<tr><td colspan=2 align="center">

## Face Swap (Insight)

You can swap your face from a webcam or the face in the video using your own single photo.

<img src="doc/lukashenko.png" width=128></img>

<img src="doc/insight_faceswap_example.gif"></img>

</td></tr>

</table>
<table align="center" border="0">

<tr><td colspan=2 align="center">

## Face Animator

There is also a Face Animator module in DeepFaceLive app. You can control a static face picture using video or your own face from the camera. The quality is not the best, and requires fine face matching and tuning parameters for every face pair, but enough for funny videos and memes or real-time streaming at 25 fps using 35 TFLOPS GPU.

<img src="doc/face_animator_example.gif"></img>

[![Stranger Things theme intro acapella](doc/Ng1C78Ceyxg_screenshot.png)](https://www.youtube.com/watch?v=Ng1C78Ceyxg)

Here is a [mini video](doc/FaceAnimator_tutor.webm?raw=true) showing the process of setting up the Face Animator for Obama controlling Kim Chen's face.

</td></tr>

</table>

<table align="center" border="0">

<tr><td colspan=2 align="center">

## System requirements

any DirectX12 compatible graphics card

(Recommended RTX 2070+ / Radeon RX 5700 XT+ )

Modern CPU with AVX instructions

4GB RAM, 32GB+ paging file

Windows 10

</td></tr>
<tr><td colspan=2 align="center">

## Documentation

</td></tr>
<tr><td align="right">
Windows
</td><td align="left">

<a href="doc/windows/main_setup.md">Main setup</a>

- <a href="doc/windows/for_streaming.md">additional setup for streaming</a>

- <a href="doc/windows/for_video_calls.md">additional setup for video calls</a>       

<a href="doc/windows/using_android_phone_camera.md">Using Android phone camera</a>  

</td></tr>
<tr><td align="right">
Linux
</td><td align="left">
<a href="build/linux">Build info</a>
</td></tr>
<tr><td align="right">
Frequently asked questions
</td><td align="left">
<a href="doc/user_faq/user_faq.md">for User</a>

<a href="doc/developer_faq/developer_faq.md">for Developer</a>
</td></tr>
<tr><td colspan=2 align="center">

## Releases

</td></tr>
<tr><td align="right">

<a href="https://disk.yandex.ru/d/7i5XTKIKVg5UUg">Windows 10 x64 (yandex.ru)</a>

<a href="https://mega.nz/folder/m10iELBK#Y0H6BflF9C4k_clYofC7yA">Windows 10 x64 (mega.nz)</a>


</td><td align="left">
Contains stand-alone zero-dependency all-in-one ready-to-use portable self-extracting folder! You don't need to install anything other than video drivers.
<br><br>
DirectX12 build : NVIDIA, AMD, Intel videocards.
<br><br>
NVIDIA build : NVIDIA cards only, GT730 and higher. Works faster than DX12. FaceMerger can work also on AMD/Intel.
</td></tr>
<tr><td colspan=2 align="center">

## Communication groups

<tr><td align="right">
<a href="https://discord.gg/rxa7h9M6rH">Discord</a>
</td><td align="left">Official discord channel. English / Russian.</td></tr>

<tr><td align="right">
QQ群124500433
</td><td align="left">中文交流QQ群，商务合作找群主</td></tr>

</td></tr>
<tr><td colspan=2 align="center">

## How can I help the project?

</td></tr>
<tr><td colspan=2 align="center">
Train your own face model by following the recommendations in the FAQ section and share it on Discord. If the model fits the quality, it will be added to the public library.
</td></tr>
<tr><td colspan=2 align="center">
Register github account and push "Star" button.
</td></tr>
<!--<tr><td colspan=2 align="center">
<a href="https://www.paypal.com/paypalme/DeepFaceLab">Donate via Paypal</a>
</td></tr>-->
<tr><td colspan=2 align="center">
<a href="https://yoomoney.ru/to/41001142318065">Donate via Yoomoney</a>
</td></tr>
<tr><td colspan=2 align="center">
bitcoin:bc1qewl062v70rszulml3f0mjdjrys8uxdydw3v6rq
</td></tr>
<tr><td colspan=2 align="center">


<!--
    <a href="https://br-stone.online"><img src="doc/logo_barclay_stone.png"></img></a><a href="https://exmo.com"><img src="doc/logo_exmo.png"></img></a>

    presents

    <tr><td align="right">


    <a href="">Windows (magnet link)</a>
    </td><td align="center">Latest release. Use torrent client to download.</td></tr>
    </tr>
-->

</table>



