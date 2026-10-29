#!/data/data/com.termux/files/usr/bin/bash
W=~/Work
toast() { timeout 2 termux-toast "$1" 2>/dev/null; }
case $1 in
  1) cat $W/notes/notes.txt ;;
  2) if timeout 2 termux-clipboard-set < $W/notes/notes.txt 2>/dev/null; then
       toast "✅ Copied!"
     else
       echo "API спит. Открой notes.txt в редакторе и скопируй вручную."
     fi ;;
  3) cd $W && git add -A && git commit -m "update" && git push origin main && toast "✅ Push done!" ;;
  4) > $W/notes/notes.txt; toast "🗑 Cleared" ;;
  *) echo "1-view 2-copy 3-push 4-clear" ;;
esac
