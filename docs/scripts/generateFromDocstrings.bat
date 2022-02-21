@echo OFF
if exist npdoc2md goto SCRIPTEXIST
git clone https://github.com/jwlodek/npdoc2md
:SCRIPTEXIST
cd npdoc2md
git pull
py npdoc2md.py -i ..\..\..\Open Horizon CUI -o ..\..\DocstringGenerated -s __main__.py