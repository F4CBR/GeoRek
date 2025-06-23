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
        return norek[:5]
    elif bank == "bca":
        return norek[:3]
    elif bank == "bri":
        return norek[:3]
    return norek

# Baca file CSV dan cari cabang
def cari_cabang(file_path, kode_cabang, bank):
    hasil = []
    try:
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [field.lower() for field in reader.fieldnames]
            for row in reader:
                row = {key.lower(): value for key, value in row.items()}
                kode = str(row.get("kode cabang", "")).strip()
                if kode.startswith(kode_cabang):
                    nama_cabang = (
                        row.get("nama cabang", "").strip() or
                        row.get("nama", "").strip() or
                        row.get("cabang", "").strip()
                    )
                    maps_link = generate_maps_link(nama_cabang, bank)
                    if bank == "mandiri":
                        if "region" in row:
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
                            hasil.append({
                                "Kode Cabang": kode,
                                "Nama Cabang": nama_cabang,
                                "Alamat": row.get("alamat", "").strip(),
                                "Kota": row.get("kota", "").strip(),
                                "Maps": maps_link
                            })
                        elif "area" in row:
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
                            "Kota": row.get("kota", "").strip(),
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
    return hasil[:1]

# Menu utama
def tampil_menu():
    while True:
        clear_screen()
        print("=" * 48)
        print("{:^48}".format("💳 GeoRek - Geo Lokasi Rekening Bank 💳"))
        print("=" * 48)
        print("|{:^46}|".format("MENU UTAMA"))
        print("|" + "-" * 46 + "|")
        print("| {:<3} {:<41}|".format("1.", "Bank MANDIRI"))
        print("| {:<3} {:<41}|".format("2.", "Bank BCA"))
        print("| {:<3} {:<41}|".format("3.", "Bank BRI"))
        print("| {:<3} {:<41}|".format("4.", "Beberapa Rekening"))
        print("| {:<3} {:<41}|".format("5.", "Keluar dari Aplikasi"))
        print("-" * 48)

        pilihan = input("Silakan pilih menu (1-5): ").strip()
        bank_dict = {"1": "mandiri", "2": "bca", "3": "bri"}

        if pilihan == "5":
            print("\n👋 Terima kasih telah menggunakan GeoRek.\n")
            break
        elif pilihan in bank_dict:
            geo_interface(bank_dict[pilihan])
        elif pilihan == "4":
            geo_interface_multi()
        else:
            print("\n❌ Pilihan tidak valid.")
            input("Tekan Enter untuk kembali...")

# Interface satu bank
def geo_interface(bank):
    clear_screen()
    print("🌐 Geo INT -", bank.upper())
    print("=" * 40)
    norek = input("Masukkan Nomor Rekening: ").strip()
    if not norek.isdigit():
        print("\n❌ Input tidak valid! Harap masukkan angka.")
        input("\nTekan Enter untuk kembali...")
        return
    hasil = cari_data_cabang(norek, bank)
    clear_screen()
    print("📌 Hasil Pencarian:")
    print("=" * 40)
    if not hasil:
        print(f"❌ Tidak ada data yang cocok untuk {bank.upper()} kode: {norek[:5]}")
    else:
        for data in hasil:
            cetak_data(bank, data)
    input("\nTekan Enter untuk kembali ke menu...")

# Interface banyak bank
def geo_interface_multi():
    clear_screen()
    print("🌐 Geo INT - Multiple BANK")
    print("=" * 40)
    print("Note:")
    print('- Pilihan Nama Bank:')
    print('  1. Mandiri')
    print('  2. BCA')
    print('  3. BRI')
    print('- Tekan Enter pada kolom Nama Bank jika sudah selesai.\n')

    input_list = []
    bank_map = {"1": "mandiri", "2": "bca", "3": "bri"}

    while True:
        kode = input("Nama Bank: ").strip()
        if kode == "":
            break
        if kode not in bank_map:
            print("❌ Kode bank tidak dikenal.")
            continue
        norek = input("Nomor rekening: ").strip()
        if not norek.isdigit():
            print("❌ Nomor rekening harus berupa angka.")
            continue
        input_list.append((bank_map[kode], norek))

    hasil_akhir = {}
    for bank, norek in input_list:
        hasil_akhir.setdefault(bank, []).extend(cari_data_cabang(norek, bank))

    clear_screen()
    print("📌 Hasil Pencarian:")
    print("=" * 40)
    for bank, entries in hasil_akhir.items():
        print(f"\n🏦 Bank: {bank.upper()}")
        if not entries:
            print("❌ Tidak ada data ditemukan.")
        else:
            for data in entries:
                cetak_data(bank, data)
    input("\nTekan Enter untuk kembali ke menu...")

# Cetak data dengan ikon
def cetak_data(bank, data):
    if "Kode Cabang" in data:
        print(f"🔢 Kode Cabang  : {data.get('Kode Cabang', '-')}")
    if "Nama Cabang" in data:
        print(f"🏢 Nama Cabang  : {data.get('Nama Cabang', '-')}")
    if "Alamat" in data:
        print(f"📬 Alamat       : {data.get('Alamat', '-')}")
    if "Kota" in data:
        print(f"🏙️ Kota         : {data.get('Kota', '-')}")
    if "Provinsi" in data:
        print(f"📍 Provinsi     : {data.get('Provinsi', '-')}")
    if "Kode Pos" in data:
        print(f"📮 Kode Pos     : {data.get('Kode Pos', '-')}")
    if "Maps" in data:
        print(f"🗺️ Maps         : {data.get('Maps', '-')}")
    print("-" * 40)

# Jalankan program
if __name__ == "__main__":
    tampil_menu()
