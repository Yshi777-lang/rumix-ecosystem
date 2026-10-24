---
name: rumix-build
description: Сборка APK Rumix через GitHub Actions. Используй, когда нужно собрать новый APK, обновить версию или запушить изменения.
---

# Rumix Build

Навык для сборки APK Rumix через GitHub Actions.

## Когда использовать

- Когда нужно собрать новый APK.
- Когда нужно обновить версию.
- Когда нужно запушить изменения в GitHub.

## Шаги

1. Проверь версию в `app/build.gradle`:
   `grep -n "versionCode\|versionName" app/build.gradle`

2. Обнови версию (если нужно).
3. Запушь изменения.
4. Дождись сборки на GitHub Actions.
5. Скачай APK из Artifacts.
6. Подпиши APK через SignYourApk.
7. Установи APK на устройство.

## Ссылки

- Репозиторий: https://github.com/Yshi777-lang/rumix
- Ветка: `My-love-Tiamat`
