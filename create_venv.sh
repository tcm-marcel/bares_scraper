#!/bin/bash

if [ $# -eq 0 ]
then
  echo "Usage: ${0} <python version>"
  exit 1
fi

version=$1

rm -rf .venv
python${version} -m venv .venv
.venv/bin/pip3 install -r requirements.txt
