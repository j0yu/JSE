import maya.cmds as c
from re import match
from maya.mel import eval as melEval
from copy import deepcopy

import logging
logger = logging.getLogger("JSE")


'''
=== TERMINOLOGY GUIDE ===

    Input   =   The pane section with the tabs and command line
    Output  =   The pane section with the output console


'''

currentInputTabType = []    # List of tabs' languages
currentInputTabLabels = []  # List of tabs' label/name
currentInputTabFiles = []   # List of tabs' associated file location
currentInputTabs = []       # List of cmdScrollFieldExecuters, will be in order of the tabs (left to right I presume)
currentInputTabLayouts = [] # List of all tab layout in the various input pane sections
currentPaneScematic = ["V50","I1","O"]    # e.g. ["V50","V30","O","V10","I1","I2","H50","I3","O"]
currentAllSchematic = []    # e.g. [ ["V50", "window4|paneLayout19|paneLayout20",
                            #         "O"  , "window4|paneLayout19|paneLayout20|cmdScrollFieldReporter8"],
                            #         "I1" , "window4|paneLayout19|paneLayout20|formLayout123"],
                            #        ["V31", "window5|paneLayout21|paneLayout22",
                            #         "O"  , "window5|paneLayout21|paneLayout22|cmdScrollFieldReporter10"],
                            #         "I3" , "window5|paneLayout21|paneLayout22|formLayout343"]
                            #      ]

engaged = False             # If True, JSE had ran in this instance of Maya
InputBuffersPath = ""
OutputSnapshotsPath = ""

''' Global Input/Output Settings:

--- Executer ---
commandCompletion
showLineNumbers
objectPathCompletion
showTooltipHelp

--- Reporter ---



'''
# Procedure to save up retyping the same debug text formatting
def defStart(text): return "{:\\<80}".format(str(text)+" ")
def defEnd(text): return "{:/>80}".format(" "+str(text))
def head1(text): return "{:=^80}".format(" "+str(text)+" ")
def head2(text): return "{:-^80}".format(" "+str(text)+" ")
def var1(inText,inVar): return "{:>30} -- {!s}".format(str(inText) , str(inVar) )
def var2(inText,inVar): return "{:>31} - {!s}".format("("+str(inText)+")" , str(inVar) )


################################################      PaneRelated       ################################################

def navigateToParentPaneLayout(paneSection):
    """
    ------------Internal useage------------
    Find the paneLayout above the current control/layout.
    This is done through assigning and reassigning the parent
    and child, shuffling up the levels of parents until the
    a paneLayout is identified

    paneSection         :   child right underneath the paneLayout that the
    (returned)              input/output section belong to.
                            The returned value can be different to the parameter
                            value that was passed in

    parentPaneLayout    :   paneLayout that is the parent of the pane that
    (returned)              called the split, initially initialised to paneSection
                            in order to start the parent traversal algorithm
    """
    logger.debug(defStart("Navigating to parent paneLayout"))
    logger.debug(var1("paneSection",paneSection))

    try: parentPaneLayout = c.control(paneSection, query=True, parent=True)
    except: parentPaneLayout = c.layout(paneSection, query=True, parent=True)
    logger.debug(var1(        "parentPaneLayout",parentPaneLayout))
    logger.debug(head1("Traversing to get parent paneLayout"))
    while not( c.paneLayout( parentPaneLayout, query=True, exists=True) ):
        paneSection = parentPaneLayout
        logger.debug(var1(        "parentPaneLayout",parentPaneLayout))
        logger.debug(var1(     "paneSection becomes",paneSection))
        parentPaneLayout = c.control(parentPaneLayout, query=True, parent=True)
        logger.debug(var1("parentPaneLayout becomes",parentPaneLayout))


    logger.debug(head2("After traversal debug"))
    logger.debug(var1(     "parent paneLayout is",parentPaneLayout ) )
    logger.debug(var1(   "child is (paneSection)",paneSection))
    logger.debug(var1(                 "(exist?)",c.control(paneSection,q=1,ex=1)) )

    logger.debug(defEnd("Navigated to parent paneLayout"))
    return paneSection,parentPaneLayout


def constructJSE( paneSection, buildSchematic ):
    """
    Procedure to split the current pane into 2 panes, or set up the default
    script editor panels if this is the first time it is run


              buildSchematic,  ---Need to write description for it---
    """
    global currentInputTabLayouts
    global currentAllSchematic

    def constructSplits(paneCfgTxt, paneEditSize, buildSchematic=buildSchematic):
        newPaneLayout = c.paneLayout(configuration=paneCfgTxt,parent=paneSection,
                                     separatorMovedCommand="JSE.refreshAllScematic()")
        currentAllSchematic[-1].append(newPaneLayout)
        logger.debug(var1("currentAllSchematic[-1]",currentAllSchematic[-1]) )

        logger.debug( var1("buildSchematic[0]",buildSchematic[0]))
        if (buildSchematic[0][0]=="V") or (buildSchematic[0][0]=="H"):
            paneChild1,buildSchematic = constructJSE( newPaneLayout, buildSchematic)
            logger.debug(var1("buildSchematic becomes",buildSchematic))
            logger.debug(var1("paneChild1",paneChild1))

        elif buildSchematic[0][0]=="I":
            currentAllSchematic[-1].append(buildSchematic[0])
            paneChild1 = createInput(newPaneLayout, int(buildSchematic.pop(0)[1:]))
            logger.debug(var1("buildSchematic becomes",buildSchematic))
            currentAllSchematic[-1].append(paneChild1)
            logger.debug(var1("currentAllSchematic[-1]",currentAllSchematic[-1]) )

        elif buildSchematic[0][0]=="O":
            currentAllSchematic[-1].append( buildSchematic.pop(0) )
            paneChild1 = createOutput(newPaneLayout)
            logger.debug(var1("buildSchematic becomes",buildSchematic))
            currentAllSchematic[-1].append(paneChild1)
            logger.debug(var1("currentAllSchematic[-1]",currentAllSchematic[-1]) )


        logger.debug( var1("buildSchematic[0]",buildSchematic[0]))
        if (buildSchematic[0][0]=="V") or (buildSchematic[0][0]=="H"):
            paneChild2,buildSchematic = constructJSE( newPaneLayout, buildSchematic)
            logger.debug(var1("buildSchematic becomes",buildSchematic))
            logger.debug(var1("paneChild2",paneChild2))

        elif buildSchematic[0][0]=="I":
            currentAllSchematic[-1].append(buildSchematic[0])
            paneChild2 = createInput(newPaneLayout, int(buildSchematic.pop(0)[1:]))
            logger.debug(var1("buildSchematic becomes",buildSchematic))
            currentAllSchematic[-1].append(paneChild2)
            logger.debug(var1("currentAllSchematic[-1]",currentAllSchematic[-1]) )

        elif buildSchematic[0][0]=="O":
            currentAllSchematic[-1].append( buildSchematic.pop(0) )
            paneChild2 = createOutput(newPaneLayout)
            logger.debug(var1("buildSchematic becomes",buildSchematic))
            currentAllSchematic[-1].append(paneChild2)
            logger.debug(var1("currentAllSchematic[-1]",currentAllSchematic[-1]) )


        logger.debug(var1("newPaneLayout",newPaneLayout) )
        c.paneLayout(newPaneLayout, edit=True,
                     paneSize=paneEditSize,
                     setPane=[ (paneChild1 , 1),
                               (paneChild2 , 2) ] )


        logger.debug(defEnd("Constructed current split"))
        logger.debug("")
        return newPaneLayout,buildSchematic

    logger.debug(defStart("Constructing"))
    logger.debug(var1("paneSection",paneSection) )
    logger.debug(var1("buildSchematic",buildSchematic) )
    '''
        If just initialising    --- Create new vertical 2 pane layout
                                --- Create output and input pane and assign
                                    it to the new pane layout
                                --- Return the pane layout so formLayout can
                                    snap it to the window's edges

    '''
    logger.debug(head2("Popping out the first element"))
    paneCfg = buildSchematic.pop(0)
    logger.debug(var1("buildSchematic (popped)",buildSchematic) )
    logger.debug(var1("paneCfg",paneCfg) )

    currentAllSchematic[-1].append(paneCfg)
    logger.debug(var1("currentAllSchematic[-1]",currentAllSchematic[-1]) )


    if   paneCfg.startswith("V") :
        newPaneLayout,buildSchematic = constructSplits( "vertical2",   [1, int(paneCfg[1:]), 100] )
        logger.debug(defEnd("Constructed"))
        logger.debug("")
        return newPaneLayout, buildSchematic

    elif paneCfg.startswith("H") :
        newPaneLayout,buildSchematic = constructSplits( "horizontal2", [1, 100, int(paneCfg[1:])] )
        logger.debug(defEnd("Constructed"))
        logger.debug("")
        return newPaneLayout, buildSchematic

    elif paneCfg.startswith("O") :
        newPane = createOutput(paneSection)
        currentAllSchematic[-1].append(newPane)
        c.paneLayout(paneSection, edit=True, setPane=[ ( newPane, 1)] )
        logger.debug(defEnd("Constructed"))
        logger.debug("")
        return paneSection, buildSchematic

    elif paneCfg.startswith("I") :
        newPane = createInput(createInput)
        currentAllSchematic[-1].append(newPane)
        c.paneLayout(paneSection, edit=True, setPane=[ ( newPane , 1)] )
        logger.debug(defEnd("Constructed"))
        logger.debug("")
        return paneSection, buildSchematic


