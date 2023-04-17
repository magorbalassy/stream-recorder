#!/bin/bash
gunicorn app:app --daemon \
  -w 2 --threads 2 \
  --access-logfile /tmp/gunicorn-access.log \
  --error-logfile /tmp/gunicorn-error.log \
  -b 0.0.0.0:5000
