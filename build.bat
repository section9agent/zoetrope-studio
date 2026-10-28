@echo off
REM ============================================================
REM  Vinyl Zoetrope Designer — Windows build script
REM  Run this once from inside the vinyl_zoetrope folder.
REM  Requires Python 3.10+ on PATH (python.org installer).
REM ============================================================

echo === Vinyl Zoetrope Designer — Windows build ===
echo.

REM -- Create / activate a virtual environment -----------------
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

REM -- Install dependencies ------------------------------------
echo Installing dependencies...
pip install --upgrade pip --quiet
pip install PyQt6 Pillow pyinstaller --quiet

REM -- Build ---------------------------------------------------
echo.
echo Building standalone executable...
pyinstaller zoetrope_studio.spec --clean --noconfirm

echo.
if exist "dist\VinylZoetrope\VinylZoetrope.exe" (
    echo BUILD SUCCESSFUL
    echo Executable: dist\VinylZoetrope\VinylZoetrope.exe
    echo.
    echo To distribute: zip the entire dist\VinylZoetrope\ folder.
) else (
    echo BUILD FAILED — check output above for errors.
)

pause
