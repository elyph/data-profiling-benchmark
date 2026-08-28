# Benchmark Metodolojisi

> Bu doküman DataXID Profiling Benchmark projesinde kullanılan ölçüm yöntemlerini, test ortamını ve bilinen sınırlamaları açıklar.
> Son güncelleme: 12 Ağustos 2026

---

## 1. Ölçüm Altyapısı

### Süre Ölçümü

`time.perf_counter()` kullanılır. Bu fonksiyon, sistemin en yüksek çözünürlüklü zamanlayıcısıdır ve duvar saati bazlıdır.

Ölçümün başlangıcı: `ProfileReport` objesi oluşturulmadan hemen önce.
Ölçümün bitişi: Profiler'ın tüm analizi tamamlayıp sonucu döndürmesinden sonra (`.to_dict()` / `.get_description()` çağrısından sonra).

**Kapsam dışı bırakılanlar:**
- Veri üretim (data generation) süresi — `perf_counter`'dan önce yapılır
- HTML/JSON rapor yazma süresi — benchmark sırasında dosyaya yazılmaz
- Garbage collection süresi — her benchmark öncesinde `gc.collect()` çağrılır

### RAM Ölçümü

`psutil.Process(os.getpid()).memory_info().rss` ile **RSS (Resident Set Size)** ölçülür. Bu, işletim sisteminin Python process'ine tahsis ettiği fiziksel RAM miktarıdır (MB cinsinden).

Ölçüm yöntemi: **Delta yöntemi**
1. Profiler çalıştırılmadan hemen önce RSS ölçülür (`mem_before`)
2. Profiler tamamlandıktan sonra RSS tekrar ölçülür (`mem_after`)
3. Ekstra RAM = `max(0, mem_after - mem_before)`

Bu yöntem, profiler'ın oluşturduğu ek yükü (heap allocation, cache, temporary objects) izole eder. Base process RAM'i (Python interpreter, yüklenmiş kütüphaneler) ölçüm dışıdır.

### İstatistiksel Yöntem (n-run)

Her benchmark `n_runs` kez tekrarlanır (varsayılan: 5).

- **Ortalama:** Aritmetik ortalama (`numpy.mean`)
- **Standart sapma:** Örneklem standart sapması (`numpy.std(ddof=1)`)
- **Hata çubukları (error bars):** Grafiklerde ±1 standart sapma olarak gösterilir

Her run arasında `gc.collect()` çağrılarak GC etkisi minimize edilir.

---

## 2. Mod Tanımları

### "Complete" Mode

Tüm analizler dahil:
- **Genel bakış:** Tip çıkarımı, eksik değer, unique değer, min/max/mean/std
- **Korelasyon matrisi:** Pearson, Spearman, Kendall, Phi-K
- **Etkileşimler (interactions):** Sütun çiftleri arası scatter plot ve box plot
- **Karakter analizi:** Text/categorical sütunlarda karakter dağılımı
- **Duplicate analizi:** Tekrar eden satır tespiti
- **Alert'ler:** High correlation, missing values, constant columns vb.

DataXID: `mode="complete"` | Pandas/YData: `minimal=False` | Zarque: `minimal=False`

### "Overview" (Light) Mode

Sadece genel bakış istatistikleri:
- Tip çıkarımı, eksik değer, unique değer, min/max/mean/std
- Histogramlar
- Temel alert'ler

**Dahil edilmeyenler:** Korelasyon matrisi, etkileşim grafikleri, karakter analizi, duplicate örnekleri.

DataXID: `mode="overview"` | Pandas/YData: `minimal=True` | Zarque: `minimal=True`

---

## 3. Test Ortamı

| Parametre | Değer |
|-----------|-------|
| İşletim Sistemi | Windows (x64) |
| RAM | 15.6 GB |
| Python | ≥ 3.10 |
| DataXID | Git submodule (`dataxid-profiling/`) |
| Zarque | PyPI (`zarque-profiling`) |
| Pandas/YData | PyPI (`ydata-profiling`) |
| Polars | ≥ 1.0 |
| NumPy | ≥ 1.21 |

---

## 4. Sentetik Veri Üretimi

Tüm benchmark'larda kullanılan sentetik veri:

