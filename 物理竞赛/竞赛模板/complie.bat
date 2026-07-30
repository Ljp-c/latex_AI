@echo off
REM 编译脚本：XeLaTeX 编译参赛项目说明书
REM ============================================

set MAIN=main

echo [1/2] XeLaTeX 第一次编译...
xelatex -synctex=1 -interaction=nonstopmode %MAIN%.tex
if %errorlevel% neq 0 (
    echo 编译出错！请查看 %MAIN%.log
    pause
    exit /b %errorlevel%
)

echo [2/2] XeLaTeX 第二次编译（交叉引用）...
xelatex -synctex=1 -interaction=nonstopmode %MAIN%.tex
if %errorlevel% neq 0 (
    echo 编译出错！请查看 %MAIN%.log
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo  编译完成！输出文件: %MAIN%.pdf
echo ========================================

REM 清理辅助文件（可选，取消下行注释以启用）
REM del /q %MAIN%.aux %MAIN%.log %MAIN%.out %MAIN%.toc %MAIN%.synctex.gz 2>nul

pause
