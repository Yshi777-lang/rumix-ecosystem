#!/data/data/com.termux/files/usr/bin/bash
# show-map.sh — открыть карту дома (RUMIX_MAP.md)
MAP="$HOME/Work/notes/CORE/RUMIX_MAP.md"
if [ -f "$MAP" ]; then
  less "$MAP"
else
  echo "❌ Карта не найдена: $MAP"
fi
