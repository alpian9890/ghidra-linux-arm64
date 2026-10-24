#!/usr/bin/env python3
import hashlib, json, os, subprocess, tempfile
from pathlib import Path
b=Path(__file__).resolve().parent
g=b/"ghidra_12.2_PUBLIC"
native=list(g.glob("**/build/os/linux_arm_64/*"))
assert len(native)==5, [str(p) for p in native]
for p in native:
    h=subprocess.check_output(["file",str(p)],text=True)
    assert "ARM aarch64" in h and "statically linked" in h,h
    print(h.strip(),flush=True)
for arch in ("arm64","amd64"):
    spec=json.loads((b/f"temurin25-{arch}.json").read_text())[0]["binary"]["package"]
    digest=hashlib.file_digest((b/f"temurin25-{arch}.tar.gz").open("rb"),"sha256").hexdigest()
    assert digest==spec["checksum"],(arch,digest)
d=g/"GPL/DemanglerGnu/build/os/linux_arm_64/demangler_gnu_v2_41"
r=subprocess.run(["qemu-aarch64",str(d)],input="_Z3addii\n",text=True,capture_output=True,check=True)
assert "add(int, int)" in r.stdout,r.stdout
print("ARM64_DEMANGLER_TEST_OK",flush=True)
with tempfile.TemporaryDirectory(dir=b) as td:
    t=Path(td)
    original=b"ghidra arm64 cross compilation test\n"*128
    (t/"in").write_bytes(original)
    l=g/"Ghidra/Features/FileFormats/build/os/linux_arm_64/lzfse"
    subprocess.run(["qemu-aarch64",str(l),"-encode","-i",str(t/"in"),"-o",str(t/"encoded")],check=True)
    subprocess.run(["qemu-aarch64",str(l),"-decode","-i",str(t/"encoded"),"-o",str(t/"out")],check=True)
    assert (t/"out").read_bytes()==original
print("ARM64_LZFSE_ROUNDTRIP_TEST_OK",flush=True)
s=g/"Ghidra/Features/Decompiler/build/os/linux_arm_64/sleigh"
r=subprocess.run(["qemu-aarch64",str(s)],capture_output=True,text=True,timeout=30)
assert "sleigh" in (r.stdout+r.stderr).lower(),(r.returncode,r.stdout,r.stderr)
print("ARM64_SLEIGH_TEST_OK",flush=True)
(b/"smoke_demo.c").write_text("int ghidra_arm64_add(int a, int b) { return a + b + 7; }\nint main(void) { return ghidra_arm64_add(2, 3); }\n")
subprocess.run(["aarch64-linux-gnu-gcc","-O0","-g","-fno-inline",str(b/"smoke_demo.c"),"-o",str(b/"smoke_demo")],check=True)
(b/"VerifyArm64.java").write_text("""import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.listing.Function;
public class VerifyArm64 extends GhidraScript {
  @Override public void run() throws Exception {
    var functions = getGlobalFunctions("ghidra_arm64_add");
    if (functions.isEmpty()) throw new AssertionError("Test function not found");
    Function f = functions.get(0);
    DecompInterface d = new DecompInterface();
    try {
      if (!d.openProgram(currentProgram)) throw new AssertionError(d.getLastMessage());
      var result = d.decompileFunction(f, 90, monitor);
      if (!result.decompileCompleted()) throw new AssertionError(result.getErrorMessage());
      String code = result.getDecompiledFunction().getC();
      if (!code.contains("ghidra_arm64_add") || !code.contains("+")) throw new AssertionError(code);
      println("ARM64_DECOMPILE_TEST_OK");
      println(code);
    } finally { d.dispose(); }
  }
}
""")
host=g/"Ghidra/Features/Decompiler/os/linux_x86_64/decompile"
backup=host.with_name("decompile.amd64-original")
assert not backup.exists(),backup
arm=g/"Ghidra/Features/Decompiler/build/os/linux_arm_64/decompile"
host.rename(backup)
try:
    host.write_text("#!/bin/sh\nexec /usr/bin/qemu-aarch64 "+str(arm)+' "$@"\n')
    host.chmod(0o755)
    env=os.environ.copy()
    env["JAVA_HOME"]=str(b/"test-jdk25")
    env["PATH"]=str(b/"test-jdk25/bin")+os.pathsep+env["PATH"]
    env["GHIDRA_HEADLESS_MAXMEM"]="1024M"
    env["GHIDRA_HEADLESS_JAVA_OPTIONS"]="-XX:ActiveProcessorCount=2 -Duser.home="+str(b/"test-home")
    (b/"test-home").mkdir(exist_ok=True)
    (b/"test-projects").mkdir(exist_ok=True)
    command=[str(g/"support/analyzeHeadless"),str(b/"test-projects"),"SmokeArm64","-import",str(b/"smoke_demo"),"-scriptPath",str(b),"-postScript","VerifyArm64.java","-max-cpu","2","-deleteProject"]
    with (b/"headless-test.log").open("w") as log:
        r=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    result=(b/"headless-test.log").read_text()
    assert r.returncode==0 and "ARM64_DECOMPILE_TEST_OK" in result,result[-12000:]
    print("ARM64_GHIDRA_HEADLESS_DECOMPILE_TEST_OK",flush=True)
finally:
    host.unlink(missing_ok=True)
    backup.rename(host)
print("ALL_TESTS_PASSED",flush=True)
