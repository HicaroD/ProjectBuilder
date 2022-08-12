#!/bin/bash
mkdir ./$1
cd ./$1
echo "Creating local repository"
git init
git remote add origin $2
git pull origin master --rebase
