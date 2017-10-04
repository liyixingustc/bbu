#!/usr/bin/env bash

source /home/apache/.pyenv/versions/bbu/bin/activate
cd /home/apache/bbu
exec celery worker -A bbu --loglevel=INFO
