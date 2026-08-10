import os
from pathlib import Path
import sys
import pandas as pd
import time
import tracemalloc


ROOT = Path(__file__).resolve().parents[1]
DATAXID_PYTHON_ROOT = ROOT / "dataxid-python"
DATAXID_PROFILING_SRC = ROOT / "dataxid-profiling" / "src"
DATAXID_PYTHON_VENV_SITE_PACKAGES = DATAXID_PYTHON_ROOT / "venv" / "Lib" / "site-packages"

for candidate in (
	DATAXID_PYTHON_VENV_SITE_PACKAGES,
	DATAXID_PYTHON_ROOT,
	DATAXID_PROFILING_SRC,
):
	if candidate.exists():
		candidate_str = str(candidate)
		if candidate_str not in sys.path:
			sys.path.insert(0, candidate_str)

from ydata_profiling import ProfileReport
import dataxid
from dataxid_profiling import ProfileReport as DataxidReport


OUTPUT_DIR = ROOT / "benchmark_outputs" / "nsl_kdd"
DATASET_PATH = ROOT / "datasets" / "nsl_kdd.txt"

# API Anahtarı
dataxid.api_key = "DATAXID_API_KEY"

# NSL-KDD standart kolon isimleri
NSL_KDD_COLUMNS = [
	"duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
	"land", "wrong_fragment", "urgent", "hot", "num_failed_logins",
	"logged_in", "num_compromised", "root_shell", "su_attempted", "num_root",
	"num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
	"is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
	"srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
	"diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
	"dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
	"dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
	"dst_host_rerror_rate", "dst_host_srv_rerror_rate", "class", "difficulty",
]


# Sentetik üretim için örnek boyutu
SYNTHETIC_SAMPLE_SIZE = 50_000

# Veriyi Yükleme
print("1. NSL-KDD verisi yükleniyor...")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(DATASET_PATH, header=None, names=NSL_KDD_COLUMNS)

# "difficulty" kolonu (43. kolon) sentetik üretimde sorun çıkarabileceği için
# orijinal profillemede ayrı tutulur, sentetik üretimden hariç tutulur.
df_difficulty = df.pop("difficulty") if "difficulty" in df.columns else None

print(f"   Yüklenen veri: {df.shape[0]} satır, {df.shape[1]} kolon")

# AŞAMA 1: YData Profiling (Süre ve RAM Ölçümü)
print("2. YData Orijinal Raporu oluşturuluyor...")
tracemalloc.start()
t0 = time.time()

ydata_rapor = ProfileReport(df, title="YData Orijinal Veri (NSL-KDD)")
OUTPUT_DIR.joinpath("ydata_orijinal.html").write_text(ydata_rapor.to_html(), encoding="utf-8")

ydata_sure = time.time() - t0
_, ydata_ram = tracemalloc.get_traced_memory()
tracemalloc.stop()

# AŞAMA 2: DataXID Profiling (Süre ve RAM Ölçümü)
print("3. DataXID Orijinal Raporu oluşturuluyor...")
tracemalloc.start()
t0 = time.time()

dx_rapor = DataxidReport(df, title="DataXID Orijinal Veri (NSL-KDD)")
OUTPUT_DIR.joinpath("dataxid_orijinal.html").write_text(dx_rapor.to_html(), encoding="utf-8")

dx_sure = time.time() - t0
_, dx_ram = tracemalloc.get_traced_memory()
tracemalloc.stop()

# AŞAMA 3: Sentetik Veri Üretme
print(f"4. DataXID API ile Sentetik Veri üretiliyor ({SYNTHETIC_SAMPLE_SIZE} satır)...")
df_orneklem = df.sample(n=SYNTHETIC_SAMPLE_SIZE, random_state=42)
df_sentetik = dataxid.synthesize(data=df_orneklem, n_samples=SYNTHETIC_SAMPLE_SIZE)

dx_sentetik_rapor = DataxidReport(df_sentetik, title="DataXID Sentetik Veri (NSL-KDD)")
OUTPUT_DIR.joinpath("dataxid_sentetik.html").write_text(dx_sentetik_rapor.to_html(), encoding="utf-8")

dx_gercek = dx_rapor.to_dict()
dx_sahte = dx_sentetik_rapor.to_dict()

dataxid_karsilastirma = "\n".join([
	"# DataXID Gerçek-Sentetik Kıyas (NSL-KDD)",
	"",
	f"- Gerçek satır sayısı: {dx_gercek['overview']['n_rows']}",
	f"- Sentetik satır sayısı: {dx_sahte['overview']['n_rows']}",
	f"- Gerçek eksik hücre: {dx_gercek['overview']['missing_cells']}",
	f"- Sentetik eksik hücre: {dx_sahte['overview']['missing_cells']}",
	f"- Gerçek duplicate satır: {dx_gercek['overview']['duplicate_rows']}",
	f"- Sentetik duplicate satır: {dx_sahte['overview']['duplicate_rows']}",
	f"- Gerçek alert sayısı: {len(dx_gercek['alerts'])}",
	f"- Sentetik alert sayısı: {len(dx_sahte['alerts'])}",
	f"- Gerçek correlation seti: {len(dx_gercek['correlations'])}",
	f"- Sentetik correlation seti: {len(dx_sahte['correlations'])}",
])
OUTPUT_DIR.joinpath("dataxid_karsilastirma.md").write_text(dataxid_karsilastirma, encoding="utf-8")

# AŞAMA 4: YData ile Kıyaslama
print("5. YData Kıyaslama (Compare) raporu hazırlanıyor...")
ydata_sentetik_rapor = ProfileReport(df_sentetik, title="YData Sentetik Veri (NSL-KDD)")
ydata_kiyas = ydata_rapor.compare(ydata_sentetik_rapor)
OUTPUT_DIR.joinpath("ydata_kiyaslama.html").write_text(ydata_kiyas.to_html(), encoding="utf-8")

# SONUÇLARI YAZDIR
print("\n" + "="*40)
print("TEST TAMAMLANDI!")
print(f"YData Profiling   -> Süre: {ydata_sure:.2f}s | RAM: {ydata_ram / (1024*1024):.2f} MB")
print(f"DataXID Profiling -> Süre: {dx_sure:.2f}s | RAM: {dx_ram / (1024*1024):.2f} MB")
print("Tüm HTML raporları klasöre kaydedildi.")
print("="*40)
