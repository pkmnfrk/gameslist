@ECHO OFF

SET SEVENZ=C:\Program Files\7-Zip\7z.exe
DEL /f gamelist.zip

"%SEVENZ%" a gamelist.zip requirements.txt *.py *.json *.css *.bat
"%SEVENZ%" a -r gamelist.zip images