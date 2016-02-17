JSE
===

Joe's Script Editor - Python based standalone script editor for Autodesk Maya using maya.cmds aiming to address issues with the default script editor and enhance functionality

###_Curent status: Unstable pre-alpha_
* Many features that are listed in menus are not functional yet
* Saving file has some bugs
* Opening file is still WIP
* Many more...

Installation
===

1. Download as zip (button to the top right!)

2. Extract `JSE.py` from the downloaded zip and place into the folder (typically):

   (where `~` is your home directory/folder)  

- Windows: `C:\Users\YourUserName\Documents\maya\scripts`
- Mac OS X: `~/Library/Preferences/Autodesk/maya/scripts`
- Linux: `~/maya/scripts` 

or wherever you Maya scripts folder may be


Launching it (Simple)
===

3. Open Maya
4. Run in Maya script editor (in Python)
```python
import JSE
JSE.run()
```

---
I **highly suggest** you check out the **wiki links below** for more configuration options for a faster/more intuitive launch in the future

* [Shelf Item](https://github.com/j0yu/JSE/wiki/Shelf-Item)
* [Keyboard Shortcuts](https://github.com/j0yu/JSE/wiki/Keyboard-Shortcut)

Usage
===

The editor is completely right-mouse button, menu based at the moment:

Hold...     | Menu Type                  | Example of actions that's found in there
------------|----------------------------|------------------------------------------
`Alt+RMB`   | Pane actions               | _Remove this pane_, _new split left_
`Shift+RMB` | Pane type specific actions | (Input Pane) _Create Tab_
`RMB`       | Control specific actions   | (Script Editor) _Execute Code_, (Expression Editor) _Update Expression_, (Output) _Snapshot then Wipe_,
