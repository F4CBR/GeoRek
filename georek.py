import csv
import json
import os
import urllib.parse

# Clear layar
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Fungsi untuk membuat link Google Maps berdasarkan Nama Cabang
def generate_maps_link(nama_cabang, bank):
    query = f"Bank {bank.upper()} {nama_cabang}"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

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
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Normalize semua fieldnames jadi lowercase
            reader.fieldnames = [field.lower() for field in reader.fieldnames]

            for row in reader:
                # Normalize row keys ke lowercase
                row = {key.lower(): value for key, value in row.items()}
                kode = str(row.get("kode cabang", "")).strip()

                if kode.startswith(kode_cabang):
                    nama_cabang = (
                        row.get("nama cabang", "").strip() or
                        row.get("nama", "").strip() or
                        row.get("cabang", "").strip()
                    )

                    # Menambahkan kolom Maps
                    maps_link = generate_maps_link(nama_cabang, bank)

                    if bank == "mandiri":
                        if "region" in row:
                            # Mandiri Luar Jakarta 1
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Alamat": row.get("alamat", "").strip(),
                                "Kota": row.get("kota / kabupaten", "").strip(),
                                "Kode Pos": row.get("kode pos", "").strip(),
                                "Provinsi": row.get("propinsi", "").strip(),
                                "Maps": maps_link
                            })
                        elif "alamat" in row and "kota" in row:
                            # Mandiri Luar Jakarta 2
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Alamat": row.get("alamat", "").strip(),
                                "Kota": row.get("kota", "").strip(),
                                "Maps": maps_link
                            })
                        elif "area" in row:
                            # Mandiri Jakarta (bukan luar)
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Kota": row.get("kota", "").strip(),
                                "Maps": maps_link
                            })

                    elif bank == "bca":
                        hasil.append({
                            "Kode Cabang": kode,
                            "Nama Cabang": nama_cabang,
                            "Alamat": row.get("alamat", "").strip(),
                            "Maps": maps_link
                        })
                    elif bank == "bri":
                        hasil.append({
                            "Kode Cabang": kode,
                            "Nama Cabang": nama_cabang,
                            "Alamat": row.get("alamat", "").strip(),
                            "Provinsi": row.get("provinsi", "").strip(),
                            "Kota": row.get("kota/kabupaten", "").strip(),
                            "Maps": maps_link
                        })
    except FileNotFoundError:
        print(f"❌ File tidak ditemukan: {file_path}")
    return hasil

# Cari file terkait untuk bank tertentu
def cari_data_cabang(norek, bank):
    file_mapping = {
        "mandiri": [
            "data/Mandiri_jakarta.csv",
            "data/Mandiri_luar-jakarta.csv",
            "data/Mandiri_luar_jakarta_2.csv"
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
        print("=" * 48)
        print("{:^48}".format("💳 GeoRek - Geo Lokasi Rekening Bank 💳"))
        print("=" * 48)
        print("|{:^46}|".format("MENU UTAMA"))
        print("|" + "-" * 46 + "|")
        print("| {:<3} {:<41}|".format("1.", "Cek Lokasi Rekening Bank MANDIRI"))
        print("| {:<3} {:<41}|".format("2.", "Cek Lokasi Rekening Bank BCA"))
        print("| {:<3} {:<41}|".format("3.", "Cek Lokasi Rekening Bank BRI"))
        print("| {:<3} {:<41}|".format("4.", "Keluar dari Aplikasi"))
        print("-" * 48)

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
