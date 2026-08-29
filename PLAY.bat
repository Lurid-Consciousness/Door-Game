@echo off
title NO FIXED SHAPE
where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0no_fixed_shape.py"
) else (
    python "%~dp0no_fixed_shape.py"
)
echo.
pause
