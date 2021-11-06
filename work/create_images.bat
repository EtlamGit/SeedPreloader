@ECHO OFF

REM set path to your Minutor exectable
SET minutor="minutor.exe"

FOR /D %%G IN (*) DO (
  ECHO %%G

  IF NOT EXIST "%%~nG.png" (
    %minutor% --world "%%~nG\world"    --savePNG "%%~nG.png"
  )

  IF NOT EXIST "%%~nG Biome.png" (
    %minutor% --world "%%~nG\world" -B --savePNG "%%~nG Biome.png"
  )
)

PAUSE
