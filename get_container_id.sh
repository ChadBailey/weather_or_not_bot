#!/bin/sh

docker container ls |grep $1 | awk -F ' ' '{print $1}'
