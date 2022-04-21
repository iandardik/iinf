#!/bin/bash

if [[ "$1" = "" || "$2" = "" ]]
then
  echo "usage: $0 <path> <prefix>"
fi

for f in `ls "$1"`
do
  mv "$1/$f" "$1/$2-$f"
done
