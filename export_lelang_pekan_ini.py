import sqlite3
import json
import datetime
from pathlib import Path

# Lokasi database dan output
DB_PATH = Path("D:/WongsoApps/LotScrapperSJB/lelang.db")
OUTPUT_JSON = Path("D:/WongsoApps/lelang-sjb/data/lelang_segera.json")

# Hitung Senin dan Jumat minggu depan
today = datetime.date.today()
weekday = today.weekday()  # Monday = 0
monday_next_week = today + datetime.timedelta(days=(7 - weekday))
friday_next_week = monday_next_week + datetime.timedelta(days=4)

start_date_str = monday_next_week.strftime("%Y-%m-%d")
end_date_str = friday_next_week.strftime("%Y-%m-%d")

# Ambil data dari database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

query = """
SELECT namaPemohon, kodeLot, namaLotLelang, nilaiLimit, tglSelesaiLelang, namaUnitKerja
FROM lot_lelang
WHERE DATE(tglSelesaiLelang) BETWEEN ? AND ?
ORDER BY DATE(tglSelesaiLelang) ASC
"""
cur.execute(query, (start_date_str, end_date_str))
rows = cur.fetchall()

# Konversi ke JSON
output = []
for row in rows:
    output.append({
        "pemohon": row["namaPemohon"],
        "kode_lot": row["kodeLot"],
        "nama_lot": row["namaLotLelang"],
        "nilai_limit": row["nilaiLimit"],
        "tanggal_lelang": row["tglSelesaiLelang"],
        "kpknl": row["namaUnitKerja"]
    })

# Simpan hasil
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"[OK] Export {len(output)} data lelang ke {OUTPUT_JSON}")
print(f"[INFO] Periode: {start_date_str} s.d. {end_date_str}")
