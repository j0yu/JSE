import maya.cmds as c

'''
=== TERMINOLOGY GUIDE ===

    Input   =   The pane section with the tabs and command line
    Output  =   The pane section with the output console


'''

currentInputTabLangs = []   # List of tabs' languages
currentInputTabLabels = []  # List of tabs' label/name
currentInputTabFiles = []   # List of tabs' associated file location
currentInputTabCode = []    # List of tabs' text buffer/the code inside it
currentInputTabs = []       # List of cmdScrollFieldExecuters, will be in order of the tabs (left to right I presume)

window = ""                 # The JSE window control
layout = ""                 # Main layout under the JSE window
tabLayouts = []             # List of all tab layout in the input pane sections

''' Global Input/Output Settings:

--- Executer ---
commandCompletion
showLineNumbers
objectPathCompletion
showTooltipHelp

--- Reporter ---



'''

def split( paneSection, re_assign_position="" ):
    '''
    Procedure to split the current pane into 2 panes, or set up the default
    script editor panels if this is the first time it is run


    re_assign_position:       "",  Only for initial creation, creates new default split pane, otherwise...
                        "bottom",  New pane position for existing pane, which will then be
                          "left",  used to figure out the pane number for setPane flag and
                         "right",  horizontal/vertical for configuration flag for c.paneLayout()
                           "top"
    '''

    # print 'split called with '+paneSection+' and '+re_assign_position
    if re_assign_position == "":
        '''
            If just initialising    --- Create new vertical 2 pane layout
                                    --- Create output and input pane and assign
                                        it to the new pane layout
                                    --- Return the pane layout so formLayout can
                                        snap it to the window's edges
        '''
        newPaneLayout = c.paneLayout(configuration='vertical2',parent=paneSection)
        c.paneLayout(newPaneLayout, edit=True,
                     setPane=[ (createOutput( newPaneLayout ) , 1),
                               (createInput(  newPaneLayout ) , 2) ] )
        return newPaneLayout
    else:
        ''' --- FIRST ---
            Find the paneLayout above the current control/layout.
            This is done through assigning and reassigning the parent
            and child, shuffling up the levels of parents until the
            a paneLayout is identified

            paneSection         :   child right underneath the paneLayout that the
                                    input/output section belong to
            parentPaneLayout    :   paneLayout that is the parent of the pane that
                                    called the split, initially initialised to paneSection
                                    in order to start the parent traversal algorithm
        '''
        parentPaneLayout = paneSection
        while not( c.paneLayout( parentPaneLayout, query=True, exists=True) ):
            # print "parentPaneLayout is ------ ",parentPaneLayout
            paneSection = parentPaneLayout
            parentPaneLayout = c.control(parentPaneLayout, query=True, parent=True)

        #---------------------------- DEBUG ------------------------------------
        # print "parent paneLayout is ----- ",parentPaneLayout
        # print "           child is ------ ",paneSection,"---",c.control(paneSection,q=1,ex=1)
        # import re
        # paneSectionShortName = re.split("\|",paneSection)[-1]
        # print "           (short)  ------ ",paneSectionShortName
        # parentPaneLayoutChildArray = c.paneLayout( parentPaneLayout, query=True, ca=True)
        # print "parentPaneLayout children- ",parentPaneLayoutChildArray
        # print "       child index number- ",parentPaneLayoutChildArray.index(paneSectionShortName)
        #---------------------------- END OF DEBUG ------------------------------------


        ''' --- SECOND ---
            Figure out which index of the pane that called split is in.
            This is done by retrieving the child array, where it's index is in the
            same order as the pane index, and then finding the index of the element
            that matches the paneSection's short name (that is, not including the
            full path)

            paneSectionShortName        :   name of the control/layout immediately under the
                                            parentPaneLayout that the split was called from
                                            (dis-includes the full object path)

            paneSectionNumber           :   pane index is the index of the child element + 1
        '''
        import re
        paneSectionShortName = re.split("\|",paneSection)[-1] # strip the short name from the full name
        paneSectionNumber = c.paneLayout( parentPaneLayout, query=True, ca=True).index(paneSectionShortName)+1




        ''' --- FINALLY ---
            Setup values for new paneLayout setup and assingment of new/existing panes
            to the newly created paneLayout depending on direction.

            paneConfig          :   paneLayout flag value for the configuration flag,
                                    how the pane layout is split basically
            newPaneLayout       :   name of the new pane layout created using the
                                    specified configuration
            newSectionPaneIndex :   Pane number for the new section to be created
                                    in the new paneLayout
            oldSectionPaneIndex :   Pane number for the previously existing section
                                    that was "split" in this new paneLayout

        '''
        if re_assign_position == "top":
            paneConfig = 'horizontal2'
            newSectionPaneIndex = 1
            oldSectionPaneIndex = 2

        if re_assign_position == "bottom":
            paneConfig = 'horizontal2'
            newSectionPaneIndex = 2
            oldSectionPaneIndex = 1

        if re_assign_position == "left":
            paneConfig = 'vertical2'
            newSectionPaneIndex = 1
            oldSectionPaneIndex = 2

        if re_assign_position == "right":
            paneConfig = 'vertical2'
            newSectionPaneIndex = 2
            oldSectionPaneIndex = 1

        newPaneLayout =  c.paneLayout(configuration=paneConfig, parent=parentPaneLayout)
        # print newPaneLayout, c.paneLayout(newPaneLayout, q=1,ex=1)
        c.paneLayout(parentPaneLayout, edit=True,
                     setPane=[( newPaneLayout, paneSectionNumber )]  )
        # print "assigning new split to current pane................."
        c.control(paneSection, edit=True, parent=newPaneLayout)
        c.paneLayout(newPaneLayout, edit=True,
                     setPane=[ (createInput( newPaneLayout ) , newSectionPaneIndex),
                               (        paneSection          , oldSectionPaneIndex) ] )

