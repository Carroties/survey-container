# Survey Container · Fasilkom UI

Papan survei angkatan untuk mengumpulkan tautan formulir tugas, riset, dan praktikum. Pengunjung bisa menekan **+**, mengirim kartu, atau membuka ringkasan dari kartu yang tersedia. Papan mulai kosong dan semua pengunjung memakai database yang sama.

## Menjalankan di komputer

Butuh Python 3.10 atau lebih baru. Buka terminal di folder yang berisi `manage.py` dan buat lingkungan Python.

```sh
python -m venv .venv
```

Aktifkan lingkungan Python sesuai sistem operasi.

- Windows PowerShell — `.\.venv\Scripts\Activate.ps1`
- macOS atau Linux — `source .venv/bin/activate`

Pasang Django, siapkan database, lalu mulai server.

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Buka <http://127.0.0.1:8000/>. Jika perintah `python` tidak tersedia, gunakan `python3` di macOS/Linux atau `py` di Windows.

## Membaca kodenya

| File | Isi |
| --- | --- |
| `surveys/templates/surveys/board.html` | Halaman, kartu, dan formulir |
| `surveys/templates/surveys/detail.html` | Isi ringkasan satu kartu |
| `surveys/static/surveys/board.css` | Gaya dan tata letak yang menyesuaikan layar |
| `surveys/static/surveys/board.js` | Popup, pemuatan ringkasan, dan hilangnya kartu di tab yang terbuka |
| `surveys/forms.py` | Validasi data dari formulir |
| `surveys/views.py` | Alur membuka papan, menambah kartu, dan membaca detail |
| `surveys/models.py` | Struktur tabel survei dan masa aktif tujuh hari |

Tampilan memakai HTML, CSS, dan JavaScript murni. Django merender HTML, memvalidasi form, dan menyimpan kartu. Database bawaan di komputer adalah SQLite. Deployment Vercel memakai PostgreSQL. Waktu kedaluwarsa dihitung dari waktu terbit dan ditampilkan dalam WIB.

## Penghapusan otomatis

Begitu umur kartu mencapai tujuh hari, papan dan halaman ringkasannya berhenti menampilkan kartu. Django juga menghapus baris kedaluwarsa saat papan berikutnya dimuat. Jadwalkan perintah berikut pada server untuk membersihkan database meski tidak ada pengunjung.

```sh
python manage.py purge_surveys
```

Jalankan dengan lingkungan Python dan lokasi database yang sama dengan aplikasi. Contoh crontab Linux berikut berjalan setiap 15 menit. Ganti jalur sesuai lokasi proyek dan database di server.

```cron
*/15 * * * * cd /opt/survey-container && SURVEY_DB_PATH=/var/lib/survey-container/db.sqlite3 .venv/bin/python manage.py purge_surveys
```

## Deploy di Vercel

Vercel menjalankan Django sebagai Function. PostgreSQL menyimpan kartu secara persisten dan dapat digunakan bersama oleh semua instance.

1. Hubungkan database PostgreSQL ke proyek di **Storage** pada dashboard Vercel. Integrasi Neon, misalnya, dapat mengisi `DATABASE_URL` secara otomatis. Pastikan variabel-variabel ini tersedia di lingkungan **Production**.

   | Variabel | Nilai |
   | --- | --- |
   | `DATABASE_URL` | URL koneksi PostgreSQL dari penyedia database |
   | `DJANGO_ALLOWED_HOSTS` | Domain Vercel, misalnya `kelompok-8-ddp1.vercel.app`, tanpa `https://` |
   | `DJANGO_DEBUG` | `0` |
   | `DJANGO_SECRET_KEY` | Kunci acak dari `python -c "import secrets; print(secrets.token_urlsafe(50))"` |

2. Di folder proyek terbaru, aktifkan `.venv` dan jalankan `python -m pip install -r requirements.txt`. Buka terminal **PowerShell** untuk membuat tabel di PostgreSQL. Saat diminta, tempel URL koneksi dari penyedia database. Jika tersedia, pakai URL koneksi langsung (*unpooled*) ke database yang sama.

   ```powershell
   $env:DATABASE_URL = Read-Host "URL PostgreSQL produksi"
   python manage.py migrate --noinput
   Remove-Item Env:DATABASE_URL
   ```

   Simpan URL database dan kunci Django di pengaturan Vercel. Keduanya adalah kredensial pribadi.

3. Pastikan Vercel memakai preset **Django**, lalu deploy versi kode ini. Preset Django menjalankan `collectstatic` saat build.
4. Buka URL produksi, tambahkan survei uji, lalu buka papan dari sesi browser lain untuk memastikan kartunya tersimpan.

Dokumentasi Vercel [Deploy a Django app](https://vercel.com/docs/frameworks/full-stack/django) dan [Postgres on Vercel](https://vercel.com/docs/postgres).

## Deploy di server dengan penyimpanan persisten

Gunakan hosting yang bisa menjalankan Python/Django dengan HTTPS dan direktori database persisten. Jalankan satu instance aplikasi agar semua pengunjung memakai berkas SQLite yang sama. Gunicorn menjalankan aplikasi dan WhiteNoise melayani CSS serta JavaScript.

1. Pasang paket produksi dengan `python -m pip install -r requirements-production.txt`.
2. Atur variabel lingkungan pada host.

   | Variabel | Nilai |
   | --- | --- |
   | `DJANGO_DEBUG` | `0` |
   | `DJANGO_SECRET_KEY` | Kunci acak dari `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
   | `DJANGO_ALLOWED_HOSTS` | Domain yang akan dibagikan, tanpa `https://` |
   | `SURVEY_DB_PATH` | Jalur absolut berkas SQLite dalam direktori persisten yang bisa ditulis |
   | `DJANGO_HTTPS_PROXY` | `1` jika reverse proxy tepercaya mengatur sendiri header `X-Forwarded-Proto` |

3. Jalankan `python manage.py migrate` dan `python manage.py collectstatic --noinput`.
4. Jalankan `gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}"` pada host Linux. Arahkan HTTPS ke port aplikasi sesuai konfigurasi hosting.
5. Gunakan URL HTTPS dari hosting untuk dibagikan ke grup. Setiap pengunjung dengan akses ke papan bisa melihat nama dan kontak yang tercantum pada kartu.

Untuk mengelola kartu melalui panel Django, buat akun dengan `python manage.py createsuperuser`, lalu buka `/admin/`.
