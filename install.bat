@echo off

set inkscape_ex="%APPDATA%\inkscape\extensions"
copy csv_to_vinyl.* "%inkscape_ex%"
copy roland.* "%inkscape_ex%"
pause