



import maya.cmds as c

'''
=== TERMINOLOGY GUIDE ===
    
    Input   =   The pane section with the tabs and command line
    Output  =   The pane section with the output console
    

'''

currentInputTabLangs = []   # List of tabs' languages
currentInputTabLabels = []  # List of tabs' label/name
currentInputTabFiles = []   # List of tabs' associated file location
currentInputTabs = []       # List of cmdScrollFieldExecuters, will be in order of the tabs (left to right I presume)

def run(dockable):
    print "JSE called ------------------"
    #---- Setup ----
    window = c.window()
    layout = c.paneLayout() 
    newPaneLayout = split(layout)
    if dockable: 
     c.dockControl("JSE",area='left',floating=True,content=window)
     print "Dockable",
    else: 
     c.showWindow(window)
     print "Standard",
    print "JSE created ------------------"

  
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

        import re.split
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
                        setPane=[parentPaneLayoutChildren[otherPaneChildNum], parentPaneLayoutSectionNumber])
        c.deleteUI( parentPaneLayout )

def createMenus( ctrl ):
    print 'called create menu with '+str(ctrl)+'...........'
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
                    

def createOutput( parentPanelLayout ):
    output = c.cmdScrollFieldReporter(parent = parentPanelLayout)
    createMenus( output )
    print "output created...."
    return output

def buildInputTab( language , name ):
    currentInputTabs.append( c.cmdScrollFieldExecuter( sourceType=language ) )
    
def createInput( parentUI ):
    inputLayout = c.formLayout(parent = parentUI) # formLayout that will hold all the tabs and command line text field
    inputTabsLay = c.tabLayout() # tabLayout that will hold all the input tab buffers
    '''
    if c.optionVar(exists="JSE_input_tabLangs"): # Has JSE been used before? (It would have stored this variable)
    # (YES)
        currentInputTabLangs  = c.optionVar(q="JSE_input_tabLangs") # Get list of tabs' languages
        currentInputTabLabels = c.optionVar(q="JSE_input_tabLabels")# Get list of tabs' label/names
        currentInputTabFiles  = c.optionVar(q="JSE_input_tabFiles") # Get list of tabs' associated file addressess
    else: # (NO)
        from maya.mel import eval as melEval
        if melEval("$workaroundToGetVariables = $gCommandExecuterType"): # What about Maya's own script editor, was it used?
            # (YES) Retrieve existing tabs' languages from the latest Maya script editor state
            
            # Here we use a workaround to get a variable from MEL (http://help.autodesk.com/cloudhelp/2015/ENU/Maya-Tech-Docs/CommandsPython/eval.html, example section)
            currentInputTabLangs  = melEval("$workaroundToGetVariables = $gCommandExecuterType")
            currentInputTabLabels = melEval("$workaroundToGetVariables = $gCommandExecuterName")
        else: # (NO)
            print "===Maya's own script editor, wasn't used!! NUTS!==="
            currentInputTabLangs  = []
            currentInputTabLabels = []
            
        currentInputTabFiles = []
    if (currentInputTabLangs == []):
    '''    
    buildInputTab( "python" , "py")
    buildInputTab( "python" , "thon")
    buildInputTab( "mel" , "mel")
    buildInputTab( "mel" , "alal")
    '''
    currentInputTabs.append( c.cmdScrollFieldExecuter(sourceType="python") )
    currentInputTabs.append( c.cmdScrollFieldExecuter(sourceType="mel") )
    '''
    
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
    
    for tab in currentInputTabs:
        createMenus( tab )
    print "input created...."
    return inputLayout

def saveCurrentSettings():
    for i in currentInputTabLangs: c.optionVar( stringValueAppend=("JSE_input_tabLangs",i) ) 
    
    
    
def setPane( paneType ):
    print "wharddupppp"