def split( paneSection, re_assign_position, newPaneIsInput):
    """
    Procedure to split the current pane into 2 panes, or set up the default
    script editor panels if this is the first time it is run


              re_assign_position,  New pane position for existing pane, which will then be
                                   used to figure out the pane number for setPane flag and
                                   horizontal/vertical for configuration flag for c.paneLayout()
    """
    global currentInputTabLayouts
    global currentAllSchematic

    logger.debug(defStart("Splitting"))
    logger.debug(var1("paneSection",paneSection) )
    logger.debug(var1("re_assign_position",re_assign_position) )

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
    paneSection,parentPaneLayout = navigateToParentPaneLayout(paneSection)

    paneSectionShortName = paneSection.rsplit("|",1)[-1]
    logger.debug(var1(              "(shortName)",paneSectionShortName ) )

    parentPaneLayoutChildArray = c.paneLayout( parentPaneLayout, query=True, ca=True)
    logger.debug(var1("parentPaneLayout children",parentPaneLayoutChildArray ))
    logger.debug(var1(       "child index number",parentPaneLayoutChildArray.index(paneSectionShortName) ))




    window_IndicesInSchematic = ""
    pane_IndicesInSchematic = ""
    try:    paneSection = c.control(paneSectionShortName, q=1, fullPathName=1)
    except: paneSection = c.layout( paneSectionShortName, q=1, fullPathName=1)
    for i in xrange(len(currentAllSchematic)):
        for j in xrange(0, len(currentAllSchematic[i]), 2):
            if currentAllSchematic[i][j+1] == paneSection:
                window_IndicesInSchematic = i
                pane_IndicesInSchematic = j
                break
        if pane_IndicesInSchematic: break

    newSchematicStart  = currentAllSchematic[window_IndicesInSchematic][:pane_IndicesInSchematic]
    logger.debug(var1("newSchematicStart",newSchematicStart))
    newSchematicEnding = currentAllSchematic[window_IndicesInSchematic][pane_IndicesInSchematic+2:]
    logger.debug(var1("newSchematicEnding",newSchematicEnding))

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
    # paneSectionShortName = paneSection.rsplit("|",1)[-1] # strip the short name from the full name
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

    elif re_assign_position == "bottom":
        paneConfig = 'horizontal2'
        newSectionPaneIndex = 2
        oldSectionPaneIndex = 1

    elif re_assign_position == "left":
        paneConfig = 'vertical2'
        newSectionPaneIndex = 1
        oldSectionPaneIndex = 2

    elif re_assign_position == "right":
        paneConfig = 'vertical2'
        newSectionPaneIndex = 2
        oldSectionPaneIndex = 1

    else:
        logger.critical("re_assign_position not matched with top, bottom, left or right!")
        logger.critical(var1("re_assign_position",re_assign_position))

    logger.debug(var1(         "paneConfig",paneConfig ))
    logger.debug(var1("newSectionPaneIndex",newSectionPaneIndex ))
    logger.debug(var1("oldSectionPaneIndex",oldSectionPaneIndex ))

    logger.debug(head2("Setting values for new paneLayouts" ) )
    newPaneLayout =  c.paneLayout(configuration=paneConfig, parent=parentPaneLayout,
                                  separatorMovedCommand="JSE.refreshAllScematic()")


    logger.debug(var1("parentPaneLayout",parentPaneLayout ))
    logger.debug(var1(     "paneSection",paneSection ))
    logger.debug(var1(   "newPaneLayout",newPaneLayout ))
    logger.debug(var1(        "(exist?)",c.paneLayout(newPaneLayout, q=1,ex=1) ) )
    c.paneLayout(parentPaneLayout, edit=True,
                 setPane=[( newPaneLayout, paneSectionNumber )]  )

    logger.debug(head2("Assigning new split to current pane" ) )
    c.control(paneSection, edit=True, parent=newPaneLayout)
    if newPaneIsInput:  newPane = createInput(  newPaneLayout )
    else:               newPane = createOutput( newPaneLayout )

    c.paneLayout(newPaneLayout, edit=True,
                 setPane=[ (   newPane    , newSectionPaneIndex),
                           ( paneSection  , oldSectionPaneIndex) ] )


    newPaneSchematic = [ paneConfig[0].capitalize()+"50", newPaneLayout ]
    logger.debug(var1("newPaneSchematic",newPaneSchematic))

    newSchematic = deepcopy(newSchematicStart)
    logger.debug(var1("newSchematic",newSchematic))
    newSchematic.extend( deepcopy(newPaneSchematic) )
    logger.debug(var1("newSchematic",newSchematic))

    if newPaneIsInput:  newSectionSchematic = "I1"
    else:               newSectionSchematic = "O"

    if oldSectionPaneIndex > newSectionPaneIndex:
        newSchematic.extend( deepcopy([newSectionSchematic, newPane]) )
        newSchematic.extend( deepcopy(currentAllSchematic[window_IndicesInSchematic][pane_IndicesInSchematic:pane_IndicesInSchematic+2]) )
    else:
        newSchematic.extend( deepcopy(currentAllSchematic[window_IndicesInSchematic][pane_IndicesInSchematic:pane_IndicesInSchematic+2] ))
        newSchematic.extend( deepcopy([newSectionSchematic, newPane] ))
    logger.debug(var1("newSchematic",newSchematic))

    newSchematic.extend( deepcopy(newSchematicEnding) )
    logger.debug(var1("newSchematic",newSchematic))

    currentAllSchematic[window_IndicesInSchematic] = deepcopy(newSchematic)
    refreshAllScematic()

    logger.debug(defEnd("Splitted"))
    logger.debug("")


def deletePane(paneSection):
    global currentAllSchematic
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
    logger.debug(defStart("Deleting Pane"))
    logger.debug(var1("paneSection",paneSection))
    logger.debug(var1("currentAllSchematic",currentAllSchematic))

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
    paneSection,parentPaneLayout = navigateToParentPaneLayout(paneSection)


    ''' --- SECOND ---
            Figure out which indices the various children of the different pane layouts
            are, as well as the grand parent layout. Can't forget about the grannies

    '''
    logger.debug(var1(     "paneSection",paneSection))
    logger.debug(var1(     "parentPaneLayout",parentPaneLayout))

    parentPaneLayoutChildren        = c.paneLayout( parentPaneLayout, query=True, childArray=True)
    logger.debug(var1(     "parentPaneLayoutChildren",parentPaneLayoutChildren))

    grandParentPaneLayout           = c.paneLayout( parentPaneLayout, query=True, parent=True)
    logger.debug(var1(        "grandParentPaneLayout",grandParentPaneLayout))
    logger.debug(var1(        "objectTypeUI",c.objectTypeUI(grandParentPaneLayout)))

    if "indow" in c.objectTypeUI(grandParentPaneLayout):
        c.deleteUI(grandParentPaneLayout)
        logger.debug(head2("Grand Parent is a window, closing window") )
        logger.debug(defEnd("Deleted Pane") )
        logger.debug("")
        return

    grandParentPaneLayoutChildren   = c.paneLayout( grandParentPaneLayout, query=True, childArray=True)
    logger.debug(var1("grandParentPaneLayoutChildren",grandParentPaneLayoutChildren))

    paneSectionShortName        = paneSection.rsplit("|",1)[-1] # strip the short name from the full name
    logger.debug(var1(         "paneSectionShortName",paneSectionShortName))

    parentPaneLayoutShortName   = parentPaneLayout.rsplit("|",1)[-1] # strip the short name from the full name
    logger.debug(var1(    "parentPaneLayoutShortName",parentPaneLayoutShortName))


    parentPaneLayoutSectionNumber   = grandParentPaneLayoutChildren.index(parentPaneLayoutShortName)+1
    logger.debug(var1("parentPaneLayoutSectionNumber",parentPaneLayoutSectionNumber))

    otherPaneChildNum           = ( parentPaneLayoutChildren.index(paneSectionShortName)+1 ) % 2
    logger.debug(var1(            "otherPaneChildNum",otherPaneChildNum))

    otherParentPaneSectionNum   = (parentPaneLayoutSectionNumber % 2) + 1
    logger.debug(var1(    "otherParentPaneSectionNum",otherParentPaneSectionNum))

    window_IndicesInSchematic = ""
    pane_IndicesInSchematic = ""
    surv__IndicesInSchematic = ""
    for i in xrange(len(currentAllSchematic)):
        logger.debug(var1("Looking for", parentPaneLayout+"|"+parentPaneLayoutChildren[otherPaneChildNum]  ))
        for j in xrange(0, len(currentAllSchematic[i]), 2):
            logger.debug(var1("currentAllSchematic[i][j+1]", currentAllSchematic[i][j+1]  ))
            logger.debug(var1("Match?", (currentAllSchematic[i][j+1] == parentPaneLayout+"|"+parentPaneLayoutChildren[otherPaneChildNum])  ))
            logger.debug(var1("Match2?", currentAllSchematic[i][j+1].endswith(parentPaneLayoutChildren[otherPaneChildNum])   ))
            if currentAllSchematic[i][j+1] == parentPaneLayout:
                window_IndicesInSchematic = i
                pane_IndicesInSchematic = j
                logger.debug(var1("window_IndicesInSchematic",window_IndicesInSchematic))
                logger.debug(var1("pane_IndicesInSchematic",pane_IndicesInSchematic))
            elif currentAllSchematic[i][j+1] == parentPaneLayout+"|"+parentPaneLayoutChildren[otherPaneChildNum]:
                surv__IndicesInSchematic = j
                logger.debug(var1("surv__IndicesInSchematic",surv__IndicesInSchematic))
                break
        if surv__IndicesInSchematic: break


    ''' --- FINALLY ---
            Re-parenting and assigning the control to the grand parent layout
            and deleting the pane layout that it previously resided under
    '''
    c.control( parentPaneLayoutChildren[otherPaneChildNum], edit=True, parent=grandParentPaneLayout)
    c.paneLayout( grandParentPaneLayout, edit=True,
                    setPane=[ parentPaneLayoutChildren[otherPaneChildNum], parentPaneLayoutSectionNumber ])
    # c.deleteUI( parentPaneLayout ) # Segmentation fault causer in 2014 SP2 Linux

    newSchematicStart    = currentAllSchematic[window_IndicesInSchematic][:pane_IndicesInSchematic]
    logger.debug(var1(   "newSchematicStart",newSchematicStart))
    newSchematicSurvivor = currentAllSchematic[window_IndicesInSchematic][surv__IndicesInSchematic:surv__IndicesInSchematic+2]
    logger.debug(var1("newSchematicSurvivor",newSchematicSurvivor))
    newSchematicEnding   = currentAllSchematic[window_IndicesInSchematic][pane_IndicesInSchematic+6:]
    logger.debug(var1(  "newSchematicEnding",newSchematicEnding))

    newSchematic = []
    newSchematic.extend( deepcopy(newSchematicStart) )
    newSchematic.extend( deepcopy(newSchematicSurvivor) )
    newSchematic.extend( deepcopy(newSchematicEnding) )


    currentAllSchematic[window_IndicesInSchematic] = deepcopy(newSchematic)
    refreshAllScematic()

    logger.debug(defEnd("Deleted Pane") )
    logger.debug("")


