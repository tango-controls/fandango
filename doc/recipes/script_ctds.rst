=============================
ctds start/stop/search/create
=============================

Using fandango/scripts/ctds to start/stop/search/create devices

   91  ./ctds list "*"
   92  ./ctds status "*"
   96  ./ctds create AlbaPLC/plctest16 AlbaPLC lab/ct/plctest16
   97  ./ctds list "*"
  109  ./fandango/scripts/ctds export lab/ct/plctest16 lab/ct/plctest16-mbus > /tmp/plctest16.dct
  121  ctds stop "*plctest16-mbus"
  129  ./fandango/scripts/ctds  stop "*/*plctest*"
  132  ./fandango/scripts/ctds status "*/*/*plctest*"
  133  ./fandango/scripts/ctds start "*/*/*plctest*"
