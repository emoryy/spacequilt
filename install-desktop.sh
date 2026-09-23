#!/usr/bin/env bash
# Register spacequilt with the desktop: a .desktop entry plus the icon, both
# pointing back at this checkout. Wayland compositors look the window icon up
# by desktop id (set with QGuiApplication::setDesktopFileName), so the entry is
# what makes the icon show up in the task bar and the launcher.
#
# Undo with: install-desktop.sh --uninstall
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data="${XDG_DATA_HOME:-$HOME/.local/share}"
entry="$data/applications/spacequilt.desktop"
icon="$data/icons/hicolor/scalable/apps/spacequilt.svg"

refresh() {
    update-desktop-database "$data/applications" 2>/dev/null || true
    gtk-update-icon-cache -qtf "$data/icons/hicolor" 2>/dev/null || true
    kbuildsycoca6 --noincremental 2>/dev/null || true
}

if [[ "${1:-}" == "--uninstall" ]]; then
    rm -f "$entry" "$icon"
    refresh
    echo "removed $entry"
    echo "removed $icon"
    exit 0
fi

mkdir -p "$(dirname "$entry")" "$(dirname "$icon")"
ln -sfn "$here/spacequilt.svg" "$icon"

cat > "$entry" <<EOF
[Desktop Entry]
Type=Application
Name=spacequilt
GenericName=Disk usage viewer
Comment=Icicle disk-usage view built on du
Exec="$here/spacequilt" %f
Icon=spacequilt
Terminal=false
Categories=Utility;Filesystem;
Keywords=disk;usage;space;du;icicle;
MimeType=inode/directory;
StartupWMClass=spacequilt
EOF

refresh
echo "installed $entry"
echo "installed $icon -> $here/spacequilt.svg"
