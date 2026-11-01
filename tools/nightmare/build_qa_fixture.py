"""Build a separate developer-only Scratch project; never overwrite release."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_sb3 import build_project

root = Path(__file__).resolve().parents[2]
out = root / 'qa-output' / 'NEXUS-BLOCKS-NIGHTMARE-QA-ONLY.sb3'
build_project(str(out), qa_mode=True)
print(f'QA-ONLY project: {out}')
