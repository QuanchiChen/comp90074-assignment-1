#!/bin/sh
docker build --tag python-docker .
docker run -p 80:80 python-docker 