def setPane( paneType ):

    logger.debug(defStart("Setting Pane"))
    logger.debug(var1("paneType",paneType))

    logger.debug(defEnd("Set Pane"))
    logger.debug("")


def createOutput( parentPanelLayout ):
    logger.debug(defStart("Creating output"))
    logger.debug(var1("parentPanelLayout",parentPanelLayout))

    output = c.cmdScrollFieldReporter(  parent = parentPanelLayout,
                                        backgroundColor=[0.1,0.1,0.1],

                                        stackTrace=True,
                                        lineNumbers=True )
    logger.debug(var1("output",output))

    createPaneMenu( output )
    createDebugMenu( output )
    createOutputMenu( output )
    logger.debug(defEnd("Created output!"))
    logger.debug("")
    return output


def createInput( parentUI, activeTabIndex=1 ):
    global currentInputTabType
    global currentInputTabLabels
    global currentInputTabFiles
    global currentInputTabs
    global InputBuffersPath

    logger.debug(defStart("Creating input"))
    logger.debug(var1("parentUI",parentUI))

    inputLayout = c.formLayout(parent = parentUI) # formLayout that will hold all the tabs and command line text field
    inputTabsLay = c.tabLayout(changeCommand="JSE.refreshAllScematic()",
                               visibleChangeCommand="JSE.logger.debug('visibility changed')") # tabLayout that will hold all the input tab buffers

    logger.debug(var1("inputLayout",inputLayout))
    logger.debug(var1("inputTabsLay",inputTabsLay ))

    #==========================================================================================================================
    #= See if previous JSE Tab settings exist, otherwise hijack Maya's current ones
    #==========================================================================================================================
    if c.optionVar(exists="JSE_input_tabLangs"): # Has JSE been used before? (It would have stored this variable)
        # (YES)
        logger.debug("Previous JSE existed, loading previous setting from optionVars")

        syncGlobals("retrieve")

    else: # (NO)
        logger.debug("No previous JSE optionVars found, must be fresh run of JSE eh?!")
        logger.debug("Hijacking settings and contents from Maya's script editor...")

        if melEval("$workaroundToGetVariables = $gCommandExecuterType"): # What about Maya's own script editor, was it used?
            # (YES) Retrieve existing tabs' languages from the latest Maya script editor state

            # Here we use a workaround to get a variable from MEL (http://help.autodesk.com/cloudhelp/2015/ENU/Maya-Tech-Docs/CommandsPython/eval.html, example section)
            currentInputTabType  = melEval("$workaroundToGetVariables = $gCommandExecuterType")
            currentInputTabLabels = melEval("$workaroundToGetVariables = $gCommandExecuterName")
            cmdExecutersList = melEval("$workaroundToGetVariables = $gCommandExecuter")
            for i in xrange( len(cmdExecutersList) ):
                logger.debug(head2("appending"))
                if currentInputTabType[i] == "python": fileExt = "py"
                else: fileExt = "mel"
                logger.debug(var1("cmdExecutersList[i]",cmdExecutersList[i]) )
                logger.debug(var1("saving to","JSE-Tab-"+str(i)+"-"+currentInputTabLabels[i]+"."+fileExt) )
                logger.debug("cmdExecutersList[i] text\n"+c.cmdScrollFieldExecuter(cmdExecutersList[i], q=1, text=1) )
                c.cmdScrollFieldExecuter( cmdExecutersList[i], e=1, storeContents=InputBuffersPath+"JSE-Tab-"+str(i)+"-"+str(currentInputTabLabels[i])+"."+str(fileExt) )
                c.cmdScrollFieldExecuter( cmdExecutersList[i], e=1, select=[0,0] )

            # It definitely will not have file locations, so we create one
            for i in range( len(currentInputTabType) ):
                currentInputTabFiles.append("")

        else: # (NO)
            try:
                logger.debug(head2("Looks like Maya's script editor haven't loaded in current session"))
                logger.debug(head2("Grabbing optionVars from previous session"))
                currentInputTabType =   c.optionVar(q="ScriptEditorExecuterTypeArray")
                currentInputTabLabels = c.optionVar(q="ScriptEditorExecuterLabelArray")
                for i in range( len(currentInputTabType) ):
                    if i == 0: currentInputTabFiles.append( c.about(preferences=True)+"/prefs/scriptEditorTemp/commandExecuter")
                    else     : currentInputTabFiles.append( c.about(preferences=True)+"/prefs/scriptEditorTemp/commandExecuter-"+str(i-1))

                # Still need to sort out the code stored when SE haven't been loaded in current session of Maya

            except:
                logger.critical( "=== Maya's own script editor, wasn't used!! NUTS! THIS SHOULD NOT BE HAPPENING ===" )
                logger.critical( "=== Default to standard [MEL, PYTHON] tab ===" )
                currentInputTabType  = ["mel","python"]
                currentInputTabLabels = ["mel","python"]

                # It definitely will not have file locations, so we create one
                for i in range( len(currentInputTabType) ):
                    currentInputTabFiles.append("")



        # Store the settings
        for i in currentInputTabType : c.optionVar(stringValueAppend=["JSE_input_tabLangs" ,i])
        for i in currentInputTabLabels: c.optionVar(stringValueAppend=["JSE_input_tabLabels",i])
        for i in currentInputTabFiles : c.optionVar(stringValueAppend=["JSE_input_tabFiles" ,i])




    logger.debug(var1(  "currentInputTabType",currentInputTabType))
    logger.debug(var1("currentInputTabLabels",currentInputTabLabels))
    logger.debug(var1( "currentInputTabFiles",currentInputTabFiles))

    #=============================================================
    #= Create the tabs
    #=============================================================

    if len(currentInputTabType) != len(currentInputTabLabels):
        logger.critical("You're fucked!, len(currentInputTabType) should equal len(currentInputTabLabels)")
        logger.critical("   currentInputTabType (len,value)",len(currentInputTabType) ,  currentInputTabType)
        logger.critical(" currentInputTabLabels (len,value)",len(currentInputTabLabels), currentInputTabLabels)
        logger.critical("  currentInputTabFiles (len,value)",len(currentInputTabFiles),  currentInputTabFiles)
    else:
        logger.debug(var1("len(currentInputTabLabels)",len(currentInputTabLabels)))
        logger.debug(var1( "len(currentInputTabFiles)",len(currentInputTabFiles)))

        logger.debug(head2("Making the script editor tabs"))
        for i in xrange( len(currentInputTabLabels) ):
            if currentInputTabType[i] == "python": fileExt = "py"
            else: fileExt = "mel"

            logger.debug(var1( "currentInputTabFiles[i]",currentInputTabFiles[i]))
            if match(".*/commandExecuter(-[0-9]+)?$",currentInputTabFiles[i]):
                fileLocation = currentInputTabFiles[i]
                currentInputTabFiles[i] = ""
                logger.debug(var1("new currentInputTabFiles[i]",currentInputTabFiles[i]))
            else:
                fileLocation = InputBuffersPath+"JSE-Tab-"+str(i)+"-"+currentInputTabLabels[i]+"."+fileExt

            currentInputTabs.append(
                makeInputTab(   currentInputTabType[i],
                                inputTabsLay,
                                currentInputTabLabels[i],
                                fileLocation )
            )

        logger.debug(head2("Making the expression editor tabs"))
        for i in c.ls(type="expression"):
            currentExpr = {}
            currentExpr["string"]         = c.expression(i,q=1,string=1)
            currentExpr["name"]           = c.expression(i,q=1,name=1)
            currentExpr["object"]         = c.expression(i,q=1,object=1)
            currentExpr["alwaysEvaluate"] = c.expression(i,q=1,alwaysEvaluate=1)
            currentExpr["unitConversion"] = c.expression(i,q=1,unitConversion=1)

            logger.debug(var1(        'currentExpr["string"]', currentExpr["string"] ) )
            logger.debug(var1(          'currentExpr["name"]', currentExpr["name"] ) )
            logger.debug(var1(        'currentExpr["object"]', currentExpr["object"] ) )
            logger.debug(var1('currentExpr["alwaysEvaluate"]', currentExpr["alwaysEvaluate"] ) )
            logger.debug(var1('currentExpr["unitConversion"]', currentExpr["unitConversion"] ) )


        currentInputTabs.append( # Append a test expression  layout for the time being
            makeInputTab( "expr", inputTabsLay, "testExpression" , "")
        )

    ''' Now this should be a text base interface for using the scipt editor, much like the command mode of vim #
        Right now this is disabled so I can focus on more imprtant stuff
    '''
    inputCmdLine = c.textField(parent= inputLayout, manage=False)
    logger.debug( var1("activeTabIndex",activeTabIndex))
    logger.debug( var1("inputTabsLay tabLabels",c.tabLayout(inputTabsLay,q=1,tabLabel=1)) )
    c.tabLayout(inputTabsLay, edit=True, selectTabIndex=activeTabIndex)
    c.formLayout(inputLayout, edit=True,
                 attachForm=[ (inputTabsLay, "top", 0),    # Snapping the top, left and right edges
                              (inputTabsLay, "left", 0),   # of the tabLayout to the edges of the
                              (inputTabsLay, "right", 0),  # formLayout

                              (inputCmdLine, "left", 0),    # Snapping the bottom, left and right edges
                              (inputCmdLine, "right", 0),   # of the cmdLine to the edges of the
                              (inputCmdLine, "bottom", 0) ],# formLayout

                 attachControl=(inputTabsLay, "bottom", 0, inputCmdLine) )
                 # Snap the bottom of the tabLayout to the top of cmdLine

    createDebugMenu(inputTabsLay)
    logger.debug(defEnd("Created input"))
    logger.debug("")

    return inputLayout


