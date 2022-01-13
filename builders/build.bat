@ECHO OFF
ECHO building tool...
cd ..
pip install -r requirements.txt
pip install pyinstaller
cd src
pyinstaller xmlpngUI.py --onefile -w -n Spritesheet-and-XML-Maker -i assets/appicon.ico
echo done building
PAUSE
