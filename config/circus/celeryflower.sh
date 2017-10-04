#!/usr/bin/env bash

sleep 5

source /home/apache/.pyenv/versions/bbu/bin/activate
cd /home/apache/bbu
exec flower -A bbu --port=8008