def deletePane(paneSection):
        '''
        This procedure removes the pane specified in the parameter, effectively
        re-merging the other pane in the shared pane layout to the pane layout
        above it. The following is a rough outline of what happens

        1 --- Find Parent Layout
        2 --- Find other secion's name and number, this will be kept
        3 --- Find grand parent layout
        4 --- Find section number of parent layout under grand parent layout
        5 --- Re-parent other section --> grand parent layout, same section number as parent layout
        6 --- Delete parent layout, which also deletes the current section (parent layout's child)
        '''

        ''' --- FIRST ---
                Find the paneLayout above the current control/layout.
                This is done through assigning and reassigning the parent
                and child, shuffling up the levels of parents until the
                a paneLayout is identified

                paneSection         :   child right underneath the paneLayout that the
                                        input/output section belong to
                parentPaneLayout    :   paneLayout that is the parent of the pane that
                                        called the split, initially initialised to paneSection
                                        in order to start the parent traversal algorithm
            '''
        parentPaneLayout = paneSection
        while not( c.paneLayout( parentPaneLayout, query=True, exists=True) ):
            paneSection = parentPaneLayout
            parentPaneLayout = c.control(parentPaneLayout, query=True, parent=True)

        ''' --- SECOND ---
                Figure out which indices the various children of the different pane layouts
                are, as well as the grand parent layout. Can't forget about the grannies

        '''
        parentPaneLayoutChildren        = c.paneLayout( parentPaneLayout, query=True, childArray=True)
        grandParentPaneLayout           = c.paneLayout( parentPaneLayout, query=True, parent=True)
        grandParentPaneLayoutChildren   = c.paneLayout( grandParentPaneLayout, query=True, childArray=True)

        import re
        paneSectionShortName        = re.split("\|",paneSection)[-1] # strip the short name from the full name
        parentPaneLayoutShortName   = re.split("\|",parentPaneLayout)[-1] # strip the short name from the full name

        parentPaneLayoutSectionNumber   = grandParentPaneLayoutChildren.index(parentPaneLayoutShortName)+1

        otherPaneChildNum           = ( parentPaneLayoutChildren.index(paneSectionShortName)+1 ) % 2
        otherParentPaneSectionNum   = (parentPaneLayoutSectionNumber % 2) + 1

        ''' --- FINALLY ---
                Re-parenting and assigning the control to the grand parent layout
                and deleting the pane layout that it previously resided under
        '''
        c.control( parentPaneLayoutChildren[otherPaneChildNum], edit=True, parent=grandParentPaneLayout)
        c.paneLayout( grandParentPaneLayout, edit=True,
                        setPane=[ parentPaneLayoutChildren[otherPaneChildNum], parentPaneLayoutSectionNumber ])
        # c.deleteUI( parentPaneLayout ) # Segmentation fault causer in 2014 SP2 Linux

