@echo off
REM ============================================================
REM 课程论文模板项目编译脚本
REM XeLaTeX 编译，自动识别 biblatex 参考文献（paper.tex）并运行 biber
REM 用法：complie.bat                编译 main.tex（空白模板）
REM       complie.bat paper          编译 paper.tex（论文全文）
REM       complie.bat paper --view   编译完成后打开 PDF
REM ============================================================
setlocal
set "TEX_FILE=%~1"
if "%TEX_FILE%"=="" set TEX_FILE=main.tex
if not exist "%TEX_FILE%" if exist "%TEX_FILE%.tex" set "TEX_FILE=%TEX_FILE%.tex"
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

echo [1] xelatex %TEX_FILE% ...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 (
  echo 编译失败，请检查 %BASE_NAME%.log
  exit /b 1
)

if not exist "%BASE_NAME%.bcf" goto final_pass

echo [2] 处理参考文献（biber）...
set "BIB_TMP=%PUBLIC%\latex_tmp"
if not exist "%BIB_TMP%" mkdir "%BIB_TMP%"
set "TEMP=%BIB_TMP%"
set "TMP=%BIB_TMP%"
biber "%BASE_NAME%"
if errorlevel 1 (
  echo 参考文献处理失败，请检查 %BASE_NAME%.blg
  exit /b 1
)

echo [3] xelatex（第 2 遍）...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 (
  echo 编译失败，请检查 %BASE_NAME%.log
  exit /b 1
)
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 (
  echo 编译失败，请检查 %BASE_NAME%.log
  exit /b 1
)
goto done

:final_pass
echo [2] xelatex（第 2 遍）...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 (
  echo 编译失败，请检查 %BASE_NAME%.log
  exit /b 1
)

:done
del /f /q "%BASE_NAME%.aux" "%BASE_NAME%.log" "%BASE_NAME%.out" "%BASE_NAME%.toc" "%BASE_NAME%.bbl" "%BASE_NAME%.bcf" "%BASE_NAME%.blg" "%BASE_NAME%.run.xml" >nul 2>nul
echo 编译成功: %BASE_NAME%.pdf
if "%~2"=="--view" start "" "%BASE_NAME%.pdf"
exit /b 0
