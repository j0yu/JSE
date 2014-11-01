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

  
def split( parentPane, re_assign_position="" ):
    '''
    re_assign_position:   ""   Only for initial creation, creates new default split pane, otherwise...
    
                    "bottom",  New pane position for existing pane, which will then be  
                      "left",  used to figure out the pane number for setPane flag and  
                     "right",  horizontal/vertical for configuration flag for c.paneLayout()
                       "top"
    '''
    # global splitsArray
    print 'split called with '+parentPane+' and '+re_assign_position
    if re_assign_position == "":
        # print len(splitsArray)
        newPaneLayout = c.paneLayout(configuration='vertical2',parent=parentPane)
        # print len(splitsArray)
        # JSE_output_ctrl = c.cmdScrollFieldReporter()
        # JSE_input_ctrl  = c.cmdScrollFieldExecuter()
        
        c.paneLayout(newPaneLayout, edit=True, 
                     setPane=[ (createOutput( newPaneLayout ) , 1),
                               (createInput(  newPaneLayout ) , 2) ] )
        return newPaneLayout
        
    if re_assign_position == "top":    
        pass                    
    if re_assign_position == "bottom": 
        pass                       
    if re_assign_position == "left":
        parentPaneLayout = parentPane
        while not( c.paneLayout( parentPaneLayout, query=True, exists=True) ):
            print "parentPaneLayout is ------ ",parentPaneLayout
            parentPane = parentPaneLayout
            parentPaneLayout = c.control(parentPaneLayout, query=True, parent=True)
        
        #---------------------------- DEBUG ------------------------------------
        print "parent paneLayout is ----- ",parentPaneLayout
        print "           child is ------ ",parentPane,"---",c.control(parentPane,q=1,ex=1)        
        import re
        parentPaneShort = re.split("\|",parentPane)[-1]        
        print "           (short)  ------ ",parentPaneShort
        parentPaneLayoutChildArray = c.paneLayout( parentPaneLayout, query=True, ca=True)
        print "parentPaneLayout children- ",parentPaneLayoutChildArray
        print "       child index number- ",parentPaneLayoutChildArray.index(parentPaneShort)
        #---------------------------- END OF DEBUG ------------------------------------
        
        # print len(splitsArray)        
        newPaneLayout =  c.paneLayout(configuration='vertical2',parent=parentPaneLayout) 
        print newPaneLayout, c.paneLayout(newPaneLayout, q=1,ex=1)
        # print len(splitsArray)
        
        # c.paneLayout(splitsArray[-2], edit=True, 
        c.paneLayout(parentPaneLayout, edit=True, 
                     setPane=[( newPaneLayout, parentPaneLayoutChildArray.index(parentPaneShort)+1 )]  )   
        print "assigning new split to current pane................."
        c.control(parentPane, edit=True, parent=newPaneLayout)
        c.paneLayout(newPaneLayout, edit=True, 
                     setPane=[ (createOutput( newPaneLayout ) , 1),
                               (parentPane , 2) ] )  

        
        pass # vertical2, 1                     
    if re_assign_position == "right":     
        pass # vertical2, 2                                             
    

def createMenus( ctrl ):
    print 'called create menu with '+str(ctrl)+'...........'
    c.popupMenu( parent=ctrl )
    c.menuItem(  radialPosition="W", command="JSE.split('"+ctrl+"','left')" )

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