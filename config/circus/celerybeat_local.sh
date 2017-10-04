#!/usr/bin/env bash

source /home/arthurtu/.pyenv/versions/bbu/bin/activate
cd /home/arthurtu/projects/bbu
exec celery -A bbu beat
