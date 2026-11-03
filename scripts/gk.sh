#!/data/data/com.termux/files/usr/bin/bash
W="$HOME/Work"
cd "$W" || exit 1
echo "== GIT KIT (дом) =="
echo "1 pull — скачать/синхронизировать"
echo "2 push ВСЁ — бэкап"
echo "3 push ОДИН файл"
echo "4 создать новый файл"
echo "5 перезаписать файл из локального"
echo "6 править файл + push"
echo "7 посмотреть файл"
echo "8 журнал"
echo "9 отменить последний коммит"
echo "0 статус"
echo "x выход (или просто Enter)"
read -r c
case "$c" in
1) git pull origin main ;;
2) git add -A && git commit -m "backup $(date +%d.%m_%H:%M)" && git push origin main ;;
3) echo "файл и сообщение:"; read -r f m; git add "$f" && git commit -m "${m:-update $f}" && git push origin main ;;
4) echo "имя файла:"; read -r f; mkdir -p "$(dirname "$f")"; touch "$f"; echo "создан: $f (наполни и выбери 3)" ;;
5) echo "локальный путь и цель в репо:"; read -r s d; mkdir -p "$(dirname "$W/$d")"; cp "$s" "$W/$d" && git add "$d" && git commit -m "overwrite $d" && git push origin main ;;
6) echo "файл:"; read -r f; nano "$f" && git add "$f" && git commit -m "edit $f" && git push origin main ;;
7) echo "файл:"; read -r f; cat "$f" ;;
8) git log --oneline -10 ;;
9) git reset --soft HEAD~1 && echo "коммит снят (изменения в индексе)" ;;
0) git status -s ;;
x|q|"") exit 0 ;;
*) echo "не знаю такой команды" ;;
esac
