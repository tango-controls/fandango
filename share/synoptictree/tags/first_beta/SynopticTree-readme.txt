

Sergi Rubio Manrique, srubio@cells.es, 
ALBA Control System group

13th November 2007: The SynopticTree is more or less up 
to date in the SVN repository (cells)

  Note: The Synoptic Tree is an application still under 
  development and it cannot be still considered as 1.0 
  release. There's some alternative codes still present 
  in this files that I will remove as soon as I 
  continue with the development.

------------------------------------------------------------
 Summary of changes from original device tree
------------------------------------------------------------

  Class explorer.ViewerMain
------------------------------------------------------------
Modified graph background (now is white instead of 
grey). It has been done by replacing the 
graph_background property while reading the file ... 
probably it's not the best way to do it.

  Class explorer.AdminMain
------------------------------------------------------------
The Synoptic parsing was initially added to this class 
... but finally all of it has been moved to a different class.

  Class explorer.SynopticMain (modified from explorer.AdminMain)
------------------------------------------------------------
SynopticMain is created to separate DeviceTree and 
SynopticTree code.

* Background of graphs changed.

* It was added capability of configuring composer servers.

* The methods setSynoptic amd loadJDObjects were added.

* TreeInitialization varies if a Synoptic has been loaded

* PopUp Menu for new Node types (HierarchyNode) has 
  been aded

* add2Table modified, now commands and attributes share 
  the same TabPanel

* The new Node types for the ATK Tree has been added in 
  an ATK patch (ATKmod.jar).

* Now SynopticMain overrides the framework 
  initialization (initComponents(...))

* It allows to open a device tree xml file linked to a 
  Synoptic (called AttributesProfile); it can be done 
  at startup or from a PopUp Menu.

* Problems with JDraw synoptic resizing solved.

  Package explorer.ui
------------------------------------------------------------
* Class RunUi modified to be able to launch JDraw and Mambo.

* Class FileUi, now it can close a file and also open 
  jdraw files instead of devtree xml.

* Class FileHandler, now it's able to close files.
