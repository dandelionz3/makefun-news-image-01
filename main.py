# Copy the finished entry image byte-for-byte to the requested output directory.
# Local run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
import os
import shutil
from pathlib import Path

source = Path(__file__).resolve().with_name("entry.png")
if not source.is_file():
    raise FileNotFoundError(f"Entry image is missing: {source}")
if source.stat().st_size > 1_048_576:
    raise ValueError(f"Entry image exceeds 1,048,576 bytes: {source.stat().st_size}")

output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
output_dir.mkdir(parents=True, exist_ok=True)
destination = output_dir / "entry.png"
shutil.copyfile(source, destination)
source_bytes = source.read_bytes()
written_bytes = destination.read_bytes()
if source_bytes != written_bytes:
    raise IOError(f"Copied image verification failed: {destination} differs from {source}")
print(f"Copied and verified {len(written_bytes)} bytes to {destination}")