def saveScript(paneSection, saveAs):
        '''
        This procedure saves the current active tab's script to a file. If...

        Current tab has file location |  and saveAs is  | then...
        ==============================|=================|===========================
                    Yes               |       Yes       |   Save to new file
        ------------------------------|-----------------|---------------------------
                    No                |       Yes       |   Save to new file
        ------------------------------|-----------------|---------------------------
                    Yes               |       No        |   Save to file location
        ------------------------------|-----------------|---------------------------
                    No                |       No        |   Save to new file



        1 --- Find Parent Layout
        2 --- Find other secion's name and number, this will be kept
        3 --- Find grand parent layout
        4 --- Find section number of parent layout under grand parent layout
        5 --- Re-parent other section --> grand parent layout, same section number as parent layout
        6 --- Delete parent layout, which also deletes the current section (parent layout's child)
        '''

        print "---------> executer",c.cmdScrollFieldExecuter( paneSection, q=1, ex=1)
        print "---------> reporter",c.cmdScrollFieldReporter( paneSection, q=1, ex=1)

        if c.cmdScrollFieldReporter( paneSection, q=1, ex=1):
            print "line numbering was..",c.cmdScrollFieldReporter( paneSection, q=1, ln=1)
            c.cmdScrollFieldReporter( paneSection, e=1, ln=0)
            print "line numbering is...",c.cmdScrollFieldReporter( paneSection, q=1, ln=1)

        ''' --- FIRST ---
                Find the paneLayout above the current control/layout.
                This is done through assigning and reassigning the parent
                and child, shuffling up the levels of parents until the
                a paneLayout is identified

                paneSection         :   child right underneath the paneLayout that the
                                        input/output section belong to
                parentPaneLayout    :   paneLayout that is the parent of the pane that
                                        called the split, initially initialised to paneSection
                                        in order to start the parent traversal algorithm
        parentPaneLayout = paneSection
        while not( c.paneLayout( parentPaneLayout, query=True, exists=True) ):
            paneSection = parentPaneLayout
            parentPaneLayout = c.control(parentPaneLayout, query=True, parent=True)
        '''

        ''' --- SECOND ---
                Figure out which indices the various children of the different pane layouts
                are, as well as the grand parent layout. Can't forget about the grannies

        parentPaneLayoutChildren        = c.paneLayout( parentPaneLayout, query=True, childArray=True)
        grandParentPaneLayout           = c.paneLayout( parentPaneLayout, query=True, parent=True)
        grandParentPaneLayoutChildren   = c.paneLayout( grandParentPaneLayout, query=True, childArray=True)

        import re
        paneSectionShortName        = re.split("\|",paneSection)[-1] # strip the short name from the full name
        parentPaneLayoutShortName   = re.split("\|",parentPaneLayout)[-1] # strip the short name from the full name

        parentPaneLayoutSectionNumber   = grandParentPaneLayoutChildren.index(parentPaneLayoutShortName)+1

        otherPaneChildNum           = ( parentPaneLayoutChildren.index(paneSectionShortName)+1 ) % 2
        otherParentPaneSectionNum   = (parentPaneLayoutSectionNumber % 2) + 1
        '''

        ''' --- FINALLY ---
                Re-parenting and assigning the control to the grand parent layout
                and deleting the pane layout that it previously resided under
        c.control( parentPaneLayoutChildren[otherPaneChildNum], edit=True, parent=grandParentPaneLayout)
        c.paneLayout( grandParentPaneLayout, edit=True,
                        setPane=[ parentPaneLayoutChildren[otherPaneChildNum], parentPaneLayoutSectionNumber ])
        # c.deleteUI( parentPaneLayout ) # Segmentation fault causer in 2014 SP2 Linux

        '''

