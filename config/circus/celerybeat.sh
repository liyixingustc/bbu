#!/usr/bin/env bash

source /home/apache/.pyenv/versions/bbu/bin/activate
cd /home/apache/bbu
exec celery -A bbu beat
