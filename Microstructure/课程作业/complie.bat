@echo off
REM ============================================================
REM 《显微结构分析》课程作业编译脚本
REM 用法：complie.bat           编译 main.tex
REM       complie.bat --view    编译完成后打开 main.pdf
REM ============================================================
setlocal
cd /d "%~dp0"

where xelatex >nul 2>nul
if errorlevel 1 (
  if exist "E:\latex_AI\TexLive\bin\windows\xelatex.exe" (
    set "PATH=E:\latex_AI\TexLive\bin\windows;%PATH%"
  ) else (
    echo 未找到 xelatex，请确认 TeX Live 已安装并加入 PATH。
    exit /b 1
  )
)

echo [1/2] xelatex main.tex ...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error main.tex >nul
if errorlevel 1 (
  echo 编译失败，请检查 main.log。
  exit /b 1
)

echo [2/2] xelatex main.tex ...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error main.tex >nul
if errorlevel 1 (
  echo 编译失败，请检查 main.log。
  exit /b 1
)

del /f /q main.aux main.log main.out main.toc >nul 2>nul
echo 编译成功: main.pdf
if "%~1"=="--view" start "" main.pdf
exit /b 0
