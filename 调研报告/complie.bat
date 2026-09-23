@echo off
REM 增强版编译脚本（Windows 版）
REM 支持：自动检测编译器、错误重试、PDF预览

setlocal enabledelayedexpansion

REM 默认主文件
set "TEX_FILE=%~1"
if "%TEX_FILE%"=="" set TEX_FILE=main.tex
if not exist "%TEX_FILE%" (
  echo ⚠️  找不到源文件: %TEX_FILE%
  exit /b 1
)
for %%F in ("%TEX_FILE%") do set "BASE_NAME=%%~nF"

REM 检测编译器
set "COMPILER=pdflatex"
findstr /i /c:"documentclass" /c:"usepackage" "%TEX_FILE%" | findstr /i /c:"ctex" /c:"xeCJK" /c:"fontspec" >nul && set "COMPILER=xelatex"
findstr /i /c:"usepackage" "%TEX_FILE%" | findstr /i /c:"luatex" >nul && set "COMPILER=lualatex"
where %COMPILER% >nul 2>nul
if errorlevel 1 (
  echo ⚠️  未找到 %COMPILER% ，请确认已安装并加入 PATH
  exit /b 1
)
echo 检测到使用 %COMPILER% 编译器

REM 编译函数
set "MAX_ATTEMPTS_DEFAULT=3"
goto :main
:compile_loop
set "ATTEMPT=1"
set "MAX_ATTEMPTS=%~1"
if "%MAX_ATTEMPTS%"=="" set "MAX_ATTEMPTS=%MAX_ATTEMPTS_DEFAULT%"
:compile_attempt
echo 编译尝试 !ATTEMPT!/%MAX_ATTEMPTS% ...
%COMPILER% -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%"
if not errorlevel 1 exit /b 0
set /a ATTEMPT+=1
if !ATTEMPT! LEQ %MAX_ATTEMPTS% goto compile_attempt
echo 编译失败，请检查错误信息
exit /b 1

:main
REM 主流程
echo 📄 编译文档: %TEX_FILE%
set "EXIT_CODE=0"

REM 第一次编译
call :compile_loop %MAX_ATTEMPTS_DEFAULT%
if errorlevel 1 exit /b 1

REM 处理参考文献
set "NEED_BIB="
set "BIB_OK="
set "BIB_FAILED="
set "BIB_TMP="
set "BIB_TMP_CREATED="
if exist "%BASE_NAME%.bcf" (set "BCF_EXIST=1") else (set "BCF_EXIST=0")
if exist "%BASE_NAME%.aux" (set "AUX_EXIST=1") else (set "AUX_EXIST=0")
if %BCF_EXIST%==1 (set "NEED_BIB=1")
if %AUX_EXIST%==1 (set "NEED_BIB=1")
if not defined NEED_BIB goto skip_bib

set "ORIG_TEMP=%TEMP%"
set "ORIG_TMP=%TMP%"
set "BIB_TMP=%CD%\.tmp"
if not exist "%BIB_TMP%" (
  mkdir "%BIB_TMP%"
  set "BIB_TMP_CREATED=1"
)
set "TEMP=%BIB_TMP%"
set "TMP=%BIB_TMP%"

where biber >nul 2>nul && (echo 📚 处理参考文献 ^(Biber^)... & biber "%BASE_NAME%" && set "BIB_OK=1")
if errorlevel 1 (
  where bibtex >nul 2>nul && (echo 📚 处理参考文献 ^(BibTeX^)... & bibtex "%BASE_NAME%" && set "BIB_OK=1")
)
if defined ORIG_TEMP set "TEMP=%ORIG_TEMP%"
if defined ORIG_TMP set "TMP=%ORIG_TMP%"
if not defined BIB_OK (
  set "BIB_FAILED=1"
  set "EXIT_CODE=2"
  echo 参考文献处理失败，跳过后续编译
  goto skip_bib
)

REM 后续编译
call :compile_loop 1
if errorlevel 1 exit /b 1
call :compile_loop 1
if errorlevel 1 exit /b 1
:skip_bib

REM 清理文件
echo 🧹 清理中间文件...
call :cleanup

if defined BIB_FAILED (
  echo ⚠️  编译完成，但参考文献处理失败: %BASE_NAME%.pdf
) else (
  echo ✅ 编译成功: %BASE_NAME%.pdf
)

REM 自动打开PDF
if "%2"=="--view" goto open_pdf
if "%2"=="-v" goto open_pdf
exit /b %EXIT_CODE%

:cleanup
for %%E in (aux log bbl bcf blg run.xml toc out lof lot nav snm vrb) do (
  if exist "%BASE_NAME%.%%E" del /f /q "%BASE_NAME%.%%E"
)
for /d %%D in (_minted-*) do if exist "%%D" rd /s /q "%%D"
if defined BIB_TMP_CREATED if exist "%BIB_TMP%" rd /s /q "%BIB_TMP%"
goto :eof

:open_pdf
if exist "%BASE_NAME%.pdf" (
  start "" "%BASE_NAME%.pdf"
) else (
  echo ⚠️  无法自动打开PDF，请手动查看
)
exit /b %EXIT_CODE%
