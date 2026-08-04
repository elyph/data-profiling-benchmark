# YData vs DataXID Profiling & Synthetic Data Benchmark

Bu proje, veri profilleme ve sentetik veri üretimi alanında sektör standartı olan `ydata-profiling` ile Polars/Rust tabanlı `dataxid-profiling` araçlarının karşılaştırılmasını içermektedir.

## Proje Amacı
İki farklı kütüphanenin hız (RAM/Süre), tip çıkarımı, veri dengesizliği tespiti ve raporlama kalitesi gibi metrikler üzerinden stres testine sokulması hedeflenmiştir. 

## Kullanılan Veri Setleri
Farklı senaryoları simüle etmek için iki zorlu veri seti seçilmiştir:
1. **Telco Customer Churn:** Kategorik ve sayısal veri tiplerinin bir arada olduğu, tip çıkarımı (type inference) testi.
2. **NSL-KDD (Ağ Saldırı Tespiti):** Devasa boyutu ve yüksek korelasyonlu yapısıyla RAM ve işlemci stres testi.

## Test Edilen Metrikler
* **Üretim Süresi (`time`):** Raporların oluşturulma hızı.
* **Bellek Tüketimi (`tracemalloc`):** İşlem sırasındaki zirve RAM (Peak Memory) kullanımı.
* **Uyarı Kalitesi (Alerts):** Veri içindeki gizli korelasyonların ve dengesizliklerin tespiti.
* **Orijinal vs Sentetik Kıyası:** Üretilen sentetik verinin orijinal veriye ne kadar sadık kaldığının manuel JSON/Dict parsing yöntemleriyle kıyaslanması.

## Klasör Yapısı
* `/benchmarks`: Testleri otomatize eden Python scriptleri.
* `/benchmark_outputs`: Araçların ürettiği etkileşimli HTML raporları ve manuel Markdown kıyaslamaları.
* `/reports`: Kıyaslama sonuçlarının nihai özet metinleri.