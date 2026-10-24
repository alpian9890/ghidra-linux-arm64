# Ghidra Linux ARM64

Paket komunitas Ghidra 12.2 untuk mode CLI/headless di Ubuntu ARM64,
termasuk Ubuntu proot-distro di Termux. Paket menyertakan Temurin JDK 25
ARM64 dalam folder terpisah.

## Unduh dan jalankan

Jalankan di dalam Ubuntu proot dan simpan di filesystem internal Ubuntu.
Arsip sekitar 697 MiB; ukuran setelah ekstraksi sekitar 1.2 GiB.

```bash
mkdir -p ~/tools
cd ~/tools
wget -c https://github.com/alpian9890/ghidra-linux-arm64/releases/download/v12.2-arm64.1/ghidra-12.2-arm64.tar.gz
wget -c https://github.com/alpian9890/ghidra-linux-arm64/releases/download/v12.2-arm64.1/ghidra-12.2-arm64.tar.gz.sha256
sha256sum -c ghidra-12.2-arm64.tar.gz.sha256
tar -xzf ghidra-12.2-arm64.tar.gz
cd ghidra-12.2-arm64
./smoke-test.sh
```

Jika koneksi terputus, jalankan kembali perintah `wget -c` yang sama.
Tes yang berhasil menampilkan `ARM64_DECOMPILE_TEST_OK`.

Analisis binary sendiri:

```bash
mkdir -p projects
./analyzeHeadless ./projects ProyekSaya -import /path/ke/binary -max-cpu 2
```

Launcher memakai JDK dalam paket dan heap maksimum awal 1024M.
Untuk memakai heap lebih besar saat RAM mencukupi:

```bash
GHIDRA_HEADLESS_MAXMEM=1536M ./analyzeHeadless ./projects ProyekSaya -import /path/ke/binary -max-cpu 2
```

## Isi paket dan pengujian

- Distribusi resmi Ghidra 12.2.
- Lima executable Linux ARM64 hasil cross-compile dengan static linking:
  decompiler, SLEIGH, GNU demangler 2.24 dan 2.41, serta LZFSE.
- Temurin JDK 25 ARM64, launcher headless, binary contoh, dan tes dekompilasi.

Build dilakukan pada Ubuntu 24.04 AMD64. GNU demangler, SLEIGH, dan
roundtrip LZFSE diuji melalui QEMU. Integrasi Ghidra headless memakai JVM
AMD64 dan executable decompiler ARM64 melalui QEMU; fungsi contoh berhasil
didekompilasi menjadi `return a + b + 7;`.

Target pengguna adalah Ubuntu 25.04 ARM64 di proot. Pengujian langsung
pada perangkat Android/proot dilakukan dengan `./smoke-test.sh` setelah
ekstraksi. Paket ini disiapkan untuk penggunaan headless.

## Build dari VPS AMD64

Pada Ubuntu 24.04 AMD64:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends python3 curl unzip make file g++-aarch64-linux-gnu qemu-user
git clone https://github.com/alpian9890/ghidra-linux-arm64.git
cd ghidra-linux-arm64
bash rebuild.sh
```

`bootstrap.py` mengambil distribusi upstream dan JDK yang dipin versinya,
memverifikasi SHA-256, lalu menyiapkan JDK untuk build dan pengujian.
`rebuild.sh` membangun native ARM64 dengan dua worker, menjalankan tes,
dan membuat paket dalam `output/`. Source Java Ghidra menggunakan paket
rilis resmi; yang dikompilasi ulang adalah komponen native.

Repo Git hanya melacak skrip dan metadata upstream yang dipilih.
Arsip, hasil ekstraksi, cache, log, dan file autentikasi berada di luar
daftar file yang dilacak.

## Sumber dan lisensi

- [Ghidra 12.2 upstream](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.2_build)
- [Eclipse Temurin](https://adoptium.net/)
- Lisensi skrip repository ini: Apache-2.0, lihat LICENSE.
- Komponen Ghidra, GNU demangler, dan Temurin mengikuti lisensi upstream
  masing-masing. Paket menyertakan dokumen lisensi upstream beserta source
  native yang disediakan distribusi Ghidra.
