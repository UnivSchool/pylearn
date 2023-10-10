@echo off

rem pylearn Windows packaging
tar cvf pypkg.tar -C src/packages/pyang-extra *.py plugins

copy pypkg.tar ..\..\..\venv\Lib\site-packages

echo.
echo Example:
echo	cd C:/repos/meta/ogroup/venv/Lib/site-packages/pyang
echo	tar xvf ..\pypkg.tar
