JSE
===

Joe's Script Editor - Python based standalone script editor for Autodesk Maya using maya.cmds aiming to address issues with the default script editor and enhance functionality

###_Curent status: Unstable pre-alpha_

Installation
===

1. Download as zip (to the right! :arrow_right:)

2. Extract `JSE.py` from the downloaded zip and place into the folder (typically):

- Windows: `C:\Users\YourUserName\Documents\maya\scripts`
- Mac OS X: `~/Library/Preferences/Autodesk/maya/scripts`
- Linux: `~/maya/scripts` 

   (where `~` is your home directory/folder)  

or wherever you Maya scripts folder may be


Launching it (Simple)
===

3. Open Maya
4. Run (in Python)
```python
import JSE
JSE.run()
```

Additional Configuration e.g. dockable and debug
===
Below are the launch scripts for:

#####Standard windowed
```python
import JSE
JSE.run()
```
#####Dockable version
```python
import JSE
JSE.run(1)
```
#####Debug mode for windowed
```python
import JSE
JSE.run(0,JSE.logging.DEBUG)
```
#####Debug mode for dockable
```python
import JSE
JSE.run(1,JSE.logging.DEBUG)
```

The following script is for debug: **WipeOptionVars and reload**:
```python
import JSE
JSE.wipeOptionVars()
reload(JSE)
```


#### Shelf shortcut
1. `Maya Window Menu` / `Settings/Preferences` / `Shelf Editor` (3rd from bottom)
2. Choose a shelf to put the shortcut in e.g. `Shelves Tab` / `Shelves` / `Custom` 
3. `Shelves Tab` / `Shelf Contents` / `New Item (icon button)` (top right corner, left of the grey bin)
--* This will greate a new "User Script". Give it a better name, icon label, etc.
4. `Command Tab` / `Language` / set to `Python`
5. Replace the script in the script section with that of the **Standard windowed** script (above)
6. `Double click Command Tab` / `Language` / set to `Python`
7. Replace the script in the script section with that of the **Dockable version** script (above)
8. `Popup Menu Items Tab` / `Menu Items` / `New Menu Item (icon button)` (top middle, left of to the grey bin)
9. Rename it "Standard Windowed" (`Popup Menu Items Tab` / `Menu Items` / `Rename`)
10. Change language to `Python` (`Popup Menu Items Tab` / `Menu Item Command` / `Language` / `Python`)
11. Replace the script in the script section with that of the **Debug mode for windowed** script (above)
12. Repeat from and including _setp 8_ to and including _step 11_ for the **Debug mode for dockable** and **WipeOptionVars and reload** scripts (all can be found above)

Usage (for shelf icon):
* `Single click` for standard windowed script editor
* `Double click` for standard dockable script editor
* `Right click` / `Debug mode for windowed` for windowed script editor in debug mode
* `Right click` / `Debug mode for dockable` for windowed script editor in debug mode
* `Right click` / `WipeOptionVars and reload` to wipe and reset script editor, especially useful when thing go wrong

#### Keyboard shortcut
1. `Maya Window Menu` / `Settings/Preferences` / `Hotkey Editor` (4th from top)
2. Press the `New` button (middle right of thw window)
3. Name it `JSE` followed by **Standard windowed**
--* I suggest also setting `Category` to **User**
4. `Language` / set to `Python`
5. Replace the script in the script section with that of the **Standard windowed** script (above)
6. `Accept` (Right of the script section)
7. `Assign New Hotkey` / Set your own keybaord shortcuts e.g. `F7`, the press `Assingn`
--* Press the `Query` button to see if the keyboard shortcut is already taken
--* Press the `Current Hotkeys`/`List All` button to see a list of unassigned buttons on the right hand side of the `List Hotkeys` Window
8. Repeat from and including _setp 2_ to and including _step 7_ for the **Dockable version**, **Debug mode for windowed**, **Debug mode for dockable** and **WipeOptionVars and reload** scripts (all can be found above)

Usage: Press the keyboard shortcut you assigned!
