
import sqlite3
import json
import datetime
from datetime import date, timedelta
from pathlib import Path
import argparse

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Jakarta")
except Exception:
    TZ = None  # fallback ke waktu lokal sistem

# --- Konfigurasi path (sesuaikan jika perlu) ---
DB_PATH = Path("D:/WongsoApps/LotScrapperSJB/lelang.db")
OUTPUT_JSON = Path("D:/WongsoApps/lelang-sjb/data/lelang_segera.json")

def get_now():
    """Waktu sekarang, timezone-aware bila tersedia."""
    if TZ:
        return datetime.datetime.now(TZ)
    return datetime.datetime.now()

def monday_this_week(today: date) -> date:
    return today - timedelta(days=today.weekday())  # Monday = 0

def friday_this_week(today: date) -> date:
    return monday_this_week(today) + timedelta(days=4)

def monday_next_week(today: date) -> date:
    return today + timedelta(days=(7 - today.weekday()))

def friday_next_week(today: date) -> date:
    return monday_next_week(today) + timedelta(days=4)

def resolve_period(mode: str = "auto", cutoff_hour: int = 12):
    """
    Menentukan periode (start_date_str, end_date_str) berdasarkan mode.
    - auto: Senin–Kamis → pekan ini; Jum’at sebelum cutoff_hour → pekan ini;
            Jum’at >= cutoff_hour atau Sabtu/Minggu → pekan depan.
    - this_week: paksa pekan ini.
    - next_week: paksa pekan depan.
    - rollingN: jendela bergulir N hari dari hari ini (mis. rolling7).
    - custom: wajib berikan --start dan --end.
    """
    now = get_now()
    today = now.date()
    weekday = today.weekday()  # Mon=0 ... Sun=6

    if mode == "auto":
        if weekday <= 3:  # Mon..Thu
            start, end = monday_this_week(today), friday_this_week(today)
        elif weekday == 4:  # Friday
            if now.hour < cutoff_hour:
                start, end = monday_this_week(today), friday_this_week(today)
            else:
                start, end = monday_next_week(today), friday_next_week(today)
        else:  # Sat(5) or Sun(6)
            start, end = monday_next_week(today), friday_next_week(today)

    elif mode == "this_week":
        start, end = monday_this_week(today), friday_this_week(today)

    elif mode == "next_week":
        start, end = monday_next_week(today), friday_next_week(today)

    elif mode.startswith("rolling"):
        # contoh: rolling7 → 7 hari
        try:
            n = int(mode.replace("rolling", ""))
        except ValueError:
            raise ValueError("Format mode rollingN tidak valid. Contoh: rolling7")
        start = today
        end = today + timedelta(days=n)

    else:
        raise ValueError("Mode tidak dikenal. Gunakan auto/this_week/next_week/rollingN/custom.")

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def main():
    parser = argparse.ArgumentParser(
        description="Export data lelang untuk pekan ini/pekan depan atau rentang lain."
    )
    parser.add_argument("--mode", default="auto",
                        choices=["auto", "this_week", "next_week", "custom"] + [f"rolling{n}" for n in range(1, 31)],
                        help=("auto (default), this_week, next_week, rollingN (mis. rolling7), atau custom"))
    parser.add_argument("--cutoff-hour", type=int, default=12,
                        help="Batas 'pagi' pada hari Jum'at, default 12 (jam 12 siang).")
    parser.add_argument("--start", help="Tanggal mulai (YYYY-MM-DD) untuk mode custom")
    parser.add_argument("--end", help="Tanggal akhir (YYYY-MM-DD) untuk mode custom")
    args = parser.parse_args()

    if args.mode == "custom":
        if not (args.start and args.end):
            raise ValueError("Untuk mode custom, --start dan --end wajib diisi (YYYY-MM-DD).")
        start_date_str, end_date_str = args.start, args.end
    else:
        start_date_str, end_date_str = resolve_period(mode=args.mode, cutoff_hour=args.cutoff_hour)

    # --- Query ke database ---
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

    # --- Konversi ke JSON ---
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

    # --- Simpan hasil ---
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[OK] Export {len(output)} data lelang ke {OUTPUT_JSON}")
    print(f"[INFO] Periode: {start_date_str} s.d. {end_date_str}")
    print(f"[INFO] Mode: {args.mode} | Cutoff Friday hour: {args.cutoff_hour}")

if __name__ == "__main__":
    main()