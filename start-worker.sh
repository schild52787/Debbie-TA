#!/bin/bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