def createPaneMenu( ctrl ):
    # print 'called create menu with '+str(ctrl)+'...........'
    c.popupMenu( parent=ctrl , altModifier=True, markingMenu=True) # markingMenu = Enable pie style menu
    '''
    c.menuItem(  label="Panes...", radialPosition="NW",
                    submenu=True )
    '''
    c.menuItem(  label="Right", radialPosition="E",
                    command="JSE.split('"+ctrl+"','right')" )
    c.menuItem(  label="Left", radialPosition="W",
                    command="JSE.split('"+ctrl+"','left')" )
    c.menuItem(  label="Below", radialPosition="S",
                    command="JSE.split('"+ctrl+"','bottom')" )
    c.menuItem(  label="Above", radialPosition="N",
                    command="JSE.split('"+ctrl+"','top')" )

    c.menuItem(  label="Hey you! Choose new section location...", enable=False)
    c.menuItem(  label="Remove This Pane!",
                    command="JSE.deletePane('"+ctrl+"')")
    c.menuItem(  label="Save script as...",
                    command="JSE.saveScript('"+ctrl+"',True)")
    c.menuItem(  label="Save script...",
                    command="JSE.saveScript('"+ctrl+"',False)")
    '''
    c.setParent(menu=1)

    c.menuItem(  label="Tab...", radialPosition="NE",
                    submenu=True )
    '''


def createExpressionMenu( ctrl ):
    # print 'called create menu with '+str(ctrl)+'...........'
    c.popupMenu( parent=ctrl , markingMenu=True) # markingMenu = Enable pie style menu
    c.menuItem(  label="Right", radialPosition="E",
                    command="JSE.split('"+ctrl+"','right')" )
    c.menuItem(  label="Left", radialPosition="W",
                    command="JSE.split('"+ctrl+"','left')" )
    c.menuItem(  label="Below", radialPosition="S",
                    command="JSE.split('"+ctrl+"','bottom')" )
    c.menuItem(  label="Above", radialPosition="N",
                    command="JSE.split('"+ctrl+"','top')" )

    c.menuItem(  label="Hey you! Choose new section location...", enable=False)
    c.menuItem(  label="Remove This Pane!",
                    command="JSE.deletePane('"+ctrl+"')")
    c.menuItem(  label="Save script as...",
                    command="JSE.saveScript('"+ctrl+"',True)")
    c.menuItem(  label="Save script...",
                    command="JSE.saveScript('"+ctrl+"',False)")



def createOutput( parentPanelLayout ):
    output = c.cmdScrollFieldReporter(parent = parentPanelLayout, backgroundColor=[0.1,0.1,0.1] )
    createPaneMenu( output )
    print "output created...."
    return output


def makeInputTab(tabUsage, pTabLayout, tabLabel, text="", fileLocation=""):
    '''
        If there is no text then load from file
    '''
    if tabUsage == "mel"     : bkgndColour = [0.16, 0.16, 0.16]
    if tabUsage == "expr"    : bkgndColour = [0.16, 0.13, 0.13]
    if tabUsage == "python"  : bkgndColour = [0.12, 0.14, 0.15]

    if tabUsage == "python"  : tabLang = "python"
    else                     : tabLang = "mel"

    inputField = c.cmdScrollFieldExecuter(  sourceType= tabLang,
                                            backgroundColor = bkgndColour,
                                            parent=pTabLayout,

                                            showLineNumbers=True )

    if fileLocation != "": c.cmdScrollFieldExecuter(inputField, e=1, loadContents=fileLocation)
    if text != ""        :
        c.cmdScrollFieldExecuter(inputField, e=1, text=text)
        c.cmdScrollFieldExecuter(inputField, e=1, storeContents=fileLocation)

    c.tabLayout(pTabLayout, e=1, tabLabel= [c.tabLayout(pTabLayout,
                                                        q=1, childArray=1)[-1] ,# Get the name of the newest tab child created
                                            tabLabel ] )                        # and rename that tab with our label

    createPaneMenu(inputField);

    return inputField


