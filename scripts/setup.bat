@echo off
chcp 65001 > nul

:: Переходим в директорию скрипта
cd /d "%~dp0\.."
echo Текущая директория: %CD%
echo.

echo Проверка и настройка окружения для Network Testing Tool...
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

:: Проверяем и устанавливаем VcXsrv
echo Проверка X Server...
where vcxsrv >nul 2>&1
if %errorlevel% neq 0 (
    echo Установка VcXsrv...
    echo Скачивание установщика...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://sourceforge.net/projects/vcxsrv/files/latest/download' -OutFile 'vcxsrv.exe'}"
    
    if not exist "vcxsrv.exe" (
        echo Ошибка: Не удалось скачать установщик VcXsrv!
        echo Пожалуйста, скачайте и установите VcXsrv вручную с https://sourceforge.net/projects/vcxsrv/
        pause
        exit /b 1
    )
    
    echo Установка...
    echo Пожалуйста, следуйте инструкциям установщика...
    start /wait "" "vcxsrv.exe"
    del vcxsrv.exe
    
    echo Настройка автозапуска...
    if exist "C:\Program Files\VcXsrv\vcxsrv.exe" (
        powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\XServer.lnk'); $Shortcut.TargetPath = 'C:\Program Files\VcXsrv\vcxsrv.exe'; $Shortcut.Arguments = '-multiwindow -clipboard -wgl -ac'; $Shortcut.Save()}"
    ) else (
        echo Предупреждение: VcXsrv не установлен в стандартную директорию.
        echo Пожалуйста, настройте автозапуск вручную.
    )
) else (
    echo VcXsrv уже установлен.
)

:: Проверяем и устанавливаем Docker
echo.
echo Проверка Docker...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker не найден. Установка Docker Desktop...
    echo Скачивание установщика...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe' -OutFile 'DockerDesktopInstaller.exe'}"
    
    echo Установка Docker Desktop...
    start /wait DockerDesktopInstaller.exe install --quiet
    del DockerDesktopInstaller.exe
    
    echo.
    echo Docker Desktop установлен.
    echo Пожалуйста, запустите Docker Desktop и перезагрузите компьютер.
    echo После перезагрузки запустите этот скрипт снова.
    pause
    exit /b
) else (
    echo Docker найден.
)

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

:: Проверяем наличие необходимых файлов
echo Проверка файлов проекта...
if not exist "docker\docker-compose.yml" (
    echo Ошибка: файл docker-compose.yml не найден!
    pause
    exit /b 1
)
if not exist "docker\Dockerfile" (
    echo Ошибка: файл Dockerfile не найден!
    pause
    exit /b 1
)
if not exist "src\gui.py" (
    echo Ошибка: файл gui.py не найден!
    pause
    exit /b 1
)
echo Все необходимые файлы найдены.
echo.

:: Проверяем и останавливаем существующие контейнеры
echo Проверка существующих контейнеров...
docker ps --filter "name=network-test" --format "{{.Names}}" | findstr "network-test" >nul
if %errorlevel% equ 0 (
    echo Остановка существующего контейнера...
    cd docker
    docker-compose down
    cd ..
    timeout /t 2 /nobreak >nul
)
echo.

:: Проверяем и настраиваем X Server
echo Проверка X Server...
tasklist /FI "IMAGENAME eq vcxsrv.exe" 2>NUL | find /I /N "vcxsrv.exe">NUL
if %errorlevel% neq 0 (
    echo Запуск X Server...
    start "" "C:\Program Files\VcXsrv\vcxsrv.exe" -multiwindow -clipboard -wgl -ac
    timeout /t 2 /nobreak >nul
)
echo.

:: Проверяем и настраиваем переменные окружения
echo Настройка переменных окружения...
setx DISPLAY "host.docker.internal:0.0" /M
echo.

:: Проверяем и настраиваем файрвол
echo Настройка файрвола...
netsh advfirewall firewall show rule name="X Server" >nul 2>&1
if %errorlevel% neq 0 (
    echo Добавление правил файрвола...
    netsh advfirewall firewall add rule name="X Server" dir=in action=allow program="C:\Program Files\VcXsrv\vcxsrv.exe" enable=yes
    netsh advfirewall firewall add rule name="X Server" dir=out action=allow program="C:\Program Files\VcXsrv\vcxsrv.exe" enable=yes
)
echo.

echo Настройка завершена!
echo.
echo Теперь вы можете запустить scripts\start.bat для запуска приложения.
echo.
pause 