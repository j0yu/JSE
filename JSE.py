import maya.cmds as c

# splitsArray = []

def run():
    # global splitsArray
    
    print "JSE called ------------------"
    #---- Setup ----
    window = c.window()
    layout = c.formLayout() 
    newPaneLayout = split(layout)
    
    #---- Attach and snap controls to main layout ----
    c.formLayout(layout, edit=True, 
                 attachForm=[ ( newPaneLayout, 'top', 0 ),
                              ( newPaneLayout, 'left', 0 ),
                              ( newPaneLayout, 'right', 0 ),
                              ( newPaneLayout, 'bottom', 0 )
                            ])
    c.showWindow(window)
    print "JSE created ------------------"

  
def split( paneSection, re_assign_position="" ):
    '''
    re_assign_position:   ""   Only for initial creation, creates new default split pane, otherwise...
    
                    "bottom",  New pane position for existing pane, which will then be  
                      "left",  used to figure out the pane number for setPane flag and  
                     "right",  horizontal/vertical for configuration flag for c.paneLayout()
                       "top"
    '''

    print 'split called with '+paneSection+' and '+re_assign_position
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
            Setup values for new paneLayout setup and assingment of new/existing panes......
            ....tbc....
            
            paneConfig          :   --
            newPaneLayout       :   --
            newSectionPaneIndex :   --
            oldSectionPaneIndex :   --

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
                     setPane=[ (createOutput( newPaneLayout ) , newSectionPaneIndex),
                               (        paneSection           , oldSectionPaneIndex) ] )  

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
                    

def createOutput( parentPanelLayout ):
    output = c.cmdScrollFieldReporter(parent = parentPanelLayout)
    createMenus( output )
    print "output created...."
    return output
    
def createInput( parentUI ):
    inputLayout = c.formLayout(parent = parentUI)
    inputTabsLay = c.tabLayout()
    inputTabs = []
    inputTabs.append( c.cmdScrollFieldExecuter(sourceType="python") )
    inputTabs.append( c.cmdScrollFieldExecuter(sourceType="mel") )
    inputCmdLine = c.textField(parent= inputLayout)
    
    c.formLayout(inputLayout, edit=True,
                 attachForm=[ (inputTabsLay, "top", 0),    # Snapping the top, left and right edges
                              (inputTabsLay, "left", 0),   # of the tabLayout to the edges of the
                              (inputTabsLay, "right", 0),  # formLayout
                              
                              (inputCmdLine, "left", 0),    # Snapping the bottom, left and right edges 
                              (inputCmdLine, "right", 0),   # of the cmdLine to the edges of the
                              (inputCmdLine, "bottom", 0) ],# formLayout
                              
                 attachControl=(inputTabsLay, "bottom", 0, inputCmdLine) )
                 # Snap the bottom of the tabLayout to the top of cmdLine
    
    for tab in inputTabs:
        createMenus( tab )
    print "input created...."
    return inputLayout

def setPane( paneType ):
    print "wharddupppp"