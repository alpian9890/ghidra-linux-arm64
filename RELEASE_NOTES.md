Paket Ghidra 12.2 Linux ARM64 untuk CLI/headless di Ubuntu proot-distro pada Termux.

Isi:
- Ghidra 12.2 dengan lima executable native ARM64 hasil cross-compile.
- Temurin JDK 25 ARM64 dalam paket.
- Launcher headless dengan heap awal maksimum 1 GiB.
- Skrip smoke-test dan binary contoh.

Validasi di VPS AMD64: checksum distribusi upstream dan JDK, ARM64 GNU
demangler, SLEIGH, roundtrip LZFSE, serta dekompilasi fungsi contoh melalui
QEMU. Pengujian langsung pada Android/proot dijalankan dengan
`./smoke-test.sh` setelah ekstraksi.

Unduh `ghidra-12.2-arm64.tar.gz` dan file `.sha256`, lalu:

```bash
sha256sum -c ghidra-12.2-arm64.tar.gz.sha256
tar -xzf ghidra-12.2-arm64.tar.gz
cd ghidra-12.2-arm64
./smoke-test.sh
```

SHA-256 arsip:
`6b12b5039223b81a59e269d847b09009cf1c13483dde8dd541ab02496b6de494`

Lihat README repository untuk perintah unduh yang dapat dilanjutkan dengan `wget -c`.

Upstream: [Ghidra](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.2_build),
[Temurin](https://adoptium.net/).
