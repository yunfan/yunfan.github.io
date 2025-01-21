#!/bin/bash

pelican content -o output -s pelicanconf.py

ghp-import -c geek42.info -b master output

git push -f origin master
git push -f origin build

