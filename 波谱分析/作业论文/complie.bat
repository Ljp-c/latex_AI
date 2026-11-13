@echo off
setlocal
set "TEX_FILE=%~1"
if "%TEX_FILE%"=="" set "TEX_FILE=main.tex"
if not exist "%TEX_FILE%" if exist "%TEX_FILE%.tex" set "TEX_FILE=%TEX_FILE%.tex"
if not exist "%TEX_FILE%" (
  echo Source file not found: %TEX_FILE%
  exit /b 1
)
for %%F in ("%TEX_FILE%") do set "BASE_NAME=%%~nF"

set "TEXBIN=E:\latex_AI\TexLive\bin\windows"
if exist "%TEXBIN%\xelatex.exe" set "PATH=%TEXBIN%;%PATH%"

where xelatex >nul 2>nul
if errorlevel 1 goto no_tex

echo [1/4] xelatex %TEX_FILE% ...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 goto fail

if not exist "%BASE_NAME%.bcf" goto final_pass

echo [2/4] biber %BASE_NAME% ...
set "BIB_TMP=%PUBLIC%\latex_tmp"
if not exist "%BIB_TMP%" mkdir "%BIB_TMP%"
set "TEMP=%BIB_TMP%"
set "TMP=%BIB_TMP%"
biber "%BASE_NAME%"
if errorlevel 1 goto bib_fail

echo [3/4] xelatex %TEX_FILE% ...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 goto fail

:final_pass
echo [4/4] xelatex %TEX_FILE% ...
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "%TEX_FILE%" >nul
if errorlevel 1 goto fail

del /f /q "%BASE_NAME%.aux" "%BASE_NAME%.log" "%BASE_NAME%.out" "%BASE_NAME%.toc" "%BASE_NAME%.bbl" "%BASE_NAME%.bcf" "%BASE_NAME%.blg" "%BASE_NAME%.run.xml" >nul 2>nul
echo Done: %BASE_NAME%.pdf
exit /b 0

:no_tex
echo xelatex not found. Check TeX Live and the TEXBIN path in this script.
exit /b 1

:bib_fail
echo Biber failed. See %BASE_NAME%.blg
exit /b 1

:fail
echo Compilation failed. See %BASE_NAME%.log
exit /b 1
