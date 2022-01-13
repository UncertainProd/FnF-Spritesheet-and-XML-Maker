@ECHO OFF
ECHO building tool...
pip install -r requirements.txt
pip install pyinstaller
cd ..
cd src
pyinstaller xmlpngUI.py --onefile -w -n Spritesheet-and-XML-Maker
echo done building
PAUSE
