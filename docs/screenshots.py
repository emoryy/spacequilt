#!/usr/bin/env python3
"""Render the README screenshots from a synthetic home directory.

The tree is made up (deterministic names and sizes, no real data), so the
images can be regenerated after UI changes and never leak anything local.

    QT_QPA_PLATFORM=offscreen python3 docs/screenshots.py

Writes docs/boxes.png and docs/icicle.png at 880x560, the content width of a
GitHub README, so they show 1:1 there. Settings go to a throwaway config dir.
"""

import importlib.machinery
import importlib.util
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIZE = (880, 560)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp(prefix="spacequilt-shots-")

loader = importlib.machinery.SourceFileLoader("sq", os.path.join(ROOT, "spacequilt"))
spec = importlib.util.spec_from_loader("sq", loader)
sq = importlib.util.module_from_spec(spec)
loader.exec_module(sq)

from PySide6.QtWidgets import QApplication  # noqa: E402

MB = 1024          # sizes are in KiB, as du reports them
GB = 1024 * MB
H = "/home/alex"


def synthetic_du():
    rnd = random.Random(7)
    lines = []

    def f(path, kib):
        lines.append((int(kib), path))

    def files(base, prefix, ext, n, lo, hi):
        for i in range(n):
            f(f"{base}/{prefix}{i:03d}.{ext}",
              rnd.lognormvariate(0, 1) * (hi - lo) / 3 + lo)

    f(f"{H}/Videos/2025-summer-trip.mkv", 9 * GB)
    f(f"{H}/Videos/wedding-ceremony.mp4", 5 * GB)
    files(f"{H}/Videos/Screencasts", "screencast-", "webm", 14, 60 * MB, 400 * MB)
    files(f"{H}/Videos/Phone", "VID_2025", "mp4", 30, 20 * MB, 300 * MB)

    games = f"{H}/.local/share/Steam/steamapps/common"
    for name, size in (("Starfarer", 38), ("Hollow Depths", 12),
                       ("Rally Dust 4", 22), ("Tiny Towns", 3)):
        f(f"{games}/{name}/data/assets.pak", size * GB * 0.7)
        f(f"{games}/{name}/data/audio.pak", size * GB * 0.2)
        files(f"{games}/{name}/bin", "lib", "so", 12, 2 * MB, 40 * MB)
        files(f"{games}/{name}/data/maps", "map", "bsp", 25, 10 * MB, 200 * MB)
    f(f"{H}/.local/share/Steam/steamapps/shadercache/cache.bin", 3 * GB)

    for pkg in ("torch", "numpy", "scipy", "opencv", "transformers", "pillow",
                "matplotlib", "pandas"):
        files(f"{H}/.cache/pip/wheels/{pkg}", "chunk", "whl",
              rnd.randint(3, 12), 5 * MB, 300 * MB)
    files(f"{H}/.cache/thumbnails/large", "thumb", "png", 900, 20, 120)
    files(f"{H}/.cache/thumbnails/normal", "thumb", "png", 600, 8, 40)
    for cache in ("Cache_Data", "Code Cache", "GPUCache"):
        files(f"{H}/.cache/browser/Default/{cache}", "f_", "dat", 300, 30, 900)

    f(f"{H}/Models/llm/mistral-7b-q4.gguf", 4.1 * GB)
    f(f"{H}/Models/llm/llama-8b-q6.gguf", 6.6 * GB)
    f(f"{H}/Models/diffusion/sdxl-base.safetensors", 6.9 * GB)
    files(f"{H}/Models/diffusion/loras", "lora-", "safetensors", 18, 50 * MB, 400 * MB)

    for proj in ("website", "photo-tools", "game-jam-2025", "dotfiles", "thesis"):
        files(f"{H}/Projects/{proj}/src", "module", "py", rnd.randint(10, 40), 4, 80)
        files(f"{H}/Projects/{proj}/.git/objects/pack", "pack-", "pack",
              rnd.randint(1, 4), 2 * MB, 200 * MB)
        if proj in ("website", "game-jam-2025"):
            for mod in ("react", "webpack", "typescript", "esbuild", "lodash",
                        "three", "vite"):
                files(f"{H}/Projects/{proj}/node_modules/{mod}/dist", "chunk", "js",
                      rnd.randint(5, 30), 20, 3000)
    files(f"{H}/Projects/thesis/figures", "fig", "pdf", 40, 200, 4000)

    for year in (2022, 2023, 2024, 2025):
        for month in range(1, 13, 2):
            files(f"{H}/Pictures/{year}/{year}-{month:02d}", "IMG_", "jpg",
                  rnd.randint(15, 60), 3 * MB, 12 * MB)
        files(f"{H}/Pictures/{year}/raw", "DSC_", "nef", rnd.randint(40, 120),
              20 * MB, 45 * MB)
    for artist in ("Aurora Lane", "The Night Shift", "Kobalt", "Ellis Grey",
                   "Sundial", "Marrow"):
        for album in range(rnd.randint(1, 3)):
            files(f"{H}/Music/{artist}/Album {album + 1}", "track", "flac", 11,
                  20 * MB, 45 * MB)

    files(f"{H}/Documents/invoices", "invoice-", "pdf", 80, 60, 400)
    files(f"{H}/Documents/manuals", "manual-", "pdf", 25, 1 * MB, 30 * MB)
    f(f"{H}/Downloads/ubuntu-24.04-desktop.iso", 5.7 * GB)
    f(f"{H}/Downloads/driver-installer.run", 400 * MB)
    files(f"{H}/Downloads", "download-", "zip", 40, 1 * MB, 300 * MB)
    f(f"{H}/VirtualMachines/win11/win11.qcow2", 48 * GB)
    f(f"{H}/VirtualMachines/win11/snapshot-1.qcow2", 11 * GB)
    f(f"{H}/.config/app/settings.json", 4)
    files(f"{H}/.config/editor/User", "state", "db", 12, 50, 3000)

    # du reports cumulative directory sizes, children before parents.
    sizes = {}
    for kib, path in lines:
        sizes[path] = kib
        d = path.rsplit("/", 1)[0]
        while d.startswith(H):
            sizes[d] = sizes.get(d, 0) + kib
            if d == H:
                break
            d = d.rsplit("/", 1)[0]
    return [f"{sizes[p]}\t{p}" for p in sorted(sizes, key=lambda p: -p.count("/"))]


def main():
    app = QApplication(sys.argv)
    builder = sq.TreeBuilder()
    for line in synthetic_du():
        builder.add(line)
    root = builder.finish()

    for view in ("boxes", "icicle"):
        win = sq.MainWindow(None, True, style="raised", view=view)
        win.resize(*SIZE)
        win.show()
        for widget in win.views.values():
            widget.set_root(root)
        win._leave_start()
        win._on_focus(root)
        app.processEvents()
        win.view.grab()          # first frame lays out the view
        app.processEvents()
        out = os.path.join(HERE, f"{view}.png")
        win.grab().save(out)
        print(out)


if __name__ == "__main__":
    main()
