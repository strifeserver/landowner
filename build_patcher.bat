@echo off
echo ============================================
echo MerchantCMS Patcher Build Script
echo ============================================
echo.
echo Cleaning old patcher build...
rmdir /s /q build_patcher 2>nul
rmdir /s /q dist_patcher 2>nul

echo Building Patcher...
pyinstaller --onefile --windowed --name MerchantCMSPatcher --distpath ./dist_patcher --workpath ./build_patcher patcher.py

echo.
echo ============================================
echo Build Complete!
echo Executable: dist_patcher\MerchantCMSPatcher.exe
echo ============================================
echo.
pause
