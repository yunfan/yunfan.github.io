#!/bin/bash

pelican content -o output -s pelicanconf.py
echo 'geek42.info'  output/CNAME

ghp-import -b master output

git push -f origin master
git push -f origin build

