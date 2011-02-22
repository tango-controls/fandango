
## SOURCES = ./sources
## CLASSES = ./classes
CLASSPATH = liquidlnf.jar:$(TANGO_HOME)/share/tango/java/Jive.jar:$(TANGO_PATH)

default: Synoptic

all:	ATK Synoptic

ATK: 	ATKmod ATKjar

Synoptic:	java5 jar

first:
	echo CLASSPATH=$(CLASSPATH) | less
# 	mkdir ./classes
# 	mkdir ./classes/api
# 	mkdir ./classes/api/java
# 	mkdir ./classes/jserver
# 	mkdir ./classes/jserver/archiving
# 	mkdir ./classes/tools
# 	mkdir ./classes/tools/mambo

java4:
	javac -d ./classes -g -nowarn -cp ATKmod.jar:$(CLASSPATH) -Xlint -source "1.4" -target "1.4" explorer/AdminMain.java fr/esrf/tangoatk/widget/jdraw/*.java fr/esrf/tangoatk/widget/util/jdraw/*.java 2>&1 | less

java5:
	javac -d ./classes -g -nowarn -cp ATKmod.jar:$(CLASSPATH) -Xlint explorer/*.java explorer/ui/*.java 2>&1 | grep -v "\[unchecked\]" | less
##	javac -g -cp $CLASSPATH -d $(CLASSES) -sourcepath $(SOURCES) `find $(SOURCES) -iname "*.java"`

jar:
	jar cvf SynopticTree.jar -C ./classes explorer
#	explorer/*.class explorer/ui/*.class explorer/html/* explorer/ui/*.gif explorer/.xvpics/*.gif doc/resources/inherit.gif | less
#	jar cvf ./classes/archiving.jar -C ./classes/jserver/archiving .

ATKmod:
	javac -d ./classes -g -nowarn -cp $(CLASSPATH) -Xlint fr/esrf/tangoatk/widget/jdraw/*.java fr/esrf/tangoatk/widget/util/jdraw/*.java fr/esrf/tangoatk/widget/device/Tree.java fr/esrf/tangoatk/widget/device/tree/*.java 2>&1 | grep -v "\[unchecked\]" | less

ATKjar:
	jar cvf ATKmod.jar -C ./classes fr/esrf/tangoatk/widget/jdraw -C ./classes fr/esrf/tangoatk/widget/util/jdraw -C ./classes fr/esrf/tangoatk/widget/device -C ./classes fr/esrf/tangoatk/widget/icons | less

clean:
	rm -vf `find -L -iname "*.class"` 
	rm -vf `find -P -iname "*~"` 
	rm -vf `find -P -iname "SynopticTree.jar"`

cleanATK:
	rm -vf `find -P -iname "ATKmod.jar"`

cleanALL: clean cleanATK
