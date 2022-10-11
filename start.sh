#!/bin/bash
app="admin.test"
docker build -t ${app} .
docker run -d -p 49999:49999 \
  --name=${app} \
  -v "$PWD":/app ${app}