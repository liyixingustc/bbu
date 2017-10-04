#!/usr/bin/env bash

sleep 5

source /home/arthurtu/.pyenv/versions/bbu/bin/activate
cd /home/arthurtu/projects/bbu
exec flower -A bbu --port=8008
