import pymel.core as pm

def run():
    print "JSE called ------------------"
    #---- Setup ----
    window = pm.window()
    layout = pm.paneLayout() 
    split(layout)
    pm.showWindow(window)
    print "JSE created ------------------"

  
def split( paneSection, re_assign_position="" ):
    '''
    Procedure to split the current pane into 2 panes, or set up the default
    script editor panels if this is the first time it is run
    
    
    re_assign_position:       "",  Only for initial creation, creates new default split pane, otherwise...
                        "bottom",  New pane position for existing pane, which will then be  
                          "left",  used to figure out the pane number for setPane flag and  
                         "right",  horizontal/vertical for configuration flag for pm.paneLayout()
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
        newPaneLayout = pm.paneLayout(configuration='vertical2',parent=paneSection)        
        newPaneLayout.setPane([ (createOutput( newPaneLayout ) , 1),
                                (createInput(  newPaneLayout ) , 2) ] )
        # return newPaneLayout
    else:
        print "\n\n\n"
        print paneSection
        print `paneSection`
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
        while not( pm.paneLayout(parentPaneLayout, exists=True) ):
            # print "parentPaneLayout is ------ ",parentPaneLayout
            paneSection = parentPaneLayout
            parentPaneLayout = parentPaneLayout.parent
        
        #---------------------------- DEBUG ------------------------------------
        # print "parent paneLayout is ----- ",parentPaneLayout
        # print "           child is ------ ",paneSection,"---",pm.control(paneSection,q=1,ex=1)        
        # import re
        # paneSectionShortName = re.split("\|",paneSection)[-1]        
        # print "           (short)  ------ ",paneSectionShortName
        # parentPaneLayoutChildArray = pm.paneLayout( parentPaneLayout, query=True, ca=True)
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
        print parentPaneLayout
        print `parentPaneLayout`
        paneSectionNumber = parentPaneLayout.getChildArray().index(paneSectionShortName)+1
        
        
        

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
    
        newPaneLayout =  pm.paneLayout(configuration=paneConfig, parent=parentPaneLayout) 
        # print newPaneLayout, pm.paneLayout(newPaneLayout, q=1,ex=1)
        pm.paneLayout(parentPaneLayout, edit=True, 
                     setPane=[( newPaneLayout, paneSectionNumber )]  )   
        # print "assigning new split to current pane................."
        pm.control(paneSection, edit=True, parent=newPaneLayout)
        pm.paneLayout(newPaneLayout, edit=True, 
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
        while not( pm.paneLayout( parentPaneLayout, query=True, exists=True) ):
            paneSection = parentPaneLayout
            parentPaneLayout = pm.control(parentPaneLayout, query=True, parent=True)
            
        ''' --- SECOND ---
                Figure out which indices the various children of the different pane layouts
                are, as well as the grand parent layout. Can't forget about the grannies
            
        '''
        parentPaneLayoutChildren        = pm.paneLayout( parentPaneLayout, query=True, childArray=True)
        grandParentPaneLayout           = pm.paneLayout( parentPaneLayout, query=True, parent=True)
        grandParentPaneLayoutChildren   = pm.paneLayout( grandParentPaneLayout, query=True, childArray=True)

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
        pm.control( parentPaneLayoutChildren[otherPaneChildNum], edit=True, parent=grandParentPaneLayout)
        pm.paneLayout( grandParentPaneLayout, edit=True, 
                        setPane=[parentPaneLayoutChildren[otherPaneChildNum], parentPaneLayoutSectionNumber])
        pm.deleteUI( parentPaneLayout )

def createMenus( ctrl ):
    print 'called create menu with '+str(ctrl)+'...........'
    print ctrl
    print `ctrl`
    pm.popupMenu( parent=ctrl , markingMenu=True) # markingMenu = Enable pie style menu
    pm.menuItem(  label="Right", radialPosition="E", 
                    command=pm.Callback( split , `ctrl`, "right" ) )
    pm.menuItem(  label="Left", radialPosition="W", 
                    command="split('"+ctrl+"','left')" )
    pm.menuItem(  label="Below", radialPosition="S", 
                    command="split('"+ctrl+"','bottom')" )
    pm.menuItem(  label="Above", radialPosition="N", 
                    command="split('"+ctrl+"','top')" )
    pm.menuItem(  label="Hey you! Choose new section location...", enable=False)
    pm.menuItem(  label="Remove This Pane!", 
					command="JSE.deletePane('"+ctrl+"')")
                    

def createOutput( parentPanelLayout ):
    output = pm.cmdScrollFieldReporter(parent = parentPanelLayout)
    createMenus( output )
    print "output created...."
    return output
    
def createInput( parentUI ):
    inputLayout = pm.formLayout(parent = parentUI)
    inputTabsLay = pm.tabLayout()
    inputTabs = []
    inputTabs.append( pm.cmdScrollFieldExecuter(sourceType="python") )
    inputTabs.append( pm.cmdScrollFieldExecuter(sourceType="mel") )
    inputCmdLine = pm.textField(parent= inputLayout)
    
    pm.formLayout(inputLayout, edit=True,
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

run()