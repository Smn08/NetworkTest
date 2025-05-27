@echo off
chcp 65001 > nul

echo Установка X Server для Windows...
echo.

:: Проверяем, установлен ли уже VcXsrv
where vcxsrv >nul 2>&1
if %errorlevel% equ 0 (
    echo VcXsrv уже установлен.
) else (
    echo Скачивание VcXsrv...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://sourceforge.net/projects/vcxsrv/files/latest/download' -OutFile 'vcxsrv.exe'}"
    
    echo Установка VcXsrv...
    start /wait vcxsrv.exe /S
    del vcxsrv.exe
)

:: Создаем ярлык для запуска X Server
echo Создание ярлыка для запуска X Server...
powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\XServer.lnk'); $Shortcut.TargetPath = 'C:\Program Files\VcXsrv\vcxsrv.exe'; $Shortcut.Arguments = '-multiwindow -clipboard -wgl -ac'; $Shortcut.Save()}"

echo.
echo X Server установлен и настроен.
echo Пожалуйста, перезагрузите компьютер и запустите start.bat снова.
echo.
pause 