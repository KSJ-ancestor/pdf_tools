@echo off

## pip install pyinstaller

cls 
echo ---------------------------
echo Compile Target
echo ---------------------------
echo 1: All
echo 2: English
echo 3: Korean
echo 0: Exit
echo ---------------------------
set /p choice=choose one (1, 2, 3 or 0): 


set Target=%choice%

if "%choice%"=="0" (
    set Target=Nothing
    goto end
)

if "%choice%"=="1" (
    set Target=All
    goto all
)

if "%choice%"=="2" (
    set Target=English
    goto eng
)

if "%choice%"=="3" (
    set Target=Korean
    goto kor
)

goto end

:all
echo.
echo -----------------------
echo compile Korean version
echo -----------------------
pyinstaller --clean pdf_tools_kr.spec

:eng
echo.
echo -----------------------
echo compile English version
echo -----------------------
pyinstaller --clean pdf_tools_en.spec
goto end

:kor
echo.
echo -----------------------
echo compile Korean version
echo -----------------------
pyinstaller --clean pdf_tools_kr.spec
goto end


:end
echo.
echo -----------------------
echo %Target% is done.
echo -----------------------
echo.
pause