def refreshAllScematic():
    global currentAllSchematic
    global currentPaneScematic
    schematicForDeletion = []
    logger.debug(defStart("Refreshing all schematics"))
    logger.debug(var1("currentAllSchematic",currentAllSchematic))

    if len(currentAllSchematic[-1]):
        for i in xrange(len(currentAllSchematic)):
            logger.debug( head2("Schematic "+str(i)) )
            windowSchematic = currentAllSchematic[i]
            logger.debug(var1("windowSchematic",windowSchematic))

            fullPathSplit = windowSchematic[1].split("|")
            logger.debug(var1("fullPathSplit",fullPathSplit))

            if not c.layout( fullPathSplit[1], q=1, exists=1):
                logger.debug( head1("Schematic primary paneLayout doesn't exist"))
                schematicForDeletion.append( i )
                logger.debug(var1("schematicForDeletion",schematicForDeletion))
            else:
                for j in xrange(0 , len(windowSchematic), 2):
                    treeNodeType  = windowSchematic[j][0]
                    logger.debug(var1("treeNodeType",treeNodeType))

                    ctrlOrLayOnly = windowSchematic[j+1].rsplit("|",1)[-1]

                    try:    ctrlOrLayNew = c.control(ctrlOrLayOnly, q=1, fullPathName=1)
                    except: ctrlOrLayNew = c.layout( ctrlOrLayOnly, q=1, fullPathName=1)
                    logger.debug(var1("ctrlOrLayNew",ctrlOrLayNew))

                    windowSchematic[j+1] = ctrlOrLayNew
                    if treeNodeType == "V":
                        windowSchematic[j] = treeNodeType+str(c.paneLayout( ctrlOrLayNew , q=1, paneSize=1)[0])

                    elif treeNodeType == "H":
                        windowSchematic[j] = treeNodeType+str(c.paneLayout( ctrlOrLayNew , q=1, paneSize=1)[1])

                    elif treeNodeType == "I":
                        childTabLay = c.layout(ctrlOrLayNew,q=1,childArray=1)[0]
                        windowSchematic[j] = treeNodeType+str(c.tabLayout( childTabLay , q=1, selectTabIndex=1) )





        logger.debug( head2("Deleting schematics marked for deletion") )
        logger.debug(var1("schematicForDeletion",schematicForDeletion))
        # Remove lists from the back to front to avoid out of range issues
        for i in reversed(schematicForDeletion):
            currentAllSchematic.pop(i)
            logger.debug(var1("schematicForDeletion",schematicForDeletion))
            logger.debug(var1("currentAllSchematic",currentAllSchematic))

        logger.debug(var1("final currentAllSchematic",currentAllSchematic))
        currentPaneScematic = []
        for i in xrange(0,len(currentAllSchematic[-1]),2):
            currentPaneScematic.append( currentAllSchematic[-1][i] )

        logger.debug(var1("new currentPaneScematic",currentPaneScematic))
    logger.debug(defStart("Refreshed all schematics"))


def createPaneMenu( ctrl ):
    logger.debug(defStart("Creating Pane Menu"))
    logger.debug(var1("ctrl",ctrl))

    c.popupMenu( parent=ctrl , altModifier=True, markingMenu=True) # markingMenu = Enable pie style menu
    c.menuItem(  label="New Right", radialPosition="E",
                    command="JSE.split('"+ctrl+"','right',True)" )
    c.menuItem(  label="New Right", radialPosition="E", optionBox=True,
                    command="JSE.split('"+ctrl+"','right',False)" )

    c.menuItem(  label="New Left", radialPosition="W",
                    command="JSE.split('"+ctrl+"','left',True)" )
    c.menuItem(  label="New Left", radialPosition="W", optionBox=True,
                    command="JSE.split('"+ctrl+"','left', False)" )

    c.menuItem(  label="New Below", radialPosition="S",
                    command="JSE.split('"+ctrl+"','bottom',True)" )
    c.menuItem(  label="New Below", radialPosition="S", optionBox=True,
                    command="JSE.split('"+ctrl+"','bottom', False)" )

    c.menuItem(  label="New Above", radialPosition="N",
                    command="JSE.split('"+ctrl+"','top',True)" )
    c.menuItem(  label="New Above", radialPosition="N", optionBox=True,
                    command="JSE.split('"+ctrl+"','top', False)" )


    c.menuItem(  label="---Pane Menu (Alt)---", enable=False)
    c.menuItem(  label="Remove This Pane!",
                    command="JSE.deletePane('"+ctrl+"')")

    logger.debug(defEnd("Created Pane Menu"))
    logger.debug("")


################################################      InputRelated      ################################################

def inputPaneMethods(ctrl, method):
    global OutputSnapshotsPath
    logger.debug(defStart("Input method processing"))
    logger.debug(var1("ctrl",ctrl))
    logger.debug(var1("method",method))

    if method[:12] == "createScript":
        print "---Navigate tree and create tab on all layouts---"
        # c.cmdScrollFieldExecuter(sourceType=method[12:])

    elif method == "createExpression":
        print "---Need to create expression---"


    logger.debug(defEnd("Input method processed"))
    logger.debug("")


