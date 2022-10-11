#!/bin/bash
app="admin.test"
docker build -t ${app} .
docker run -d -p 540:540 \
  --name=${app} \
  -v "$PWD":/app ${app}