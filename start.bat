@echo off
chcp 65001 > nul

echo Запуск Network Testing Tool...
echo.

:: Переходим в директорию скрипта
cd /d "%~dp0"
echo Текущая директория: %CD%
echo.

:: Проверяем права администратора
echo Проверка прав администратора...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Требуются права администратора!
    echo Пожалуйста, запустите программу от имени администратора.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
echo Права администратора подтверждены.
echo.

:: Проверяем наличие Docker
echo Проверка Docker...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker не найден!
    echo Пожалуйста, установите Docker Desktop.
    echo Скачать можно с https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo Docker найден.
echo.

:: Проверяем, запущен ли Docker
echo Проверка статуса Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker не запущен!
    echo Пожалуйста, запустите Docker Desktop и перезапустите этот скрипт.
    pause
    exit /b 1
)
echo Docker запущен.
echo.

:: Проверяем наличие docker-compose
echo Проверка docker-compose...
where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    echo docker-compose не найден!
    echo Пожалуйста, установите Docker Desktop.
    pause
    exit /b 1
)
echo docker-compose найден.
echo.

:: Проверяем наличие необходимых файлов
echo Проверка необходимых файлов...
if not exist "docker-compose.yml" (
    echo Ошибка: файл docker-compose.yml не найден!
    echo Текущая директория: %CD%
    pause
    exit /b 1
)
echo docker-compose.yml найден.

if not exist "Dockerfile" (
    echo Ошибка: файл Dockerfile не найден!
    echo Текущая директория: %CD%
    pause
    exit /b 1
)
echo Dockerfile найден.

if not exist "gui.py" (
    echo Ошибка: файл gui.py не найден!
    echo Текущая директория: %CD%
    pause
    exit /b 1
)
echo gui.py найден.
echo.

:: Проверяем, запущен ли X Server
tasklist /FI "IMAGENAME eq vcxsrv.exe" 2>NUL | find /I /N "vcxsrv.exe">NUL
if %errorlevel% neq 0 (
    echo Запуск X Server...
    start "" "C:\Program Files\VcXsrv\vcxsrv.exe" -multiwindow -clipboard -wgl -ac
    timeout /t 2 /nobreak >nul
)

:: Останавливаем существующие контейнеры
echo Остановка существующих контейнеров...
docker-compose down
timeout /t 2 /nobreak >nul

:: Запускаем контейнер
echo Запуск контейнера...
docker-compose up -d
if %errorlevel% neq 0 (
    echo Ошибка запуска контейнера!
    pause
    exit /b 1
)

:: Ждем запуска контейнера
echo Ожидание запуска контейнера...
timeout /t 5 /nobreak >nul

:: Запускаем GUI
echo Запуск графического интерфейса...
docker exec -e DISPLAY=host.docker.internal:0.0 -e QT_X11_NO_MITSHM=1 -e QT_DEBUG_PLUGINS=1 -e QT_STYLE_OVERRIDE=Fusion -e QT_QPA_PLATFORM=xcb -e LIBGL_ALWAYS_INDIRECT=1 network-test python3 gui.py
if %errorlevel% neq 0 (
    echo Ошибка запуска GUI!
    pause
    exit /b 1
)

:: Останавливаем контейнер после закрытия GUI
echo Остановка контейнера...
docker-compose down

echo Приложение остановлено.
pause 