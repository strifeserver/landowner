@echo off
echo ============================================
echo MerchantCMS Build Script
echo ============================================
echo.
echo Attempting to close any running MerchantCMS instances...
taskkill /F /IM MerchantCMS.exe /T 2>nul
echo.
echo IMPORTANT: Please close any File Explorer windows showing the dist folder.
echo.
pause


echo Cleaning old build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo Building application...
pyinstaller MerchantCMS.spec

echo.
echo Copying database...
xcopy /E /I /Y data dist\MerchantCMS\data

echo.
echo ============================================
echo Build Complete!
echo ============================================
echo Executable: dist\MerchantCMS\MerchantCMS.exe
echo.
pause
