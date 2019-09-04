#!/bin/sh

docker container stop $(docker container ls |grep weather_or_not_bot | awk -F ' ' '{print $1}')
