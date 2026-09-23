@echo off
setlocal enabledelayedexpansion

REM 增强版编译脚本 (Windows 批处理)
REM 支持：自动检测编译器、错误重试、参考文献处理、PDF 预览

set TEX_FILE=%1
if "%TEX_FILE%"=="" set TEX_FILE=main.tex
set BASE_NAME=%~n1
if "%BASE_NAME%"=="" set BASE_NAME=main

REM 检测编译器
set COMPILER=pdflatex
findstr /i /c:"documentclass.*{ctex" "%TEX_FILE%" >nul
if not errorlevel 1 set COMPILER=xelatex
findstr /i /c:"usepackage.*{xeCJK" "%TEX_FILE%" >nul
if not errorlevel 1 set COMPILER=xelatex
findstr /i /c:"usepackage.*{fontspec" "%TEX_FILE%" >nul
if not errorlevel 1 set COMPILER=xelatex
findstr /i /c:"usepackage.*{luatex" "%TEX_FILE%" >nul
if not errorlevel 1 set COMPILER=lualatex

echo 检测到使用 %COMPILER% 编译器

REM 编译函数（通过标签实现）
call :compile_tex
if errorlevel 1 (
    echo 编译失败，请检查错误信息
    exit /b 1
)

REM 处理参考文献
if exist "%BASE_NAME%.bcf" (
    where biber >nul 2>&1
    if not errorlevel 1 (
        echo 处理参考文献 (Biber)...
        biber "%BASE_NAME%"
    )
) else if exist "%BASE_NAME%.aux" (
    where bibtex >nul 2>&1
    if not errorlevel 1 (
        echo 处理参考文献 (BibTeX)...
        bibtex "%BASE_NAME%"
    )
)

REM 如果需要参考文献，则再次编译
if exist "%BASE_NAME%.bcf" (
    echo 第二次编译...
    call :compile_tex
    echo 第三次编译...
    call :compile_tex
) else if exist "%BASE_NAME%.aux" (
    echo 第二次编译...
    call :compile_tex
    echo 第三次编译...
    call :compile_tex
)

REM 清理中间文件
echo 清理中间文件...
call :cleanup

echo 编译成功: %BASE_NAME%.pdf

REM 自动打开 PDF
if "%2"=="--view" goto open_pdf
if "%2"=="-v" goto open_pdf
goto :eof

:open_pdf
if exist "%BASE_NAME%.pdf" start "" "%BASE_NAME%.pdf"
exit /b

REM 编译函数（带重试）
:compile_tex
set attempt=1
set max_attempts=3
:compile_loop
if %attempt% gtr %max_attempts% (
    exit /b 1
)
echo 编译尝试 %attempt%/%max_attempts% ...
%COMPILER% -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%"
if not errorlevel 1 exit /b 0
set /a attempt+=1
timeout /t 1 /nobreak >nul
goto compile_loop

REM 清理函数
:cleanup
del /q "%BASE_NAME%.aux" "%BASE_NAME%.log" "%BASE_NAME%.bbl" "%BASE_NAME%.bcf" "%BASE_NAME%.blg" "%BASE_NAME%.run.xml" "%BASE_NAME%.toc" "%BASE_NAME%.out" "%BASE_NAME%.lof" "%BASE_NAME%.lot" "%BASE_NAME%.nav" "%BASE_NAME%.snm" "%BASE_NAME%.vrb" 2>nul
for /d %%i in (_minted-*) do rd /s /q "%%i" 2>nul
exit /b