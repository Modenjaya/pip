import requests
import time
import os
from datetime import datetime, timedelta

# --- Konfigurasi ---
CHECK_IN_URL = "https://api-mm.pip.world/account/check-in"
COOKIE_FILE = "cookie.txt" 
SECONDS_IN_DAY = 86400 # 24 jam = 86400 detik
# -------------------

# Header dasar yang dibutuhkan untuk request POST
BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://mm.pip.world",
    "referer": "https://mm.pip.world/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "content-length": "0",
}

def load_cookies_and_check_in():
    """Memuat semua cookie dari file dan menjalankan check-in."""
    
    try:
        with open(COOKIE_FILE, 'r') as f:
            # Baca baris yang tidak kosong
            raw_lines = [line.strip() for line in f if line.strip()]
            
    except FileNotFoundError:
        print(f"🚨 GAGAL: File '{COOKIE_FILE}' tidak ditemukan.")
        return

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Ditemukan {len(raw_lines)} akun untuk diproses. 🚀")
    
    for index, line in enumerate(raw_lines, 1):
        # Ambil string cookie, abaikan komentar setelah '#'
        cookie_string = line.split('#')[0].strip()
        account_note = line.split('#')[1].strip() if '#' in line else f"Akun #{index}"

        if not cookie_string:
            continue
            
        print("-" * 50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Check-in untuk: **{account_note}**")
        
        # 1. Gabungkan Header dan Cookie
        headers = BASE_HEADERS.copy()
        headers["cookie"] = cookie_string
        
        try:
            # 2. Kirim Permintaan POST
            response = requests.post(CHECK_IN_URL, headers=headers)
            
            # 3. Periksa Hasil
            if response.status_code == 200:
                data = response.json()
                print("  ✅ Berhasil Check-in!")
                print(f"     Response: XP diterima: {data.get('xp')}, Streak: {data.get('streak')}")
                
            elif response.status_code == 401:
                print("  ❌ GAGAL: Token/Cookie KADALUWARSA (401 Unauthorized).")
                print(f"     Periksa cookie untuk **{account_note}** di {COOKIE_FILE}.")
            
            elif "already checked-in" in response.text.lower():
                print("  ℹ️ Sudah Check-in hari ini.")
            
            else:
                print(f"  ❌ GAGAL: Status Code {response.status_code}")
                print(f"     Response Text: {response.text[:100]}...")
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Terjadi kesalahan koneksi: {e}")
        
        # Jeda sebentar antar akun untuk menghindari rate limit
        time.sleep(3) 

    print("\n[INFO] Selesai memproses semua akun.")
    print("-" * 50)


def main_loop_24h():
    """Fungsi utama yang menjalankan loop 24 jam sederhana."""
    
    print(f"*** Auto Check-In Bot Dimulai ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB) ***")
    
    while True:
        start_time = time.time()
        
        # 1. Jalankan Check-in
        print(f"\n--- WAKTUNYA CHECK-IN ({datetime.now().strftime('%H:%M:%S')}) ---")
        load_cookies_and_check_in()
        
        end_time = time.time()
        
        # Hitung waktu yang dibutuhkan untuk eksekusi
        execution_time = end_time - start_time
        
        # Hitung sisa waktu tidur: 24 jam dikurangi waktu eksekusi
        sleep_duration = SECONDS_IN_DAY - execution_time
        
        # Pastikan tidak ada waktu tunggu negatif (jika eksekusi > 24 jam)
        if sleep_duration < 0:
            sleep_duration = 0
            print("⚠️ Peringatan: Waktu eksekusi melebihi 24 jam. Jeda diabaikan.")
        
        # 2. Tidur selama sisa durasi
        next_run = datetime.now() + timedelta(seconds=sleep_duration)
        print(f"\n😴 Tidur... Eksekusi membutuhkan waktu {execution_time:.2f} detik.")
        print(f"   Jeda selama {sleep_duration:.0f} detik. Jalankan lagi pada {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        time.sleep(sleep_duration)
        
        # 3. Loop kembali untuk eksekusi berikutnya

if __name__ == "__main__":
    main_loop_24h()
