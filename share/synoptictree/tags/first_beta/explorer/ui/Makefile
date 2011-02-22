include ../../../../.make-include

ALL = $(TARGET)/RefreshUI.class                       \
      $(TARGET)/FileUI.class                          \
      $(TARGET)/EditUI.class                          \
      $(TARGET)/RunUI.class                           \
      $(TARGET)/UIBit.class                           \
      $(TARGET)/RefreshDialog.class                   \
      $(TARGET)/UIDialog.class                        \
      $(TARGET)/PreferencesDialog.class               \
      $(TARGET)/Refresher.class                       \
      $(TARGET)/FileHandler.class                     \
      $(TARGET)/Clearable.class                       \
      $(TARGET)/Dialog.class                          \
      $(TARGET)/DTMenuBar.class                       \


all: html $(ALL)
	$(J)

html:
	cp *.html $(TARGET)/


clean: class-clean

run: all
	$(JAVA) apps.explorer.ui.UIDialog