def makeInputTab(tabUsage, pTabLayout, tabLabel, fileLocation, exprDic={}):
    '''
        If there is no text then load from file
    '''
    logger.debug(defStart("Making input tab"))
    logger.debug(var1(    "tabUsage",tabUsage))
    logger.debug(var1(  "pTabLayout",pTabLayout))
    logger.debug(var1(    "tabLabel",tabLabel))
    logger.debug(var1("fileLocation",fileLocation))
    inputField = ""

    if tabUsage == "mel"     : bkgndColour = [0.16, 0.16, 0.16]
    if tabUsage == "expr"    : bkgndColour = [0.16, 0.13, 0.13]
    if tabUsage == "python"  : bkgndColour = [0.12, 0.14, 0.15]
    logger.debug(var1( "bkgndColour",bkgndColour))

    if tabUsage == "python"  : tabLang = "python"
    else                     : tabLang = "mel"
    logger.debug(var1(     "tabLang",tabLang))


    if tabUsage == "expr":
        exprPanelayout = c.paneLayout( parent = pTabLayout, configuration='vertical2')

        #========================================================================================================
        exprForm = c.formLayout( parent = exprPanelayout)
        #--------------------------------------------------------
        angleOption = c.optionMenu( parent = exprForm)
        option_All = c.menuItem(label="Convert All Units")
        option_Non = c.menuItem(label="None")
        option_Ang = c.menuItem(label="Angular only")
        #--------------------------------------------------------
        evalOption = c.optionMenu( parent = exprForm)
        option_OnD = c.menuItem(label="On Demand")
        option_Alw = c.menuItem(label="Always Evaluate")
        option_AfC = c.menuItem(label="After Cloth")
        c.optionMenu( evalOption, e=1, select = 2)
        #--------------------------------------------------
        defObject  = c.textField( parent = exprForm, placeholderText="Default Obj. e.g.pCube", w=150 )
        #--------------------------------------------------------
        inputField = c.cmdScrollFieldExecuter(  sourceType= "mel",
                                                backgroundColor = bkgndColour,
                                                parent=exprForm,

                                                showLineNumbers=True )
        logger.debug(var1("inputField",inputField))

        c.formLayout(exprForm, e=1, attachForm=([angleOption, "top", 0],
                                                [evalOption,  "top", 0],
                                                [defObject,   "top", 0],
                                                [defObject,   "right", 0],
                                                [inputField,  "bottom", 0],
                                                [inputField,  "right", 0],
                                                [inputField,  "left", 0]),

                          attachControl=([inputField, "top", 0, defObject],
                                         [defObject,  "left", 0, evalOption],
                                         [evalOption,  "left", 0, angleOption]) )

        #========================================================================================================
        attrForm = c.formLayout( parent = exprPanelayout)
        #--------------------------------------------------------
        objSearchField  = c.textFieldGrp( parent = attrForm, placeholderText="Search obj for attr", w=120 )
        attrList      = c.textScrollList( parent = attrForm, append=["--NOTHING FOUND--"], enable=False)

        c.textFieldGrp( objSearchField, e=1, textChangedCommand="JSE.listObjAttr('"+objSearchField+"','"+attrList+"')" )
        c.textScrollList(     attrList, e=1, doubleClickCommand="JSE.attrInsert('"+inputField+"','"+objSearchField+"','"+attrList+"')" )

        logger.debug(var1("textChangedCommand","JSE.listObjAttr('"+objSearchField+"','"+attrList+"')"))
        c.formLayout(attrForm, e=1, attachForm=([objSearchField, "top", 0],
                                                [objSearchField, "left", 0],
                                                [objSearchField, "right", 0],
                                                [attrList, "left", 0],
                                                [attrList, "right", 0],
                                                [attrList,  "bottom", 0]   ),
                                 attachControl=([attrList, "top", 0, objSearchField]) )
        tabLabel = c.expression(n=tabLabel)

        createExpressionMenu(exprPanelayout)
        createInputMenu(exprPanelayout)
        createPaneMenu(exprPanelayout)

    else:
        inputField = c.cmdScrollFieldExecuter(  sourceType= tabLang,
                                                backgroundColor = bkgndColour,
                                                parent=pTabLayout,

                                                showLineNumbers=True,
                                                spacesPerTab=4,
                                                autoCloseBraces=True,
                                                showTooltipHelp=True,
                                                objectPathCompletion=True,
                                                commandCompletion=True )
        logger.debug(var1("inputField",inputField))

        with open(fileLocation,"r") as bufferFile:
            c.cmdScrollFieldExecuter(inputField, e=1, text=bufferFile.read() )

        # make sure the text is not selected
        c.cmdScrollFieldExecuter(inputField, e=1, select=[0,0] )

        createScriptEditorMenu(inputField)
        createInputMenu(inputField)
        createPaneMenu(inputField)

    c.tabLayout(pTabLayout, e=1, tabLabel= [c.tabLayout(pTabLayout,
                                                        q=1, childArray=1)[-1] ,# Get the name of the newest tab child created
                                            tabLabel ] )                        # and rename that tab with our label



    logger.debug(defEnd("Made input tab"))
    return inputField


def createInputMenu( ctrl ):
    logger.debug(defStart("Creating Input Menu"))
    logger.debug(var1("ctrl",ctrl))

    c.popupMenu( parent=ctrl , shiftModifier=True, markingMenu=True) # markingMenu = Enable pie style menu

    c.menuItem(  label="Create Tab...", radialPosition="N", subMenu=True)
    c.menuItem(  label="Create Python", radialPosition="E",
                    command="JSE.inputPaneMethods('"+ctrl+"','createScriptpython')" )
    c.menuItem(  label="Create MEL", radialPosition="W",
                    command="JSE.inputPaneMethods('"+ctrl+"','createScriptmel')" )
    c.menuItem(  label="Create Expression", radialPosition="N",
                    command="JSE.inputPaneMethods('"+ctrl+"','createExpression')" )

    c.setParent("..", menu=True)
    c.menuItem(  label="---Input Menu (Shift)---", enable=False)
    c.menuItem(  label="Close this tab", radialPosition="N",
                    command="" )
    c.menuItem(  label="", command="")

    logger.debug(defEnd("Created Input Menu"))
    logger.debug("")


################################################   ExpressionRelated    ################################################

def attrInsert(cmdField, objSearchField, attrField):
    logger.debug(defStart("Inserting attribute to expression field"))
    logger.debug(var1(      "cmdField",cmdField))
    logger.debug(var1("objSearchField",objSearchField))
    logger.debug(var1(     "attrField",attrField))

    logger.debug(head2("Get selected attributes and combine with object string"))
    attrText = c.textScrollList(attrField, q=1, selectItem=1)[0].split(" ")[0]
    objText  = c.textFieldGrp(objSearchField, q=1, text=1)
    logger.debug( var1("attrText",attrText))
    logger.debug( var1( "objText",objText))

    logger.debug(head2("Insert it into the expression field (at current cursor pos)"))
    c.cmdScrollFieldExecuter(cmdField, e=1, insertText="{0}.{1}".format(objText, attrText))

    logger.debug(defEnd("Inserted attribute to expression field"))
    logger.debug("")


def listObjAttr(objTextField, scrollListToOutput):
    # If the current object is not valid then get outta here
    logger.debug(defStart("Listing object attributes") )
    logger.debug(var1(      "objTextField",objTextField))
    logger.debug(var1("scrollListToOutput",scrollListToOutput))

    c.textScrollList( scrollListToOutput, e=1, removeAll=1)
    objInQuestion = c.textFieldGrp( objTextField, q=1, text=1)
    logger.debug(var1(     "objInQuestion",objInQuestion))

    try:    attrLong = c.listAttr(objInQuestion)
    except:
        c.textScrollList( scrollListToOutput, e=1, append=["--NOTHING FOUND--"], enable=False)
        return
    attrShrt = c.listAttr(objInQuestion, shortNames=1)

    logger.debug(var1(          "attrLong",attrLong))
    logger.debug(var1(          "attrShrt",attrShrt))

    attrTxt = []
    for i,j in zip(attrLong,attrShrt):
        attrTxt.append( "{0} ({1})".format(i,j) )

    sorted(attrTxt)
    c.textScrollList( scrollListToOutput, e=1, append=attrTxt, enable=True)
    logger.debug(defEnd("Listed object attributes") )


