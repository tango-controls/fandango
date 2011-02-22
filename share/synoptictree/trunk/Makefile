
## SOURCES = ./sources
## CLASSES = ./classes
#CLASSPATH = liquidlnf.jar:$(TANGO_HOME)/share/tango/java/Jive.jar:$(TANGO_PATH)
JAVADIR = $(SICILIA)/lib/java
CLASSPATH = liquidlnf.jar:$(JAVADIR)/Jive.jar:$(JAVADIR)/atkpanel.jar:$(JAVADIR)/ATKCore.jar:$(JAVADIR)/ATKWidget.jar:$(JAVADIR)/TangORB.jar

default: Synoptic

#all:	ATK Synoptic
all:	Synoptic

ATK: 	ATKmod ATKjar

#Synoptic:	java5 jar
Synoptic: java jar

java: java5

first:
	echo CLASSPATH=$(CLASSPATH) | less
	mkdir ./classes
	mkdir ./classes/explorer
	mkdir ./classes/tree
	mkdir ./classes/api
	mkdir ./classes/api/java
	mkdir ./classes/jserver
	mkdir ./classes/jserver/archiving
	mkdir ./classes/tools
	mkdir ./classes/tools/mambo
	mkdir ./classes/fr	

java4:
	javac -d ./classes -g -nowarn -cp ATKmod.jar:$(CLASSPATH) -Xlint -source "1.4" -target "1.4" explorer/AdminMain.java fr/esrf/tangoatk/widget/jdraw/*.java fr/esrf/tangoatk/widget/util/jdraw/*.java 2>&1 | less

JDraw:
	javac -cp $(THE_PATH) -d . -sourcepath . `find -iname "*.java"`
	jar -cvf $(JARNAME) `find fr ! -iname "*.java" -and ! -type d | grep -v "CVS"`

java5:
	javac -d ./classes -g -nowarn -cp ATKmod.jar:$(CLASSPATH) -sourcepath . `find -iname "*.java"` 2>&1 | grep -v "\[unchecked\]" | less
##	javac -g -cp $CLASSPATH -d $(CLASSES) -sourcepath $(SOURCES) `find $(SOURCES) -iname "*.java"`

jar:
	cp -rf `find explorer/ui -iname "*.gif"` ./classes/explorer/ui
	cp -rf `find widget.icons -iname "*.gif"` ./classes/fr/esrf/tangoatk/widget/icons
	cp -rf `find widget.util.jdraw/gif/ -iname "*.gif"` ./classes/fr/esrf/tangoatk/widget/util/jdraw/gif/
	jar cvf SynopticTree.jar `find classes ! -iname "*.java" -and ! -type d | grep -v "CVS" | sed "s/classes\///" | sed "s/.*/-C .\/classes &/"`

clean:
	rm -vf `find -L -iname "*.class"` 
	rm -vf `find -P -iname "*~"` 
	rm -vf `find -P -iname "SynopticTree.jar"`

cleanATK:
	rm -vf `find -P -iname "ATKmod.jar"`

cleanALL: clean cleanATK
