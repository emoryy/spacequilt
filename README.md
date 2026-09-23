# SpaceQuilt

A modern, minimal disk-usage viewer with two classic visualisations that
nothing on Linux carries forward today:

- the **icicle** view of [xdiskusage](https://xdiskusage.sourceforge.net/):
  horizontal, size-proportional columns you click to drill into (the same
  interaction model as the Android *DiskUsage* app);
- the **boxes** view of SpaceMonger: every directory a titled box with its
  children packed inside, recursively, so a whole volume reads as one nested
  map.

Both share the tree, colours, drill-down and zoom, and switch live. Built on
Qt6 (PySide6) so it looks and themes like a current desktop app.

Like the original xdiskusage, it doesn't implement its own filesystem walker,
it parses the output of `du` (`du -k --all`), which is fast, correct, and
already handles the awkward parts (hardlinks, sparse files, block accounting).

## Requirements

- Python 3
- PySide6 (`pip install --user PySide6`, or your distro's `pyside6` package)
- `du` (coreutils)

## Usage

```sh
spacequilt [PATH] [-X/--cross-filesystems] [--colors SCHEME]
```

- `PATH`: directory to scan. Without it the window opens on a page listing
  the mounted volumes (device, filesystem, usage bar) and recent scans, with a
  *Browse for a folder…* button for anything else; *Open…* (Ctrl+O) brings
  that page back at any time
- `-x`, `--one-filesystem`: stop at mount points (`du -x`). **This is the
  default**, so scanning `/` measures the root filesystem itself instead of
  descending into every mounted disk, `/proc`, `/sys` and so on.
- `-X`, `--cross-filesystems`: descend into other mounted filesystems too
- `--view icicle|boxes`: start in the icicle columns or the SpaceMonger-style
  nested boxes; remembered, and the toolbar buttons (Ctrl+1 / Ctrl+2) switch
  live, keeping the current focus
- `--colors branches|levels|rainbow`: colour scheme; the choice is
  remembered, and the toolbar's *Colors* menu switches it live
- `--style flat|raised|deep`: relief of the blocks. *Raised* (default) gives a
  light top/left edge, a dark bottom/right edge, a soft gradient and, in the
  boxes view, sunken content areas, a nod to SpaceMonger's tiles; *deep* is
  the same twice as strong. Remembered too; the toolbar's *Style* menu is the
  same switch

Window size, maximised state and screen are remembered between runs.

### Colour schemes

| Scheme | Look |
| --- | --- |
| `branches` (default) | Each top-level entry of the focused node gets its own hue; deeper levels inherit it and get lighter, with a small per-path lightness jitter so siblings stay distinguishable |
| `levels` | SpaceMonger's flat pastels: one colour per depth (counted from the scanned root), cycling salmon, yellow, green, cyan, lavender, magenta, grey |
| `rainbow` | Every level spreads the hues over the wheel again, starting at the parent's hue, so the largest child matches its parent and its siblings fan out from there |

The `N smaller items` blocks are the unresolved part of their branch and
look like it: the branch's colour, slightly muted, under a dot stipple, the
way SpaceMonger 2 drew what was too small to lay out.

The toolbar has a *One filesystem* toggle (Ctrl+M) that flips this and
rescans, so a single window can switch between "this drive only" and
"everything under this path".

While `du` runs, an overlay shows how many entries have been read and which
directory is being walked. The bar is a real percentage when a target is
known: the volume's used inode count for a mount-point scan, or the entry
count of the previous scan of the same path (remembered between runs).
Otherwise it sweeps indeterminately. On a rescan the old tree stays visible,
dimmed, under the overlay.

When the scanned path is a mount point (and the scan stays on one
filesystem), the tree is wrapped in a *disk* node: the first column shows the
device, and next to the scanned directory a **Free space** block shows what
the volume has left, SpaceMonger style. The status bar then reports total,
used and free space for the volume.

### Desktop integration

```sh
./install-desktop.sh            # undo with --uninstall
```

Installs a `.desktop` entry and symlinks `spacequilt.svg` into the icon theme,
both pointing back at this checkout. Wayland compositors resolve a window's
icon through its desktop id rather than from the window itself, so without the
entry the task bar falls back to a generic placeholder. The entry also
registers `inode/directory`, so folders get a *Open with SpaceQuilt* action.

### Interaction

| Action | Result |
| --- | --- |
| Wheel | Zoom continuously around the cursor |
| Shift + wheel | Icicle: zoom vertically only (sizes) |
| Ctrl + wheel | Icicle: zoom horizontally only (depth) |
| Ctrl+1 / Ctrl+2 | Switch to the icicle / boxes view |
| Drag (left or middle) | Pan the view |
| Left click a block | Select it (path and size go to the status bar) |
| Double click a block | Drill into it, animated (double click the focused column to go up) |
| 0 / Ctrl+0 | Fit the view back to the focused node (animated) |
| Breadcrumb button | Jump to that ancestor |
| Backspace / Esc | Go up one level |
| Esc during a scan / Cancel or Stop button | Cancel the scan; whatever was shown before stays |
| Ctrl+O | Volumes / recent / browse page |
| Right click | Open in file manager / copy path |
| Ctrl+R | Rescan |
| Ctrl+O | Pick another directory |
| Ctrl+M | Toggle staying on one filesystem (rescans) |

In the boxes view a directory shows a title bar (name left, size right) when
there is room, and its children are packed inside by a squarified treemap;
files and too-small directories get a centred label. Each directory's layout
gives every entry its place and is decided once; zooming only scales it, so
nothing rearranges as you zoom: the screen size decides what is drawn, not
where it goes. Whatever is too small to draw shows as the parent's dotted
area, the way SpaceMonger 2 drew unresolved content, and resolves entry by
entry as you zoom in. The smallest boxes are capped at a few thousand per
frame, so the map stays fluid on a large screen.

Zooming out stops at the fit, and panning stops where the content ends: below
the fit or beyond the edge there is nothing more to see. Zoom is
continuous, not a set of discrete levels: the layout is recomputed in
screen pixels every frame, so zooming in genuinely subdivides deeper levels
(and breaks up the `N smaller items` aggregate blocks) instead of magnifying
what is already drawn. Drilling in with a double click still exists: the view
zooms until the block fills the window, then the focus switches and the
viewport is the fit of the node you jumped to. Going up plays the same
motion backwards.

## Status

Early MVP. Works end-to-end; rough edges expected on very large trees (the
whole `du` output is held in memory as a Python object graph).
