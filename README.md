# spacequilt

A modern, minimal take on [xdiskusage](https://xdiskusage.sourceforge.net/)'s
**icicle** disk-usage visualization: horizontal, size-proportional columns you
click to drill into. Same interaction model as the Android *DiskUsage* app,
rebuilt on Qt6 (PySide6) so it looks and themes like a current desktop app.

Like the original xdiskusage, it doesn't implement its own filesystem walker,
it parses the output of `du` (`du -k --all`), which is fast, correct, and
already handles the awkward parts (hardlinks, sparse files, block accounting).

## Requirements

- Python 3
- PySide6 (`pip install --user PySide6`, or your distro's `pyside6` package)
- `du` (coreutils)

## Usage

```sh
spacequilt [PATH] [-x/--one-filesystem]
```

- `PATH` — directory to scan (default: current directory)
- `-x`, `--one-filesystem` — don't cross mount points (passes `-x` to `du`)

### Interaction

| Action | Result |
| --- | --- |
| Left click a block | Drill into it (click the focused column to go back up) |
| Breadcrumb button | Jump to that ancestor |
| Backspace / Esc | Go up one level (Esc at the root quits) |
| Right click | Open in file manager / copy path |
| Ctrl+R | Rescan |
| Ctrl+O | Pick another directory |

## Status

Early MVP. Works end-to-end; rough edges expected on very large trees (the
whole `du` output is held in memory as a Python object graph).