def createInput( parentUI ):
    global currentInputTabLangs
    global currentInputTabLabels
    global currentInputTabFiles
    global currentInputTabs
    global currentInputTabCode

    inputLayout = c.formLayout(parent = parentUI) # formLayout that will hold all the tabs and command line text field
    inputTabsLay = c.tabLayout() # tabLayout that will hold all the input tab buffers


    #==========================================================================================================================
    #= See if previous JSE Tab settings exist, otherwise hijack Maya's current ones
    #==========================================================================================================================
    if c.optionVar(exists="JSE_input_tabLangs"): # Has JSE been used before? (It would have stored this variable)
    # (YES)
        currentInputTabLangs  = c.optionVar(q="JSE_input_tabLangs") # Get list of tabs' languages
        currentInputTabLabels = c.optionVar(q="JSE_input_tabLabels")# Get list of tabs' label/names
        currentInputTabFiles  = c.optionVar(q="JSE_input_tabFiles") # Get list of tabs' associated file addressess
        for i in currentInputTabLangs:currentInputTabCode.append( "" )
    else: # (NO)
        from maya.mel import eval as melEval
        if melEval("$workaroundToGetVariables = $gCommandExecuterType"): # What about Maya's own script editor, was it used?
            # (YES) Retrieve existing tabs' languages from the latest Maya script editor state

            # Here we use a workaround to get a variable from MEL (http://help.autodesk.com/cloudhelp/2015/ENU/Maya-Tech-Docs/CommandsPython/eval.html, example section)
            currentInputTabLangs  = melEval("$workaroundToGetVariables = $gCommandExecuterType")
            currentInputTabLabels = melEval("$workaroundToGetVariables = $gCommandExecuterName")
            for cmdExecuter in melEval("$workaroundToGetVariables = $gCommandExecuter"):
                currentInputTabCode.append( c.cmdScrollFieldExecuter(cmdExecuter, q=1, t=1) )
                print "appending"

        else: # (NO)
            print "===Maya's own script editor, wasn't used!! NUTS! THIS SHOULD NOT BE HAPPENING==="
            print "===Default to standard [MEL, PYTHON] tab==="
            currentInputTabLangs  = ["mel","python"]
            currentInputTabLabels = ["mel","python"]

        # Either way, whether Maya have it or not, it definitely will not have file locations, so we create one
        for i in range( len(currentInputTabLangs) ):
            fileExt = ""
            if currentInputTabLangs[i] == "python": fileExt = "py"
            else: fileExt = "mel"
            currentInputTabFiles.append(currentInputTabLabels[i]+"."+fileExt)

        # Store the settings
        for i in currentInputTabLangs : c.optionVar(stringValueAppend=["JSE_input_tabLangs" ,i])
        for i in currentInputTabLabels: c.optionVar(stringValueAppend=["JSE_input_tabLabels",i])
        for i in currentInputTabFiles : c.optionVar(stringValueAppend=["JSE_input_tabFiles" ,i])




    #=============================================================
    #= Create the tabs
    #=============================================================
    if ( len(currentInputTabLangs) != len(currentInputTabLabels) ):
        print "You're fucked, len(currentInputTabLangs) should euqal len(currentInputTabLabels)",\
              "\n currentInputTabLangs",len(currentInputTabLangs),currentInputTabLangs,\
              "\n currentInputTabLabels",len(currentInputTabLabels),currentInputTabLabels,\
              "\n currentInputTabFiles",len(currentInputTabFiles),currentInputTabFiles
    else:
        print len(currentInputTabLabels), len(currentInputTabCode)
        for i in xrange( len(currentInputTabLabels) ):
            currentInputTabs.append(
                makeInputTab(   currentInputTabLangs[i],
                                inputTabsLay,
                                currentInputTabLabels[i],
                                currentInputTabCode[i],
                                currentInputTabFiles[i] )
            )

        currentInputTabs.append(
            makeInputTab( "expr", inputTabsLay, "test expression" )
        )


    inputCmdLine = c.textField(parent= inputLayout, manage=False)

    c.formLayout(inputLayout, edit=True,
                 attachForm=[ (inputTabsLay, "top", 0),    # Snapping the top, left and right edges
                              (inputTabsLay, "left", 0),   # of the tabLayout to the edges of the
                              (inputTabsLay, "right", 0),  # formLayout

                              (inputCmdLine, "left", 0),    # Snapping the bottom, left and right edges
                              (inputCmdLine, "right", 0),   # of the cmdLine to the edges of the
                              (inputCmdLine, "bottom", 0) ],# formLayout

                 attachControl=(inputTabsLay, "bottom", 0, inputCmdLine) )
                 # Snap the bottom of the tabLayout to the top of cmdLine


    print "input created...."

    return inputLayout

