"""Copy a demo into `examples/`: the reports as they are, the images as previews of at most 1600 px.

A pipeline's outputs are not versioned (they are made again, and the certified surface weighs 55 MB); the examples
are, so that what each prize returns can be seen on GitHub, and they say which command they come from.

    uv run vesuve demo --data <data/ of the experimental branch> --output outputs/demo
    uv run python tools/make_examples.py outputs/demo
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parents[1]


def main() -> int:
    source, target = Path(sys.argv[1]), HERE / "examples"
    for prize in sorted(p for p in source.iterdir() if (p / "report.json").exists()):
        d = target / prize.name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        for f in sorted(prize.iterdir()):
            if f.is_file() and f.suffix in (".md", ".json") and f.stat().st_size < 400_000:
                shutil.copy2(f, d / f.name)
            elif f.is_file() and f.suffix in (".png", ".jpg"):
                im = Image.open(f).convert("RGB")
                im.thumbnail((1600, 1600))
                im.save(d / f"{f.stem}.jpg", quality=85, optimize=True)
        print(f"{prize.name}: {len(list(d.iterdir()))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
