#!/usr/bin/env python3
import hashlib, json, os, shutil, subprocess, tarfile, zipfile
from pathlib import Path
b=Path(__file__).resolve().parent
g=b/"ghidra_12.2_PUBLIC"
assert "ALL_TESTS_PASSED" in (b/"native-test.log").read_text()
out=b/"output"
out.mkdir(exist_ok=True)
root=out/"ghidra-12.2-arm64"
root.mkdir(exist_ok=True)
clean=root/"ghidra_12.2_PUBLIC"
if not clean.exists():
    with zipfile.ZipFile(b/"ghidra_12.2_PUBLIC_20261016.zip") as z:
        z.extractall(root)
        for info in z.infolist():
            mode=info.external_attr>>16
            if mode:
                (root/info.filename).chmod(mode&0o777)
natives=list(g.glob("**/build/os/linux_arm_64/*"))
assert len(natives)==5
for p in natives:
    rel=p.relative_to(g)
    dest=clean/Path(str(rel).replace("/build/os/","/os/"))
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dest)
    subprocess.run(["aarch64-linux-gnu-strip",str(dest)],check=True)
    dest.chmod(0o755)
jdk=root/"jdk-25"
jdk.mkdir(exist_ok=True)
if not (jdk/"bin/java").exists():
    subprocess.run(["tar","-xzf",str(b/"temurin25-arm64.tar.gz"),"-C",str(jdk),"--strip-components=1"],check=True)
launcher='''#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export JAVA_HOME="$task_root/jdk-25"
export PATH="$JAVA_HOME/bin:$PATH"
export GHIDRA_HEADLESS_MAXMEM="${GHIDRA_HEADLESS_MAXMEM:-1024M}"
export GHIDRA_HEADLESS_JAVA_OPTIONS="-XX:ActiveProcessorCount=2 ${GHIDRA_HEADLESS_JAVA_OPTIONS:-}"
exec "$task_root/ghidra_12.2_PUBLIC/support/analyzeHeadless" "$@"
'''
(root/"analyzeHeadless").write_text(launcher)
(root/"analyzeHeadless").chmod(0o755)
scripts=root/"scripts"
scripts.mkdir(exist_ok=True)
shutil.copy2(b/"VerifyArm64.java",scripts/"VerifyArm64.java")
shutil.copy2(b/"smoke_demo",root/"smoke_demo")
smoke='''#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$task_root/test-projects"
"$task_root/jdk-25/bin/java" -version
"$task_root/analyzeHeadless" "$task_root/test-projects" "SmokeArm64-$$" -import "$task_root/smoke_demo" -scriptPath "$task_root/scripts" -postScript VerifyArm64.java -max-cpu 2 -deleteProject 2>&1 | tee "$task_root/smoke-test.log"
grep -q ARM64_DECOMPILE_TEST_OK "$task_root/smoke-test.log"
'''
(root/"smoke-test.sh").write_text(smoke)
(root/"smoke-test.sh").chmod(0o755)
readme="""Ghidra 12.2 ARM64 untuk Ubuntu proot di Termux
================================================
Paket ini memuat rilis resmi Ghidra 12.2, lima executable native Linux ARM64
hasil cross-compile di VPS AMD64, serta Temurin JDK 25 ARM64.
Java sistem tidak perlu diganti. Launcher analyzeHeadless memakai JDK dalam paket.
Default heap headless 1024M dan jumlah CPU JVM 2.
Hasil cross-compile memakai static linking untuk executable native.

Jalankan di dalam Ubuntu proot, dari filesystem internal Ubuntu:
  ./smoke-test.sh
  mkdir -p projects
  ./analyzeHeadless ./projects ProyekSaya -import /path/program -max-cpu 2

Untuk binary lebih besar, jika RAM cukup:
  GHIDRA_HEADLESS_MAXMEM=1536M ./analyzeHeadless ./projects ProyekSaya -import /path/program

Paket ini disiapkan dan diuji untuk mode headless.
Pengujian di VPS: ARM64 demangler, LZFSE roundtrip, SLEIGH, dan decompiler ARM64
di bawah QEMU. Integrasi decompiler diuji menggunakan JVM AMD64 dan executable
decompiler ARM64 melalui QEMU. Tes penuh pada Android/proot dilakukan dengan
smoke-test.sh setelah ekstraksi.

Build di VPS:
  cd /root/ghidra-arm64-build/12.2
  bash rebuild.sh
Konfigurasi cross-compiler: cross-arm64.init.gradle
Log build: build.log
Log tes native: native-test.log
Log tes headless: headless-test.log

Sumber:
https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.2_build
https://adoptium.net/
"""
(root/"README-id.txt").write_text(readme)
metadata={
    "ghidra":"12.2",
    "ghidra_original_sha256":"2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67",
    "jdk":json.loads((b/"temurin25-arm64.json").read_text())[0],
    "build_host":"Ubuntu 24.04 AMD64",
    "target":"Linux ARM64 (Ubuntu proot)",
    "native_linking":"static",
    "native_test":"AMD64 JVM + QEMU ARM64 native decompiler, plus native tool tests",
}
(root/"BUILD_METADATA.json").write_text(json.dumps(metadata,indent=2)+"\n")
for p in (root/"analyzeHeadless",root/"smoke-test.sh"):
    subprocess.run(["bash","-n",str(p)],check=True)
artifact=out/"ghidra-12.2-arm64.tar.gz"
with tarfile.open(artifact,"w:gz",compresslevel=3) as tar:
    tar.add(root,arcname=root.name)
digest=hashlib.file_digest(artifact.open("rb"),"sha256").hexdigest()
(out/"ghidra-12.2-arm64.tar.gz.sha256").write_text(digest+"  "+artifact.name+"\n")
with tarfile.open(artifact,"r:gz") as tar:
    names=set(tar.getnames())
    assert root.name+"/jdk-25/bin/java" in names
    for name in ("analyzeHeadless","smoke-test.sh","scripts/VerifyArm64.java","smoke_demo"):
        assert root.name+"/"+name in names,name
print(str(artifact))
print(f"Size: {artifact.stat().st_size} bytes")
print(f"SHA256: {digest}")
print("PACKAGE_OK")