def saveCurrentSettings():
    for i in currentInputTabLangs:  c.optionVar( stringValueAppend=("JSE_input_tabLangs",i) )
    for i in currentInputTabLabels: c.optionVar( stringValueAppend=("JSE_input_tabLabels",i) )
    for i in currentInputTabFiles:  c.optionVar( stringValueAppend=("JSE_input_tabFiles",i) )

def wipeOptionVars():
    for i in c.optionVar(list=True):
        if i[0:4] == "JSE_":
            c.optionVar(remove=i)
    c.confirmDialog(icon="warning", messageAlign="center",
                message="JSE optionVars wiped! Reactor core highly unstable...\nCLOSE IT DOWN AND GET OUTTA THERE!")

def layoutJSE():
    def recursiveLayoutTraverse(JSELayout, layerNum):
        layoutChildArray = c.layout(JSELayout, q=1, ca=1)
        if layoutChildArray != []:
            for i in c.layout(JSELayout, q=1, ca=1):
                for tabs in range(layerNum): print "\t",
                print i
                try:
                    c.layout(i, q=1, ca=1)
                    recursiveLayoutTraverse(i, layerNum+1)
                except:
                    pass

    global layout
    print "------------------JSE LAYOUT------------------"
    recursiveLayoutTraverse(layout, 0)

    ''' EXAMPLE OUTPUT
    paneLayout38
    cmdScrollFieldReporter18
    formLayout110
        tabLayout22
            cmdScrollFieldExecuter179
            cmdScrollFieldExecuter180
            cmdScrollFieldExecuter181
            cmdScrollFieldExecuter182
            cmdScrollFieldExecuter183
            cmdScrollFieldExecuter184
            cmdScrollFieldExecuter185
            cmdScrollFieldExecuter186
            cmdScrollFieldExecuter187
            cmdScrollFieldExecuter188
        textField22
    '''


    ''' Storage
    --- Window ---
    Width
    Height

    --- Pane Layout ---
    childArray
    configuration       vertical2
    paneSize            [71, 100, 29, 100]

    --- Reporter ---
 -eac -echoAllCommands       on|off
 -fst -filterSourceType      String
 -pma -popupMenuArray
  -se -suppressErrors        on|off
  -si -suppressInfo          on|off
  -sr -suppressResults       on|off
 -sst -suppressStackTrace    on|off
  -st -stackTrace            on|off
  -sv -saveSelection         String
 -svs -saveSelectionToShelf
  -sw -suppressWarnings      on|off
   -t -text                  String

    --- Executer ---
 -acb -autoCloseBraces       on|off
 -pma -popupMenuArray
 -spt -spacesPerTab          UnsignedInt
  -st -sourceType            String
 -stc -storeContents         String
   -t -text                  String
 -tfi -tabsForIndent         on|off


    '''

def setPane( paneType ):
    pass



def run(dockable):
    global window
    global layout

    print "JSE called ------------------"

    #---- Setup ----
    window = c.window(width=950, height=650)
    layout = c.paneLayout()
    newPaneLayout = split(layout)
    if dockable:
        c.dockControl("JSE",area='left',floating=True,content=window)
        print "Dockable",
    else:
        c.showWindow(window)
        print "Standard",
    print "JSE created ------------------"

# End of script, now just to run it
# run(0)
