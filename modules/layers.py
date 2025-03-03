— A guide to the Forgotten Realms, describing how to create a custom dungeon module. What You Need: D&D 5e, a.docx file containing the code, the D&D 5e rules, the MUD map, the D&D 5e character sheet, and the D&D player character. An optional MUD map and text file also supplied. Instructions: Use a new computer with Python, or you can download and print the original file using a text editor (eg. Notepad). The MUD map file contains all dungeons in the Forgotten Realms (in alphabetical order).
Create a MUD map
Install Python
Install D&D 5e rules
Download the MUD image
Open the MUD application with Python
Type "import d6; print d6" with your new MUD character's name
Run the game
You may think the MUD module and code together look like this. It does, it does. But in reality not all code files are created equal. It turns out that you need to find the source for each module, map and rule. This guide will show you the source, and where you can find it, for each in-game module that you need to create something. If you want to learn the full scope of things you might want to buy a book on Modular Programming. It will do most of the heavy lifting for you. What You Will Need : Python (or other 3rd party Python/numpy/miphella compatible tool for your computer)
A notebook, pen or pencil
A blank copy of the book
Directories and files containing source code files (especially D7.txt + 5e sources (i.e. rules))
A copy of MUD server files (or your own server files)
A copy of the game client
Python: For example, if you were creating a file that looks like this :
python -m cgi -o file.xml
I would use cgi in this situation: cgi (python version 3.4.2)
This will use all the extra files in your'source' folder. You can always install your own server files from somewhere, but if you want to just download them for offline use you probably will not need them. And if you have files from your own server then you better make use of the 'raw' folder. You can open that from any text editor for easy referencing and saving. The client code files are listed to your