#!/bin/sh

MOD="$1"

if [ ! "$MOD" ] ; then MOD="../fandango" ; fi

TARGET=$(pwd)/autodoc

echo "Generating $MOD documentation at $TARGET"

if [ -e $MOD/.svn ] || [ -e $MOD/.git ] ; then
 echo "Execute this method only on exports!, not checkouts!!!"
 echo "exiting ..."
 exit 1
fi

if [ ! -e $TARGET ] ; then mkdir $TARGET; fi
cp *rst $TARGET/
if [ -e README ] ; then cp README $TARGET ;
elif [ -e ../README ] ; then cp ../README $TARGET ; fi
if [ -e conf.py ] ; then cp conf.py $TARGET ; 
elif [ -e $MOD/doc/conf.py ] ; then cp $MOD/doc/conf.py $TARGET ; fi
if [ -e $MOD/doc/index.rst ] ; then cp $MOD/doc/index.rst $TARGET ; fi

CMD="sphinx-apidoc -F -e -o $TARGET $MOD"
$CMD
cd $TARGET
make html
ln -s _build/html

