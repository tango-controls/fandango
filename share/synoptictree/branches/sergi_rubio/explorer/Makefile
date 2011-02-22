include ../../../.make-include

BEANINFO=

ALL = $(TARGET)/CommandTable.class                    \
      $(TARGET)/CommandTableModel.class               \
      $(TARGET)/EntityTable.class                     \
      $(TARGET)/EntityTableModel.class                \
      $(TARGET)/EntityAdapter.class                   \
      $(TARGET)/AttributePanel.class                  \
      $(TARGET)/AttributeTableModel.class             \
      $(TARGET)/MyCellRenderer.class                  \
      $(TARGET)/AttributeTable.class                  \
      $(TARGET)/ViewDialog.class                      \
      $(TARGET)/SetDialog.class                       \
      $(TARGET)/DeviceAliasDialog.class               \
      $(TARGET)/EntityAliasDialog.class               \
      $(TARGET)/About.class                           \
      $(TARGET)/Preferences.class                     \
      $(TARGET)/FileManager.class                     \
      $(TARGET)/Main.class                            \
      $(TARGET)/AdminMain.class                       \
      $(TARGET)/ViewerMain.class                      \
      $(TARGET)/Test.class                            \
      $(TARGET)/Status.class                          \
      $(TARGET)/ColumnListener.class                  \
      $(TARGET)/BooleanViewer.class                   \
      $(TARGET)/DeviceList.class                      \
      $(TARGET)/DeviceTreeFileException.class         \






all: ui-all html $(ALL)
	$(J)

test:	all
	$(JAVA) apps.explorer.Test

ui-all:
	(cd ui && $(MAKE) all)

clean: ui-clean class-clean

ui-clean:
	(cd ui && $(MAKE) clean)
html:
	cp *.html $(TARGET)/

run: all
	$(JAVA) -DHOST="soleil" apps.explorer.Main test.xml

runa: all
	$(JAVA) apps.explorer.Main

atab: all
	$(JAVA) apps.explorer.AttributeTable	

ps: all
	$(JAVA) apps.explorer.PropertyDialog

pd: all
	$(JAVA) apps.explorer.PreferencesDialog