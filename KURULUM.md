# DeepFaceLive: RTX 50 serisi (Blackwell) için güncel kurulum

Bu depo, arşivlenmiş [iperov/DeepFaceLive](https://github.com/iperov/DeepFaceLive) projesinin güncel Python ve GPU kütüphaneleriyle çalışacak şekilde düzenlenmiş bir kopyasıdır. Orijinal proje GPL-3.0 lisanslıdır. Lisans (`LICENSE`) ve orijinal telif bildirimleri değiştirilmeden korunmuştur.

Orijinal proje Python 3.8, onnxruntime-gpu 1.15 (CUDA 11.8 + cuDNN 8), numpy 1.21 ve PyQt6 6.5 sürümlerine sabitlenmişti. Bu sürümler RTX 50 serisi (sm_120) kartları desteklemiyor ve Python 3.12 için paketleri de yok. Bu kopya aşağıdaki sürümlerle test edildi:

| Bileşen | Sürüm |
|---|---|
| Python | 3.12.10 |
| onnxruntime-gpu | 1.31.1 (CUDA 13 + cuDNN 9, pip ile) |
| CUDA çalışma zamanı (pip) | nvidia-cuda-runtime 13.5, cublas 13.10, cudnn-cu13 9.28 |
| onnxruntime-directml (yedek) | 1.24.4 |
| numpy | 2.5.4 |
| OpenCV (contrib) | 5.0.0 |
| PyQt6 | 6.12.0 |
| ffmpeg / ffprobe | 9.0.2 (proje içinde, `_tools\ffmpeg`) |

Test edilen makine: Windows 11, RTX 5070 12 GB, NVIDIA sürücüsü 621.14.

## 1. Gereksinimler

1. **NVIDIA sürücüsü:** CUDA 13'ü destekleyen güncel bir sürücü gerekir (580 serisi ya da üstü). Kontrol etmek için komut isteminde `nvidia-smi` yazın. Sağ üstteki `CUDA Version` değeri 13.0 veya üstü olmalı.
2. **CUDA Toolkit ve cuDNN'i sisteme kurmanıza gerek yok.** Gerekli CUDA 13 ve cuDNN 9 DLL'leri pip paketleri (`nvidia-*`) olarak sanal ortamın içine kurulur, uygulama da açılırken bunları kendisi yükler.
3. **Python 3.12 (64 bit):** <https://www.python.org/downloads/> adresinden kurun. Kurulumda "py launcher" seçeneği açık kalsın. Kontrol için: `py -3.12 --version`.
4. **Microsoft Visual C++ Redistributable (x64, güncel):** Çoğu bilgisayarda zaten kurulu. onnxruntime "MSVC runtime" hatası verirse <https://aka.ms/vs/17/release/vc_redist.x64.exe> adresinden kurun.
5. Disk alanı: sanal ortam için yaklaşık 4 GB, her DFM yüz modeli için yaklaşık 700 MB.

## 2. Kurulum (tek seferlik)

Proje klasöründe **`kurulum.bat`** dosyasına çift tıklayın. Betik şunları yapar:

1. `.venv` adında bir sanal ortam oluşturur (global Python'a dokunmaz).
2. `requirements-rtx50.txt` dosyasındaki sabit sürümleri kurar (CUDA/cuDNN paketleri büyüktür, birkaç dakika sürebilir).
3. Depoda parçalara bölünmüş model dosyalarını (`*.part0`, `*.part1` ...) birleştirir.
4. ffmpeg ve ffprobe'u `_tools\ffmpeg` klasörüne indirir. Video dosyası kaynağı ve akış çıkışı bunları kullanır.
5. Son olarak görülen aygıtları yazar. Listede `[CUDA]` etiketli GPU'nuzu görmelisiniz:

```
onnxruntime 1.31.1
  aygıt: [0] NVIDIA GeForce RTX 5070 [11.9Gb] [CUDA]
  aygıt: CPU
```

Elle kurmak isterseniz:

```bat
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-rtx50.txt
.venv\Scripts\python main.py dev merge_large_files
```

### Yedek yol: DirectX 12 (DirectML)

CUDA bir nedenle çalışmazsa (eski sürücü vb.) DirectML ile de çalıştırabilirsiniz. Ayrı bir ortam kurulur:

```bat
kurulum.bat directml
baslat.bat directml
```

Bu bilgisayarda DirectML yolu CUDA'ya yakın hızda çalıştı (ayrıntılar aşağıda).

## 3. Başlatma

**`baslat.bat`** dosyasına çift tıklayın. Açılan siyah pencere uygulamanın günlüklerini gösterir, onu kapatmayın. Kullanıcı verileri (ayarlar, modeller, çıktı) `userdata` klasöründe tutulur.

## 4. Yüz modellerinin (DFM) indirilmesi

- Uygulamada **Face swap (DFM)** modülünde **Model** listesinden bir model seçtiğinizde model, projenin GitHub sürümlerinden (`github.com/iperov/DeepFaceLive/releases`) otomatik olarak `userdata\dfm_models` klasörüne indirilir. Modeller 300-700 MB arasıdır.
- Elle indirmek için ilgili `.dfm` dosyasını aynı klasöre koyun. Uygulama klasördeki tüm `.dfm` dosyalarını listeler.
- Kendi eğittiğiniz modeli kullanmak için DeepFaceLab ile `.dfm` olarak dışa aktarıp aynı klasöre koymanız yeterli.

> Yüz değiştirmeyi yalnızca izni olan kişilerin görüntüleriyle ve yasal amaçlarla kullanın. Başkasının yüzünü izinsiz kullanmak ya da yanıltıcı içerik üretmek hukuki sorumluluk doğurur.

## 5. İlk kullanım (adım adım)

Her modülün sol üstündeki güç düğmesi o modülü açıp kapatır.

1. **File source** (video ya da resim klasörü) veya **Camera source** (kamera) modüllerinden birini açın.
2. **Face detector:** Detector = `YoloV5`, Device = `[0] NVIDIA ... [CUDA]`.
3. **Face marker:** Marker = `Google FaceMesh`, Device = CUDA.
4. **Face aligner:** varsayılan ayarlar yeterli (Face coverage 2.2, Resolution 224).
5. **Face swap (DFM):** Device = CUDA, Model = istediğiniz model.
6. **Face merger:** Device = `[0] NVIDIA GeForce RTX 5070` (OpenCL). CPU'ya göre belirgin şekilde hızlıdır.
7. **Stream output:** Source = `Merged frame`. Sonucu ayrı pencerede görmek için **window** düğmesine basın.

## 6. Kamera girişi

- **Camera source** modülünü açın. **Device index** kameranın sırası (0, 1, ...), **Driver** olarak önce `DirectShow` deneyin. Görüntü gelmezse `Microsoft Media Foundation` seçin.
- Çözünürlük ve FPS'i aynı modülden ayarlayabilirsiniz. 1280x720 çoğu durumda yeterlidir. Çözünürlük arttıkça yüz tespiti ve birleştirme yavaşlar.
- Bu bilgisayarda kamera olarak yalnızca **Iriun Webcam** sürücüleri görünüyor (telefonu webcam yapan uygulama). Görüntü gelmesi için telefonda Iriun uygulamasının açık ve bağlı olması gerekir.
- Kamerayı aynı anda yalnızca bir uygulama açabilir. DeepFaceLive kamerayı kullanırken Zoom/Discord gibi uygulamalarda gerçek kamerayı değil, aşağıdaki sanal kamerayı seçin.

## 7. Sanal kamera çıkışı (OBS Virtual Camera)

DeepFaceLive'ın kendi sanal kamera sürücüsü yoktur. Görüntü OBS Studio (bu bilgisayarda 32.2.2 kurulu) üzerinden sanal kameraya verilir. İki yol var:

**Yol A: pencere yakalama (önerilen, en düşük gecikme)**
1. DeepFaceLive'da **Stream output** > Source = `Merged frame`, ardından **window** düğmesine basın. Ayrı bir çıktı penceresi açılır.
2. OBS'de **Kaynaklar** > `+` > **Pencere Yakalama** ile bu pencereyi seçin. Yakalama yöntemi `Windows 10 (1903 ve üstü)` olsun.
3. OBS'de **Sanal Kamerayı Başlat** düğmesine basın.
4. Zoom/Teams/Discord'da kamera olarak **OBS Virtual Camera** seçin.

**Yol B: yerel ağ akışı (mpegts/UDP)**
1. **Stream output** modülünde `mpegts udp://` kutusunu işaretleyin (varsayılan `127.0.0.1:1234`).
2. OBS'de **Kaynaklar** > `+` > **Medya Kaynağı**. "Yerel dosya" işaretini kaldırın. Giriş: `udp://127.0.0.1:1234`, giriş biçimi: `mpegts`.
3. **Sanal Kamerayı Başlat**.

Yol B'de ffmpeg kodlama yaptığı için birkaç kare gecikme ve küçük bir FPS kaybı olur. Bu akış test edildi: OBS'ye giden UDP akışından 1280x720 mpeg2video kareler alındı.

## 8. Ölçülen performans (RTX 5070)

Test girişi: kamu malı (public domain) bir tablodan (Mona Lisa, Wikimedia Commons) üretilmiş 1280x720, 30 FPS'lik hareketli video. Model: `Joker.dfm` (224x224). Ölçümler sırasında bilgisayarda bir oyun da açıktı, yani GPU paylaşılıyordu.

**Uygulamanın kendisi (GUI, tüm modüller ayrı süreçlerde, paralel):**

| Ayar | Stream output ortalama FPS |
|---|---|
| Real time açık (kaynak 30 FPS ile sınırlı) | ~30 FPS |
| Real time kapalı (sınırsız) | ~29-36 FPS |
| Sınırsız + mpegts akışı açık | ~25-26 FPS |

Darboğaz modüller: Face detector (~35-47 FPS) ve Face merger (~34-49 FPS). DFM yüz değiştirme tek başına ~58-63 FPS.

**Başsız ölçüm betiği (tüm aşamalar tek süreçte, sırayla, kare başına ortalama):**

| Aşama | CUDA | CPU | DirectML |
|---|---|---|---|
| Yüz tespiti (YoloV5) | 11.5 ms | 43.0 ms | 9.8 ms |
| İşaretleme (FaceMesh) | 5.4 ms | 5.0 ms | 2.2 ms |
| Hizalama | 0.8 ms | 1.8 ms | 0.9 ms |
| **Yüz değiştirme (DFM)** | **10.8 ms** | **257 ms** | 14.4 ms |
| Birleştirme | 18.8 ms (OpenCL) | 39 ms (CPU) | 21.7 ms (OpenCL) |
| Toplam / FPS | 47 ms / **21 FPS** | 346 ms / 2.9 FPS | 49 ms / 20 FPS |

Kendi bilgisayarınızda ölçmek için:

```bat
.venv\Scripts\python scripts\pipeline_benchmark.py --dfm userdata\dfm_models\Joker.dfm --input video.mp4 --merge-gpu
```

(`--cpu` ile CPU karşılaştırması, `--out-dir klasor` ile örnek kareler ve çıktı videosu.)

## 9. Sorun giderme

| Belirti | Çözüm |
|---|---|
| Device listesinde yalnızca `CPU` var | `nvidia-smi` ile sürücüyü ve CUDA 13 desteğini kontrol edin, `kurulum.bat` dosyasını tekrar çalıştırın. Olmazsa DirectML yolunu deneyin. |
| `cublasLt64_13.dll ... is missing` | Bu kopyada DLL'ler `onnxruntime.preload_dlls()` ile otomatik yükleniyor. Hata görürseniz sanal ortamı silip (`.venv`) kurulumu tekrarlayın. |
| File source'ta `[WinError 2] The system cannot find the file specified` | ffmpeg/ffprobe bulunamadı. `_tools\ffmpeg` klasöründe `ffprobe.exe` olmalı. `kurulum.bat` bu dosyaları indirir. |
| Uygulama hiçbir hata göstermeden kapanıyor | Bu kopyada yakalanmayan Qt hataları siyah pencereye yazılır. Oradaki traceback'e bakın. |
| DirectML'de aynı GPU iki kez görünüyordu | Parsec Virtual Display Adapter yüzünden. Bu kopyada tekrar eden adaptör listeden çıkarılıyor. |
| FPS düşük | Face merger aygıtını GPU yapın, Face detector'da Window size'ı küçültün (ör. 320), kaynak çözünürlüğünü 1280x720'ye indirin, arka planda GPU kullanan oyunları kapatın. |

## 10. Bu kopyada orijinale göre yapılan değişiklikler

- `collections.Iterable` yerine `collections.abc.Iterable` (Python 3.10+), kaldırılmış `np.int`/`np.float` takma adları (numpy 1.24+).
- onnxruntime: pip ile gelen CUDA/cuDNN DLL'leri `preload_dlls()` ile yükleniyor. `CUDA_CACHE_MAXSIZE` değişken adındaki görünmez karakterler temizlendi.
- PyQt6 / Python 3.10+: Qt fonksiyonlarına float yerine int geçiliyor (`QSlider.setValue`, `QProgressBar.setValue`, `QRect`). Eski hâliyle uygulama açılır açılmaz sessizce kapanıyordu.
- `main.py`: yakalanmayan Qt slot hataları süreci öldürmek yerine loglanıyor. Proje içindeki `_tools\ffmpeg` PATH'e ekleniyor.
- OpenCV 5: `FacemarkLBF.fit` çıktı şekli değişikliği.
- DirectML: Parsec sanal ekranı yüzünden tekrar listelenen GPU ayıklanıyor.
- Yeni dosyalar: `kurulum.bat`, `baslat.bat`, `requirements-rtx50.txt`, `requirements-directml.txt`, `scripts/pipeline_benchmark.py`, bu belge.

`build/windows/WindowsBuilder.py` ve `build/linux/Dockerfile` (taşınabilir paket üretimi) güncellenmedi. Bunlar hâlâ eski sürümlere işaret ediyor.

## Lisans

DeepFaceLive © iperov ve katkıda bulunanlar, GPL-3.0 (`LICENSE`). Bu kopyadaki değişiklikler de aynı lisans altındadır. ffmpeg kendi lisansıyla (`_tools\ffmpeg\LICENSE`) dağıtılır ve depoya eklenmez.