- **10 kolon:** 5 sayısal (float32, `standard_normal` dağılım) + 3 kategorik (A/B/C/D, uniform) + 2 boolean (True/False, uniform)
- **Seed:** `42` (NumPy — tekrarlanabilirlik için)
- **Backend'ler:**
  - Polars: `np.random.default_rng(seed)` → `pl.DataFrame(dict)`
  - Pandas: `np.random.seed(seed)` → `pd.DataFrame` (kategorikler `string[pyarrow]`)

Her iki backend aynı seed ile aynı veriyi üretir.

---

## 5. Ölçüm Akışı

```
1. Veri üretimi (süre ölçümüne DAHİL DEĞİL)
2. gc.collect() — GC temizliği
3. mem_before ölçümü
4. t0 = perf_counter()
5. ProfileReport(df, config)  
6. .to_dict() / .get_description()  
7. elapsed = perf_counter() - t0
8. mem_after ölçümü
9. delta_mem = max(0, mem_after - mem_before)
10. del report; gc.collect()
```

DataXID `to_dict()` ile, Pandas/Zarque `get_description()` ile lazy evaluation'ı zorlar. Bu, gerçek kullanım senaryosunu yansıtır — kullanıcı raporu görüntülemek istediğinde tüm analiz tamamlanmış olmalıdır.

---

## 6. Örnek Büyüklükleri

### Complete Mode
| Satır Sayısı | Etiket | Açıklama |
|-------------|--------|----------|
| 100.000 | 100K | Küçük — tüm araçlar sorunsuz |
| 500.000 | 500K | Orta — farklar belirginleşmeye başlar |
| 1.000.000 | 1M | Büyük — Pandas zorlanmaya başlar |
| 2.000.000 | 2M | Çok büyük — Pandas ~1 GB RAM kullanır |

### Minimal Mode
| Satır Sayısı | Etiket | Açıklama |
|-------------|--------|----------|
| 1M | 1M | Küçük |
| 10M | 10M | Orta |
| 25M | 25M | Büyük |
| 50M | 50M | Zarque cross-over noktası |
| 75M | 75M | Üst sınır |
| 100M | 100M | Extreme — sadece DataXID sorunsuz |

---

## 7. Bilinen Sınırlamalar

1. **JIT warm-up kontrol edilmez:** İlk run, sonraki run'lardan yavaş olabilir (özellikle Numba/JIT kullanan araçlarda). `n_runs` ortalaması bunu kısmen dengeler ama ilk run'ı ayırmaz.

2. **OS disk cache etkisi:** İkinci ve sonraki run'lar, işletim sisteminin veriyi RAM'de cache'lemesi nedeniyle daha hızlı olabilir. `gc.collect()` sadece Python seviyesinde temizlik yapar, OS cache'i etkilemez.

3. **Single-process ölçüm:** `psutil.Process().memory_info().rss` sadece ana process'in RAM'ini ölçer. Zarque gibi multiprocessing kullanan araçlarda child process'lerin RAM'i ölçüme dahil **edilmez**. Bu, Zarque'ın gerçek RAM kullanımından daha düşük görünmesine neden olabilir.

4. **CPU kullanımı ölçülmez:** Benchmark sadece süre ve RAM ölçer. CPU çekirdek kullanımı, I/O wait gibi metrikler izlenmez.

5. **Sadece sentetik veri:** Gerçek dünya verisindeki dengesiz dağılımlar, yüksek kardinalite, nested tipler benchmark kapsamında değildir.

6. **Windows spesifik:** Linux'ta `memory_info().rss` farklı davranabilir (özellikle paylaşımlı kütüphane mapping'leri).

7. **15.6 GB RAM sınırı:** 100M satır üstü testler yapılamaz.

---

## 8. Doğrulama ve Tekrarlanabilirlik

Aynı sonuçları elde etmek için:
1. `numpy.random.seed(42)` veya `np.random.default_rng(42)` kullan
2. Aynı Python ve kütüphane sürümlerini kullan
3. Benchmark öncesi sistemi mümkün olduğunca idle duruma getir (arka plan process'leri kapat)
4. `n_runs=3` ile çalıştır, ortalamayı kullan
