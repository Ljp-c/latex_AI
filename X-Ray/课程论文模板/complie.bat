@echo off
REM ============================================================
REM 《X 射线晶体学》课程论文模板（LaTeX 版）编译脚本
REM 使用 XeLaTeX 连续编译两遍（本模板无参考文献）；
REM 用法：complie.bat            编译 main.tex
REM       complie.bat main      编译指定主文件（不含扩展名）
REM       complie.bat main --view   编译完成后打开 PDF
REM ============================================================
setlocal
set "TEX_FILE=%~1"
if "%TEX_FILE%"=="" set TEX_FILE=main.tex
if not exist "%TEX_FILE%" (
  echo 找不到源文件: %TEX_FILE%
  exit /b 1
)
for %%F in ("%TEX_FILE%") do set "BASE_NAME=%%~nF"

where xelatex >nul 2>nul
if errorlevel 1 (
  echo 未找到 xelatex，请确认 TeX Live 已加入 PATH
  exit /b 1
)

for /l %%I in (1,1,2) do (
  echo [%%I/2] xelatex %TEX_FILE% ...
  xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%"
  if errorlevel 1 (
    echo 编译失败，请检查 %BASE_NAME%.log
    exit /b 1
  )
)

del /f /q "%BASE_NAME%.aux" "%BASE_NAME%.log" "%BASE_NAME%.out" "%BASE_NAME%.toc" >nul 2>nul
echo 编译成功: %BASE_NAME%.pdf
if "%~2"=="--view" start "" "%BASE_NAME%.pdf"
exit /b 0
