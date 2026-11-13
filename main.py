"""Copy and verify the entry image in the harness output directory.

Local run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
from pathlib import Path

MAX_BYTES = 1_048_576
source = Path(__file__).resolve().with_name("entry.png")
if not source.is_file():
    raise FileNotFoundError(f"Entry image is missing: {source}")
source_size = source.stat().st_size
if source_size > MAX_BYTES:
    raise ValueError(f"Entry image is {source_size} bytes; maximum is {MAX_BYTES}")

output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
output_dir.mkdir(parents=True, exist_ok=True)
target = output_dir / "entry.png"
shutil.copyfile(source, target)
if source.read_bytes() != target.read_bytes():
    raise IOError(f"Copied entry image does not match source: {target}")
print(f"Copied and verified {target.stat().st_size} bytes at {target}")
