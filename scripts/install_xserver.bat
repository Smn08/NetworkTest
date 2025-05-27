@echo off
echo Installing VcXsrv...

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator
    pause
    exit /b 1
)

:: Скачивание VcXsrv
powershell -Command "& {Invoke-WebRequest -Uri 'https://sourceforge.net/projects/vcxsrv/files/latest/download' -OutFile 'vcxsrv.exe'}"

:: Установка VcXsrv
echo Installing VcXsrv...
start /wait vcxsrv.exe /S

:: Создание ярлыка для автозапуска
echo Creating startup shortcut...
powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\XLaunch.lnk'); $Shortcut.TargetPath = 'C:\Program Files\VcXsrv\xlaunch.exe'; $Shortcut.Arguments = '-multiwindow -clipboard -wgl -ac'; $Shortcut.Save()}"

:: Запуск VcXsrv
echo Starting VcXsrv...
start "" "C:\Program Files\VcXsrv\xlaunch.exe" -multiwindow -clipboard -wgl -ac

echo Installation complete! Please restart your computer and run start.bat again.
pause 