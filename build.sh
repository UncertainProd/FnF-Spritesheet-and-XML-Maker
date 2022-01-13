#!/bin/sh
echo building
pip install -r requirements.txt
pip install pyinstaller
cd src
pyinstaller xmlpngUI.py -w --onefile -n Spritesheet-and-XML-Maker
echo finished building
