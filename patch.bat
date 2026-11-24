@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
set "UPD=%USERPROFILE%\Documents\Rozvidka\update"

echo.
echo  rozvedka 5.0.4 - local patch
echo.

if not exist "%UPD%\app-5.0.4.asar" (
    echo  сначала установи Rozvedka-Setup-5.0.4.exe
    echo  потом запусти patch.bat снова
    echo.
    pause
    exit /b 1
)

where python >nul 2>nul
if not errorlevel 1 goto :usepython

where py >nul 2>nul
if not errorlevel 1 goto :usepy

if exist "ready\app-5.0.4.asar" goto :useready

echo  python не найден, и готового asar нет
echo  поставь python 3.8+ (галочка add to path) и повтори
echo.
pause
exit /b 1

:usepython
python patcher.py
goto :check

:usepy
py -3 patcher.py
goto :check

:useready
if not exist "%UPD%\app-5.0.4.asar.orig" copy /y "%UPD%\app-5.0.4.asar" "%UPD%\app-5.0.4.asar.orig" >nul
copy /y "ready\app-5.0.4.asar" "%UPD%\app-5.0.4.asar" >nul
if errorlevel 1 (
    echo  не смог скопировать ready asar
    pause
    exit /b 1
)
echo  ready asar установлен

:check
if errorlevel 1 (
    echo.
    echo  патч не встал, смотри текст выше
    pause
    exit /b 1
)

echo.
echo  готово, запускаю...
start "" "%LOCALAPPDATA%\Programs\Rozvedka\Rozvidka.exe"
exit /b 0
