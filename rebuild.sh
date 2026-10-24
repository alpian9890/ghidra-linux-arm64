#!/usr/bin/env bash
set -euo pipefail
build_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$build_dir/bootstrap.py"
export JAVA_HOME="$build_dir/test-jdk25"
export PATH="$JAVA_HOME/bin:$PATH"
export GRADLE_USER_HOME="$build_dir/../gradle-cache"
cd "$build_dir/ghidra_12.2_PUBLIC/support/gradle"
./gradlew --no-daemon --max-workers=2 -Dorg.gradle.jvmargs=-Xmx1024m -I "$build_dir/cross-arm64.init.gradle" buildNatives_linux_arm_64
cd "$build_dir"
python3 -u test-arm64.py | tee native-test.log
python3 package-arm64.py
