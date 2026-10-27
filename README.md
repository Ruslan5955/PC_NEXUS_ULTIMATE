# PC NEXUS ULTIMATE

Многофункциональная Python-утилита для Windows 10/11: Gaming Center, обзор системы, очистка временных файлов, Hardware Lab, диагностика сети, Windows Toolkit, Privacy Center и Secret Room.

## Возможности
- Системная сводка: ОС, CPU, RAM, свободное место на системном диске, видеокарта.
- Gaming: быстрые переходы к Game Mode, графическим настройкам, питанию, герцовке, Game Bar и автозагрузке.
- Очистка: анализ и очистка временной папки текущего пользователя с подтверждением.
- Hardware: диспетчер устройств, дисков, DirectX, монитор ресурсов, отчёт батареи.
- Сеть: ping, DNS lookup, ipconfig, очистка DNS-кэша и защищённый подтверждением сброс Winsock.
- Windows: SFC, DISM CheckHealth, службы, журналы, планировщик, восстановление и обновления.
- Приватность: ссылки на разрешения камеры/микрофона/местоположения и настройки защиты.
- Secret Room: God Mode, экспорт отчёта, системные папки и пасхалка.
- Логи: `%APPDATA%\\PCNexus\\pc_nexus.log`.

## Запуск
Нужны Windows 10/11 и Python 3.10+.

```powershell
py -m pip install -r requirements.txt
py .\\pc_nexus\\main.py
```

## Сборка EXE
```powershell
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name PC-NEXUS-ULTIMATE pc_nexus\\main.py
```
EXE появится в `dist`.

## GitHub
Создай пустой репозиторий на GitHub, затем из папки проекта:

```powershell
git init
git add .
git commit -m "Release PC NEXUS ULTIMATE 2.0"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/pc-nexus-ultimate.git
git push -u origin main
```

## Важно
- Программа не отключает Defender, UAC, Windows Update или брандмауэр.
- Очистка ограничена временной папкой текущего пользователя и требует подтверждения.
- Сброс Winsock меняет сетевую конфигурацию; может потребоваться перезагрузка и перенастройка VPN.
- SFC/DISM и некоторые оснастки требуют прав администратора.
- Прирост FPS не гарантируется; безопасные настройки и результат зависят от системы.
- Температуры компонентов требуют совместимого источника датчиков и в этой версии напрямую не считываются.
