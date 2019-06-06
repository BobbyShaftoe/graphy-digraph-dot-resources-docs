#!/usr/bin/env bash

# brew install graphviz
# git clone https://github.com/davidfraser/pyan.git 

pyan *.py --uses --no-defines --colored --grouped --annotated --dot >myuses.dot

dot -Tsvg myuses.dot >myuses.svg


