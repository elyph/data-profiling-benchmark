# NSL-KDD Benchmark: YData Profiling vs DataXID Profiling

## Amaç
NSL-KDD veri seti üzerinde YData Profiling ve DataXID Profiling araçlarının performansı ve sentetik veri karşılaştırması ölçülmüştür.

## Veri Seti
- Dataset: NSL-KDD
- Kullanılan örneklem: 14000
- Kolon sayısı: 43

## Sonuçlar

| Araç              | Süre    | Peak RAM  | Not                 |
|-------------------|---------|-----------|---------------------|
| YData Profiling   | 137.67s | 369.32 MB | Baseline profilleme |
| DataXID Profiling | 12.30s  | 46.68 MB  | Baseline profilleme |

## Çıktılar
- `benchmark_outputs/nsl_kdd/ydata_orijinal.html`
- `benchmark_outputs/nsl_kdd/dataxid_orijinal.html`
- `benchmark_outputs/nsl_kdd/dataxid_sentetik.html`
- `benchmark_outputs/nsl_kdd/ydata_kiyaslama.html`
- `benchmark_outputs/nsl_kdd/dataxid_karsilastirma.md`