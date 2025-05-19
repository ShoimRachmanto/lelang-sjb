import sqlite3
import json
import datetime
from pathlib import Path

# Lokasi database dan output
DB_PATH = Path("D:/WongsoApps/LotScrapperSJB/lelang.db")
OUTPUT_JSON = Path("D:/WongsoApps/lelang-sjb/data/lelang_segera.json")

# Hitung hari ini dan range yang ditampilkan
today = datetime.date.today()
weekday = today.weekday()  # Monday = 0, Sunday = 6

# Dapatkan tanggal Senin minggu ini
monday_this_week = today - datetime.timedelta(days=weekday)

if weekday < 4:  # Senin–Kamis
    start_date = monday_this_week
    end_date = monday_this_week + datetime.timedelta(days=4)  # s.d. Jumat
else:  # Jumat
    start_date = monday_this_week
    end_date = monday_this_week + datetime.timedelta(days=9)  # s.d. Rabu minggu depan

# Format string SQL (YYYY-MM-DD)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Ambil dari SQLite
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

# Konversi ke list of dicts
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


# Simpan ke JSON
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Export {len(output)} data lelang ke {OUTPUT_JSON}")
