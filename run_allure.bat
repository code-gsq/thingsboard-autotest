@echo off
rem 一键跑完测试并生成/打开 Allure 报告
chcp 65001 >nul
cd /d %~dp0

echo [1/3] Running all tests...
python -m pytest --alluredir=reports/allure-results
if errorlevel 1 (
    echo.
    echo Tests failed. See output above.
    pause
    exit /b 1
)

echo [2/3] Generating Allure report...
allure generate reports/allure-results -o reports/allure-report --clean

echo [3/3] Opening report...
allure open reports/allure-report
pause
