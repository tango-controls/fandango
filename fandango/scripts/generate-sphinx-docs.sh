#!/bin/sh

## THIS SCRIPT WILL COPY ALL DOCUMENTATION TO A SEPARATE
# autodoc FOLDER TO AVOID MODIFYING ORIGINAL GIT CHECKOUT
# used in fandango and panic projects

MOD="$1"

if [ ! "$MOD" ] || [ "$(echo $MOD | grep '\-h' )" != "" ] ; then 
  echo "This script will search for .rst files and sources"
  echo "and will generate sphinx documentation in an autodoc/ folder"
  echo ""
  echo "Usage: "
  echo "      # git clone https://github.com/.../PROJECT PROJECT.git"
  echo "      # cd PROJECT.git/doc "
  echo "      # generate-sphinx-docs.sh ../PROJECT [--force] [--clean]"
  exit 1
fi

TARGET=$(pwd)/autodoc

echo "Generating $MOD documentation at $TARGET"

if [ "$(echo $* | grep '\-force')" == "" ]; then
 if [ -e $MOD/.svn ] || [ -e $MOD/.git ] ; then
  echo "Execute this method only on exports!, not checkouts!!!"
  echo "exiting ..."
  exit 1
 fi
fi

if [ "$(echo $* | grep '\-clean')" != "" ]; then
 echo "Removing $TARGET ..."
 rm -rf $TARGET
fi

if [ -e update.py ] ; then 
  python update.py ; 
fi
FILES=$(ls | grep -v autodoc | grep -v sandbox)

if [ ! -e $TARGET ] ; then mkdir $TARGET; fi
#rm -rf $TARGET/*
cp -rv $FILES $TARGET/

#if [ -e README ] ; then cp README $TARGET ;
#elif [ -e "../README*" ] ; then cp "../README*" $TARGET; fi
# if [ -e conf.py ] ; then cp conf.py $TARGET ; 

cp -v $MOD/*rst $MOD/READ* $TARGET/
if [ -e $MOD/doc/conf.py ] ; then cp $MOD/doc/conf.py $TARGET ; fi
if [ -e $MOD/doc/index.rst ] ; then cp $MOD/doc/index.rst $TARGET ; fi

CMD="sphinx-apidoc -F -e -o $TARGET $MOD"
$CMD
cd $TARGET
make html
ln -s _build/html