def updateExpr(exprPanelayout):
    global currentInputTabLabels

    logger.debug(defStart("Creating/Saving Expression"))
    logger.debug(var1("exprPanelayout",exprPanelayout))

    logger.debug(head2("Get expression's formLayout, then it's children"))
    exprForm = c.layout(exprPanelayout,q=1,childArray=1)[0]

    convUnitMenu, evalMenu, defObjTxtField, cmdField = c.layout(exprForm,q=1,childArray=1)
    convUnitValue = c.optionMenu( convUnitMenu,  q=1, select=1)-1
    if   convUnitValue == 0: convUnitValue = "all"
    elif convUnitValue == 1: convUnitValue = "none"
    elif convUnitValue == 2: convUnitValue = "angularOnly"
    evalValue     = c.optionMenu(     evalMenu,  q=1, select=1)-1
    defObjText    = c.textField( defObjTxtField, q=1, text=1)
    exprText      = c.cmdScrollFieldExecuter( cmdField, q=1, text=1)

    logger.debug(head2("Get tab name for expression name"))
    tabChildShort = exprPanelayout.rsplit("|",1)[-1]
    logger.debug(var1( "tabChildShort", tabChildShort))
    logger.debug(var1("exprPanelayout", exprPanelayout))
    logger.debug(var1(      "(parent)", c.layout( exprPanelayout, q=1,parent=1)))
    allTabLabels = c.tabLayout( c.layout( exprPanelayout, q=1,parent=1), q=1, tabLabel=1)
    allTabChild  = c.tabLayout( c.layout( exprPanelayout, q=1,parent=1), q=1, ca=1)

    for i,j in zip(allTabLabels,allTabChild):
        if j==tabChildShort: currentTabLabel = i

    logger.debug(var1(       "exprText",exprText))
    logger.debug(var1("currentTabLabel",currentTabLabel))
    logger.debug(var1(     "defObjText",defObjText))
    logger.debug(var1(      "evalValue",evalValue))
    logger.debug(var1(  "convUnitValue",convUnitValue))

    c.expression(currentTabLabel,e=1, string=exprText,
                                        name=currentTabLabel,
                                      object=defObjText,
                              alwaysEvaluate=evalValue,
                              unitConversion=convUnitValue )


    c.cmdScrollFieldExecuter( cmdField, e=1, text=c.expression(currentTabLabel,q=1, string=1) )

    logger.debug(defEnd("Created/Saved Expression"))
    logger.debug("")


def createExpressionMenu( ctrl ):
    logger.debug(defStart("Creating Expression Menu"))
    logger.debug(var1("ctrl",ctrl))

    c.popupMenu( parent=ctrl , markingMenu=True) # markingMenu = Enable pie style menu
    c.menuItem(  label="New Expression", radialPosition="E",
                    command="JSE.logger.debug('New Expression')" )
    c.menuItem(  label="Save to file", radialPosition="W",
                    command="JSE.logger.debug('Save expression to file')" )
    c.menuItem(  label="Close Expression", radialPosition="S",
                    command="JSE.logger.debug('Unregister Expression')" )
    c.menuItem(  label="Update Expression", radialPosition="N",
                    command="JSE.updateExpr('"+ctrl+"')" )

    c.menuItem(  label="----Expression Menu----", enable=False)

    logger.debug(defEnd("Created Expression Menu"))
    logger.debug("")


################################################     OutputRelated      ################################################

def outputPaneMethods(ctrl, method, *arg):
    global OutputSnapshotsPath
    logger.debug(defStart("Output method processing"))
    logger.debug(var1("ctrl",ctrl))
    logger.debug(var1("method",method))

    if "snapshot" in method:
        newSnapshotFileName = OutputSnapshotsPath+c.date(format="YYYY-MMm-DDd-hhhmmmss.txt")
        logger.debug( var1("newSnapshotFileName", newSnapshotFileName ))

        with open(newSnapshotFileName,"w") as snapshotFile:
            snapshotFile.write(c.cmdScrollFieldReporter(ctrl, q=1, text=1))

        if "Wipe" in method:
            c.cmdScrollFieldReporter(ctrl, e=1, clear=1)
        logger.info("Snapshot saved to: %s",newSnapshotFileName)
        
        '''
        Currently we only permit a maximum of 20 snapshots, additional ones are deleted
        '''
        snapshotList = c.getFileList(folder=OutputSnapshotsPath, filespec='*' )
        logger.debug( var1("new snapshotList", snapshotList ))
        for i in snapshotList[20:]:
            logger.debug( var1("deleting", i ))
            c.sysFile(OutputSnapshotsPath+i,delete=1)

    if "Wipe" in method:
        c.cmdScrollFieldReporter(ctrl, e=1, clear=1)

    logger.debug(defEnd("Output method processed"))
    logger.debug("")


def createOutputMenu( ctrl ):
    logger.debug(defStart("Creating Output Menu"))
    logger.debug(var1("ctrl",ctrl))

    c.popupMenu( parent=ctrl , markingMenu=True) # markingMenu = Enable pie style menu
    c.menuItem(  label="Snapshot then Wipe", radialPosition="N",
                    command="JSE.outputPaneMethods('"+ctrl+"','snapshotWipe')" )
    c.menuItem(  label="Wipe", radialPosition="E",
                    command="JSE.outputPaneMethods('"+ctrl+"','Wipe')" )
    c.menuItem(  label="Snapshot", radialPosition="W",
                    command="JSE.outputPaneMethods('"+ctrl+"','snapshot')" )

    c.menuItem(  label="---Output Menu---", enable=False)
    c.menuItem(  label="", command="")


    c.popupMenu( parent=ctrl , shiftModifier=True, markingMenu=True) # markingMenu = Enable pie style menu
    c.menuItem(  label="Snapshot then Wipe", radialPosition="N",
                    command="JSE.outputPaneMethods('"+ctrl+"','snapshotWipe')" )
    c.menuItem(  label="Wipe", radialPosition="E",
                    command="JSE.outputPaneMethods('"+ctrl+"','Wipe')" )
    c.menuItem(  label="Snapshot", radialPosition="W",
                    command="JSE.outputPaneMethods('"+ctrl+"','snapshot')" )

    c.menuItem(  label="---Output Menu---", enable=False)
    c.menuItem(  label="", command="")

    logger.debug(defEnd("Created Output Menu"))
    logger.debug("")


################################################  Script EditorRelated  ################################################

