# Telco Dataset Benchmark: YData Profiling vs DataXID Profiling

## Amaç
Bu çalışmada Telco veri seti üzerinde YData Profiling ve DataXID Profiling araçlarının performansı ve kullanım kolaylığı karşılaştırılmıştır. Ayrıca DataXID SDK ile sentetik veri üretilmiş ve gerçek-sentetik karşılaştırması yapılmıştır.

## Veri Seti
- Dataset: Telco Churn
- Satır sayısı: 7043
- Kolon sayısı: 21
- Temizleme: `TotalCharges` sayısala çevrildi (Sayısal analiz yapılabilmesi ve profiling araçlarında tip uyuşmazlığı oluşmaması için)

## Yöntem
1. Gerçek veri YData Profiling ile profillendi.
2. Gerçek veri DataXID Profiling ile profillendi.
3. DataXID SDK ile sentetik veri üretildi.
4. YData compare ile gerçek ve sentetik veri karşılaştırıldı.
5. DataXID tarafında gerçek ve sentetik raporlar ayrı ayrı çıkarılıp manuel kıyaslandı.

## Sonuçlar

| Araç              | Süre   | Peak RAM | Not                                              |
|-------------------|--------|----------|--------------------------------------------------|
| YData Profiling   | 11.33s | 35.94 MB | Compare için daha hazır ve okunaklı çıktı üretti |
| DataXID Profiling | 2.40s  | 7.14 MB  | Daha hızlı ve daha hafif çalıştı                 |
| DataXID SDK       | -      | -        | Sentetik veri üretimi için kullanıldı            |

## Gözlemler
- DataXID Profiling baseline profillemede daha hızlı ve daha az bellek tüketiyor.
- YData, gerçek-sentetik karşılaştırma tarafında daha kullanıcı dostu bir compare deneyimi sunuyor.
- Sentetik veri genel yapıyı koruyor, ancak bazı sayısal kolonlarda dağılım genişlemesi gözleniyor.
- Özellikle `MonthlyCharges` ve `TotalCharges` kolonlarında küçük kaymalar var.

## Yorum
DataXID, performans açısından güçlü bir profil çıkarma aracı olarak öne çıktı. YData ise karşılaştırma ve raporlama deneyiminde daha olgun bir kullanım sunuyor. Bu nedenle iki araç farklı amaçlar için avantajlı görünüyor: biri hızlı analiz, diğeri daha hazır compare deneyimi.

## Sonuç
Telco verisi üzerinde yapılan testlerde DataXID Profiling, hız ve bellek kullanımında daha iyi sonuç verdi. YData ise sentetik veri karşılaştırmasında daha açıklayıcı bir rapor üretme avantajına sahip oldu.

## Çıktılar
- `benchmark_outputs/ydata_orijinal.html`
- `benchmark_outputs/dataxid_orijinal.html`
- `benchmark_outputs/dataxid_sentetik.html`
- `benchmark_outputs/ydata_kiyaslama.html`
- `benchmark_outputs/dataxid_karsilastirma.md`