import csv
import json
import os

# Clear layar
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Ambil kode cabang berdasarkan panjang digit tiap bank
def extract_kode_cabang(norek, bank):
    if bank == "mandiri":
        return norek[:5]  # Untuk Mandiri ambil 5 digit
    elif bank == "bca":
        return norek[:3]  # Untuk BCA ambil 3 digit pertama
    elif bank == "bri":
        return norek[:3]  # Untuk BRI ambil 3 digit pertama
    return norek

# Baca file CSV dan cari cabang (menggunakan startswith agar fleksibel)
def cari_cabang(file_path, kode_cabang, bank):
    hasil = []
    try:
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:  # <-- UTF-8 with BOM
            reader = csv.DictReader(csvfile)
            for row in reader:
                kode = str(row.get("Kode Cabang", "")).strip()

                if kode.startswith(kode_cabang):
                    # Ambil nama cabang dari berbagai kemungkinan nama kolom
                    nama_cabang = (
                        row.get("Nama Cabang", "").strip() or
                        row.get("Nama", "").strip() or
                        row.get("Cabang", "").strip()
                    )

                    if bank == "mandiri":
                        if "Area" in row:
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Area": row.get("Area", "").strip(),
                                "Kota": row.get("Kota", "").strip()
                            })
                        elif "Region" in row:
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Area": row.get("Region", "").strip(),
                                "Kota": row.get("KOTA / KABUPATEN", "").strip(),
                                "Kode Pos": row.get("KODE POS", "").strip(),
                                "Provinsi": row.get("PROPINSI", "").strip()
                            })
                        elif "Alamat" in row and "Kota" in row:
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Area": "",
                                "Kota": row.get("Kota", "").strip()
                            })
                    elif bank == "bca":
                        hasil.append({
                            "Kode Cabang": kode,
                            "Nama Cabang": nama_cabang,
                            "Alamat": row.get("Alamat", "").strip()
                        })
                    elif bank == "bri":
                        hasil.append({
                            "Kode Cabang": kode,
                            "Nama Cabang": nama_cabang,
                            "Alamat": row.get("Alamat", "").strip(),
                            "Provinsi": row.get("Provinsi", "").strip(),
                            "Kota": row.get("Kota/Kabupaten", "").strip()
                        })
    except FileNotFoundError:
        print(f"❌ File tidak ditemukan: {file_path}")
    return hasil

# Cari semua file terkait untuk bank tertentu
def cari_data_cabang(norek, bank):
    file_mapping = {
        "mandiri": [
            "data/mandiri_jakarta.csv",
            "data/mandiri_luar1.csv",
            "data/mandiri_luar2.csv"
        ],
        "bca": [
            "data/bca.csv"
        ],
        "bri": [
            "data/bri.csv"
        ]
    }

    hasil = []
    kode_cabang = extract_kode_cabang(norek, bank)
    for file in file_mapping.get(bank, []):
        data = cari_cabang(file, kode_cabang, bank)
        if data:
            hasil.extend(data)
    return {bank: hasil}

# Menu utama
def tampil_menu():
    while True:
        clear_screen()
        print("=" * 50)
        print("{:^50}".format("💳 GeoRek - Geo Lokasi Rekening Bank 💳"))
        print("=" * 50)
        print("\n|{:^46}|".format("MENU UTAMA"))
        print("|" + "-" * 46 + "|")
        print("| {:<3} {:<40}|".format("1.", "Cek Lokasi Rekening Bank MANDIRI"))
        print("| {:<3} {:<40}|".format("2.", "Cek Lokasi Rekening Bank BCA"))
        print("| {:<3} {:<40}|".format("3.", "Cek Lokasi Rekening Bank BRI"))
        print("| {:<3} {:<40}|".format("4.", "Keluar dari Aplikasi"))
        print("-" * 50)

        pilihan = input("Silakan pilih menu (1-4): ")

        if pilihan == "4":
            print("\n👋 Terima kasih telah menggunakan GeoRek.\n")
            break

        bank_dict = {"1": "mandiri", "2": "bca", "3": "bri"}
        bank = bank_dict.get(pilihan)

        if bank:
            geo_interface(bank)
        else:
            print("\n❌ Pilihan tidak valid. Tekan Enter untuk kembali ke menu...")
            input()

# Interface per bank
def geo_interface(bank):
    clear_screen()
    print("=" * 50)
    print("{:^50}".format(f"🌐 Geo INT - {bank.upper()}"))
    print("=" * 50)
    norek = input("Masukkan Nomor Rekening: ").strip()

    if not norek.isdigit():
        print("\n❌ Input tidak valid! Harap masukkan nomor rekening yang benar (angka saja).")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    hasil = cari_data_cabang(norek, bank)
    clear_screen()
    print("=" * 50)
    print("{:^50}".format("📍 HASIL PENCARIAN"))
    print("=" * 50)

    if not hasil[bank]:  # Jika hasil kosong
        print(f"❌ Tidak ada data yang cocok untuk kode cabang {norek[:3]} yang dimasukkan.")
    else:
        print(json.dumps(hasil, indent=2, ensure_ascii=False))
    
    input("\nTekan Enter untuk kembali ke menu...")

# Jalankan program
if __name__ == "__main__":
    tampil_menu()