def scriptEditorMethods(ctrl, method, *arg):
    global OutputSnapshotsPath
    global currentInputTabLabels
    global currentInputTabType
    global currentInputTabs
    logger.debug(defStart("Script editor method processing"))
    logger.debug(var1("ctrl",ctrl))
    logger.debug(var1("method",method))
    paneSection,parentPaneLayout = navigateToParentPaneLayout(ctrl) 
    logger.debug( var1("paneSection",paneSection))

    if method == "run":
        logger.debug(head2("Executing script text"))

        scriptIsMEL = ( c.cmdScrollFieldExecuter(ctrl, q=1, sourceType=1) == "mel" )
        logger.debug( var1("scriptIsMEL",scriptIsMEL) )

        if c.cmdScrollFieldExecuter(ctrl, q=1, hasSelection=1):  scriptToRun = c.cmdScrollFieldExecuter(ctrl, q=1, selectedText=1)
        else:                                                    scriptToRun = c.cmdScrollFieldExecuter(ctrl, q=1, text=1)

        logger.debug( var1("scriptToRun",scriptToRun) )

        saveInputTabs()

        if scriptIsMEL: melEval(scriptToRun)
        else:           c.evalDeferred(scriptToRun)

        logger.debug(head2("Executed script text") )

    elif method.startswith("save"):
        logger.debug(head2("Saving script") )
        global currentInputTabFiles
        logger.debug( var1("currentInputTabFiles",currentInputTabFiles))

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
        '''
        #   1/ Navigate to pane parent tab
        parentTabLay = paneSection+"|"+c.layout(paneSection, q=1, childArray=1)[0]
        logger.debug( var1("parentTabLay",parentTabLay))

        parentTabLayChildArray = c.tabLayout(parentTabLay,q=1, childArray=1)
        logger.debug( var2("childArray", parentTabLayChildArray ))
        logger.debug( var2("(len)",len(parentTabLayChildArray) ))

        # currentInputTabLabels = c.tabLayout(parentTabLay,q=1, tabLabel=1)
        # logger.debug( var2("tabLabel", currentInputTabLabels ))
        # logger.debug( var2("(len)",len(currentInputTabLabels) ))

        #   2/ Find out which tab index
        selectedTabIndex = c.tabLayout(parentTabLay,q=1, selectTabIndex=1)
        logger.debug( var1("selectedTabIndex", selectedTabIndex))

        #   3/ Get Pane file location using tab index
        # tabFileLocation = currentInputTabFiles[ c.tabLayout(parentTabLay,q=1, selectTabIndex=1)-1 ]
        # logger.debug( var1("tabFileLocation",tabFileLocation))

        #   4/ Find out if method[5:]=="As"
        logger.debug( var1("ends in As",method.endswith("As") ))

        #   5/ Do the boolean table to find out whether save as or save
        saveInputTabs()

        logger.debug( head2("Saving....") )
        if "All" in method:
            logger.debug( head2("Save all"))
            if method.endswith("As"):   saveInputTabs(range( 1, len(parentTabLayChildArray)+1 ),parentTabLay,parentTabLayChildArray,True)
            else:                       saveInputTabs(range( 1, len(parentTabLayChildArray)+1 ),parentTabLay,parentTabLayChildArray)
        else:
            logger.debug( head2("Save single"))
            if method.endswith("As"):   saveInputTabs( [selectedTabIndex-1],parentTabLay,parentTabLayChildArray,True)
            else:                       saveInputTabs( [selectedTabIndex-1],parentTabLay,parentTabLayChildArray)




        logger.debug(head2("Saved script") )



    if method == "open":
        logger.debug(head2("Loading script") )
        parentTabLay = paneSection+"|"+c.layout(paneSection, q=1, childArray=1)[0]
        parentTabLayChildArray = c.tabLayout(parentTabLay,q=1, childArray=1)
        selectedTabIndex = c.tabLayout(parentTabLay,q=1, selectTabIndex=1)
        
        cmdFieldShort    = parentTabLayChildArray[selectedTabIndex-1]
        currentInputTabs[   selectedTabIndex-1] = c.cmdScrollFieldExecuter(cmdFieldShort,q=1,fullPathName=1)
        currentInputTabType[selectedTabIndex-1] = c.cmdScrollFieldExecuter(cmdFieldShort,q=1,sourceType=1)
        
        tabCmdField      = currentInputTabs[   selectedTabIndex-1]
        tabSourceType    = currentInputTabType[selectedTabIndex-1]
        
        logger.debug( var1("cmdFieldShort",cmdFieldShort))
        logger.debug( var1("tabCmdField",tabCmdField))


        if currentInputTabType[selectedTabIndex-1] =="python":
            selectedFileFilter = "Python"
            fileFilter1 = "Python (*.py);;"
        else:
            selectedFileFilter = "MEL"
            fileFilter1 = "MEL (*.mel);;"


        retrievedFile = c.fileDialog2(fileMode=1,
                                      fileFilter= fileFilter1+"All Files (*.*)",
                                      selectFileFilter=selectedFileFilter,
                                      startingDirectory="./",
                                      dialogStyle=2)
        if retrievedFile:
            if method.endswith("ToNewTab"):
                logger.debug( head2("Need to open to new tab"))
            else:
                with open(retrievedFile,"r") as bufferFile:
                    c.cmdScrollFieldExecuter(currentInputTabs[selectedTabIndex-1], e=1, text=bufferFile.read() )
                currentInputTabFiles[ selectedTabIndex-1] = retrievedFile
                currentInputTabLabels[selectedTabIndex-1] = retrievedFile.rsplit("/",1)[-1]
                c.tabLayout( parentTabLay, e=1, tabLabel=[tabCmdField, retrievedFile.rsplit("/",1)[-1] ])

            logger.debug(head2("Loaded script") )


    logger.debug(defEnd("Script editor method processed"))
    logger.debug("")


def createScriptEditorMenu( ctrl ):
    logger.debug(defStart("Creating Script Editor Menu"))
    logger.debug(var1("ctrl",ctrl))

    c.popupMenu( parent=ctrl , markingMenu=True) # markingMenu = Enable pie style menu
    c.menuItem(  label="Run code", radialPosition="N",
                    command="JSE.scriptEditorMethods('"+ctrl+"','run')" )

    c.menuItem(  label="Save...", radialPosition="E", subMenu=True)
    c.menuItem(  label="Save", radialPosition="E",
                    command="JSE.scriptEditorMethods('"+ctrl+"','save')" )
    c.menuItem(  label="Save As", radialPosition="S",
                    command="JSE.scriptEditorMethods('"+ctrl+"','saveAs')" )
    c.menuItem(  label="Save All", radialPosition="N",
                    command="JSE.scriptEditorMethods('"+ctrl+"','saveAll')" )
    c.menuItem(  optionBox=True, radialPosition="N",
                    command="JSE.scriptEditorMethods('"+ctrl+"','saveAllAs')" )
    c.setParent("..",menu=1)
    c.menuItem(  label="Open File", radialPosition="W",
                    command="JSE.scriptEditorMethods('"+ctrl+"','open')" )
    logger.debug(defEnd("Created Script Editor Menu"))
    logger.debug("")


################################################      Maintainance      ################################################

def saveInputTabs(tabIndex=[],parentTabLay="",parentTabLayChildArray=[],saveAs=False):
    global currentInputTabType
    global currentInputTabLabels
    global currentInputTabFiles
    global currentInputTabs
    global InputBuffersPath
    ''' tab index   0   : Save all
                   >=1  : Save specific

    '''

    logger.debug(defStart("Saving input tabs"))

    logger.debug(var1("InputBuffersPath",InputBuffersPath))
    logger.debug(var1("tabIndex",tabIndex))
    logger.debug(var1("parentTabLayChildArray",parentTabLayChildArray))
    logger.debug(var1("saveAs",saveAs))
    #debugGlobals()

    """
    First clean up the currentInputTabs list so there is only 1 SET of active tabs
    otherwise we end up with non-existing controls that may spring errors

    --- TEMPORARY FIX ---

    """
    for i in range( len(currentInputTabs)):
        if c.control(currentInputTabs[i], q=1, exists=1):
            # ok this control exist, therefore take this "section" of the entire list and use it
            currentInputTabs = currentInputTabs[i: i+len(currentInputTabLabels)+1]
            break



    """
    Then delete the existing buffers in the temp location
    """
    for i in  c.getFileList( folder=InputBuffersPath, filespec='JSE*' ):
        c.sysFile(InputBuffersPath+i,delete=1)


    """
    Finally write the code in the current tabs to files
    """
    for i in range( len( currentInputTabType ) ):

        logger.debug(var1("(for loop) i",i))
        """
        If it is the default maya script editor, don't bother "Save to File" as this
        situation only happens when we are hijacking Maya's settings and contents
        """
        if match(".*/commandExecuter(-[0-9]+)?$",currentInputTabFiles[i]): currentInputTabFiles[i]=""

        logger.debug(var1("(for loop) currentInputTabType[i]",currentInputTabType[i]))
        if currentInputTabType[i] != "expr":
            if currentInputTabType[i] == "python": fileExt = "py"
            else: fileExt = "mel"
            c.cmdScrollFieldExecuter(currentInputTabs[i], e=1,
                                     storeContents=InputBuffersPath+"JSE-Tab-"+str(i)+"-"+currentInputTabLabels[i]+"."+fileExt)



            """
            Do the same for actual file paths that the script may be opened from
            """
            logger.debug(var1("not tabIndex",not tabIndex))
            if (not tabIndex and currentInputTabFiles[i]):
                try:
                    c.sysFile( currentInputTabFiles[i], delete=1)
                    c.cmdScrollFieldExecuter(currentInputTabs[i], e=1,
                                             storeContents = currentInputTabFiles[i] )
                except:
                    returnedButton = c.confirmDialog(message="Cannot save to :"+currentInputTabFiles[i], button=["Choose new location...","Cannot be bothered"] )
                    if returnedButton == "Cannot be bothered": currentInputTabFiles[i]=""
                    else:    
                        tabIndex = [i]
                        saveAs = True
                    print "Saved",currentInputTabFiles[i]

            if tabIndex:
                if tabIndex[0] == i and not saveAs and currentInputTabFiles[i]:
                    logger.debug(var1("(save) tabToSaveIndex",tabIndex[0]))
                    try:
                        c.sysFile( currentInputTabFiles[i], delete=1 )
                        c.cmdScrollFieldExecuter(currentInputTabs[i], e=1,
                                                 storeContents = currentInputTabFiles[i] )
                        tabIndex.pop(0)
                        print "Saved",currentInputTabFiles[i]
                    except:
                        returnedButton = c.confirmDialog(message="Cannot save to :"+currentInputTabFiles[i], button=["Choose new location...","Cannot be bothered"] )
                        if returnedButton == "Cannot be bothered": currentInputTabFiles[i]=""
                        else:      saveAs = True

                if saveAs or (not currentInputTabFiles[i] and not saveAs):
                    tabToSaveIndex = tabIndex.pop(0)
                    logger.debug(var1("(save as) tabToSaveIndex",tabToSaveIndex))
                    #   1/ Navigate to pane parent tab (done)
                    #   2/ Get tab label
                    tabLabel = currentInputTabLabels[tabToSaveIndex]

                    #   3/ Get tab language
                    tabCmdField = parentTabLayChildArray[tabToSaveIndex]
                    rawTabLang = c.cmdScrollFieldExecuter( tabCmdField, q=1, sourceType=1)

                    logger.debug(var1("fileExt",fileExt))
                    if fileExt =="py":
                        selectedFileFilter = "Python"
                        fileFilter1 = "Python (*.py);;"
                    else:
                        selectedFileFilter = "MEL"
                        fileFilter1 = "MEL (*.mel);;"

                    #   4/ File save dialog with label+language
                    returnedFile = c.fileDialog2(fileFilter= fileFilter1+"All Files (*.*)",
                                                 selectFileFilter=selectedFileFilter,
                                                 startingDirectory="./"+tabLabel,
                                                 dialogStyle=2)[0]
                    if returnedFile:
                        c.cmdScrollFieldExecuter( tabCmdField, e=1, storeContents=returnedFile )
                        currentInputTabFiles[ tabToSaveIndex] = returnedFile
                        currentInputTabLabels[tabToSaveIndex] = returnedFile.rsplit("/",1)[-1]
                        c.tabLayout( parentTabLay, e=1, tabLabel=[tabCmdField, returnedFile.rsplit("/",1)[-1] ])


        # make sure the text is not selected
        c.cmdScrollFieldExecuter(currentInputTabs[i], e=1, select=[0,0] )

    syncGlobals("store")
    logger.debug(defEnd("Saved input tabs"))
    logger.debug("")


def saveCurrentSettings():
    global currentInputTabType
    global currentInputTabLabels
    global currentInputTabFiles

    for i in currentInputTabType:  c.optionVar( stringValueAppend=("JSE_input_tabLangs",i) )
    for i in currentInputTabLabels: c.optionVar( stringValueAppend=("JSE_input_tabLabels",i) )
    for i in currentInputTabFiles:  c.optionVar( stringValueAppend=("JSE_input_tabFiles",i) )


def syncGlobals(direction):
    global currentInputTabType
    global currentInputTabLabels
    global currentInputTabFiles
    global currentInputTabs
    global currentInputTabLayouts

    if direction=="store":
        c.optionVar(clearArray="JSE_input_tabLangs")
        c.optionVar(clearArray="JSE_input_tabLabels")
        c.optionVar(clearArray="JSE_input_tabFiles")
        for i in currentInputTabType :  c.optionVar(stringValueAppend=["JSE_input_tabLangs" ,i])
        for i in currentInputTabLabels: c.optionVar(stringValueAppend=["JSE_input_tabLabels",i])
        for i in currentInputTabFiles : c.optionVar(stringValueAppend=["JSE_input_tabFiles" ,i])
    
    elif direction=="retrieve":
        currentInputTabType   = c.optionVar(q="JSE_input_tabLangs") # Get list of tabs' languages
        currentInputTabLabels = c.optionVar(q="JSE_input_tabLabels")# Get list of tabs' label/names
        currentInputTabFiles  = c.optionVar(q="JSE_input_tabFiles") # Get list of tabs' associated file addressess


def wipeOptionVars():
    logger.debug(defStart("Wiping JSE Option Vars"))
    for i in c.optionVar(list=True):
        if i[0:4] == "JSE_":
            c.optionVar(remove=i)
            logger.debug(var1("removed",i))
    logger.debug(defEnd("Option Vars Wiped"))


def wipeJSEfiles():
    global InputBuffersPath
    global OutputSnapshotsPath
    logger.debug(defStart("Wiping JSE Files"))
    logger.debug(var1("InputBuffersPath",InputBuffersPath))
    logger.debug(var1("OutputSnapshotsPath",OutputSnapshotsPath))
    try:
        for inputBufferFile in c.getFileList(folder=InputBuffersPath):
            logger.debug(var1("InputBuffersPath+file",InputBuffersPath+inputBufferFile))  
            if match("^JSE-Tab-[0-9]+-.+\.(py|mel)$", inputBufferFile):   
                c.sysFile(InputBuffersPath+inputBufferFile, delete=1)
                logger.debug(var1("Deleted",inputBufferFile))    
        
        for outputSnapshotFile in c.getFileList(folder=OutputSnapshotsPath):
            logger.debug(var1("OutputSnapshotsPathPath+file",OutputSnapshotsPath+outputSnapshotFile))
            if match("^[0-9]{4}-[0-9]{2}m-[0-9]{2}d-[0-9]{2}h[0-9]{2}m[0-9]{2}.txt$", outputSnapshotFile): 
                c.sysFile(OutputSnapshotsPath+outputSnapshotFile, delete=1)
                logger.debug(var1("Deleted",outputSnapshotFile))   
    except:
        logger.error(head1("Unable to wipe files, try running JSE first"))
        return
    
    logger.debug(defEnd("JSE Files Wiped"))


################################################      DebugRelated      ################################################

def createDebugMenu( ctrl ):
    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug(defStart("Creating Debug Menu"))
        logger.debug(var1("ctrl",ctrl))

        c.popupMenu( parent=ctrl , markingMenu=True,
                     shiftModifier=True, ctrlModifier=True, altModifier=True ) # markingMenu = Enable pie style menu
        c.menuItem(  label="wipeOptionVars", radialPosition="E",
                        command="JSE.wipeOptionVars()" )
        c.menuItem(  label="refreshAllScematic", radialPosition="W",
                        command="JSE.refreshAllScematic()" )
        c.menuItem(  label="debugGlobals", radialPosition="S",
                        command="JSE.debugGlobals()" )
        c.menuItem(  label="Reload", radialPosition="N",
                        command="reload(JSE)" )

        c.menuItem(  label="Run in... [SetLevel]", enable=False)
        c.menuItem(  label="Debug",  command="JSE.run(0,JSE.logging.DEBUG)")
        c.menuItem(  optionBox=True, command="JSE.logger.setLevel(JSE.logging.DEBUG)")
        c.menuItem(  label="Info",   command="JSE.run(0,JSE.logging.INFO)")
        c.menuItem(  optionBox=True, command="JSE.logger.setLevel(JSE.logging.INFO)")
        c.menuItem(  label="Error",  command="JSE.run(0,JSE.logging.ERROR)")
        c.menuItem(  optionBox=True, command="JSE.logger.setLevel(JSE.logging.ERROR)")


        logger.debug(defEnd("Created Debug Menu"))
        logger.debug("")


def layoutJSE():
    logger.debug(defStart("Layout JSE"))
    def recursiveLayoutTraverse(JSELayout, layerNum):
        layoutChildArray = c.layout(JSELayout, q=1, ca=1)
        if layoutChildArray:
            for i in c.layout(JSELayout, q=1, ca=1):
                for tabs in range(layerNum): print "\t",
                print i
                try:
                    c.layout(i, q=1, ca=1)
                    recursiveLayoutTraverse(i, layerNum+1)
                except:
                    pass

    global layout

    recursiveLayoutTraverse(layout, 0)

    logger.debug(defEnd("Layout JSE"))
    logger.debug("")
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


def debugGlobals():
    global currentInputTabType
    global currentInputTabLabels
    global currentInputTabFiles
    global currentInputTabs
    global currentInputTabLayouts
    global currentPaneScematic
    global currentAllSchematic
    global engaged

    logger.debug(defStart("JSE Debug Globals"))
    logger.debug("                      engaged: %s",engaged)
    logger.debug("   currentInputTabType, size : %s",len(currentInputTabType))
    logger.debug("%s",currentInputTabType)
    logger.debug("")
    logger.debug(" currentInputTabLabels, size : %s",len(currentInputTabLabels))
    logger.debug("%s",currentInputTabLabels)
    logger.debug("")
    logger.debug("  currentInputTabFiles, size : %s",len(currentInputTabFiles))
    logger.debug("%s",currentInputTabFiles)
    logger.debug("")
    logger.debug("")
    logger.debug("      currentInputTabs, size : %s",len(currentInputTabs))
    for i in currentInputTabs: logger.debug(i)
    logger.debug("")
    logger.debug("")
    logger.debug("currentInputTabLayouts, size : %s",len(currentInputTabLayouts))
    logger.debug("%s",currentInputTabLayouts)
    logger.debug("")
    logger.debug("   currentPaneScematic, size : %s",len(currentPaneScematic))
    logger.debug("%s",currentPaneScematic)
    logger.debug("")
    logger.debug("    currentAllSchematic, size : %s",len(currentAllSchematic))
    logger.debug("%s",currentAllSchematic)
    logger.debug(defEnd("JSE Debug Globals"))
    logger.debug("")

##################################################################################################################


def run(dockable=False, loggingLevel=logging.INFO):
    global currentInputTabLayouts
    global currentAllSchematic
    global currentPaneScematic
    global InputBuffersPath
    global OutputSnapshotsPath
    global engaged

    # Logger levels: CRITICAL ERROR WARNING INFO DEBUG NOTSET
    logger.setLevel(loggingLevel)

    logger.debug("")
    logger.debug(head1("JSE called"))
    debugGlobals()

    #---- Setup ----
    JSE_Path = c.about(preferences=1)+"/prefs/JSE/"
    c.sysFile(JSE_Path,makeDir=True)

    InputBuffersPath = JSE_Path+"InputBuffers/"
    c.sysFile(InputBuffersPath,makeDir=True)

    OutputSnapshotsPath = JSE_Path+"OutputSnapshots/"
    c.sysFile(OutputSnapshotsPath,makeDir=True)


    window = c.window(title="JSE", width=950, height=650)
    currentAllSchematic.append([])
    # currentInputTabLayouts.append( c.paneLayout() )
    # newPaneLayout = split( currentInputTabLayouts[-1] )
    refreshAllScematic()
    debugGlobals()
    constructJSE(  c.paneLayout(), deepcopy(currentPaneScematic) )
    refreshAllScematic()

    # Re-populate
    # for i in xrange(0, len(currentAllSchematic[-1]), 2):
    #     currentPaneScematic.append(currentAllSchematic[-1][i])

    engaged = True
    saveInputTabs()

    if dockable:
        c.dockControl(area='left',floating=True,content=window)
        logger.info(head1("Dockable JSE created" ))
    else:
        c.showWindow(window)
        logger.info(head1("Standard JSE created" ))
    logger.debug("")




# End of script, if you want to to run it from just import
# run(0)
