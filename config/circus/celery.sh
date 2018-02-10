#!/usr/bin/env bash

source /home/apache/.venv/bbu/bin/activate
cd /home/apache/bbu
exec celery worker -A bbu --loglevel=INFO
