#!/bin/bash
cd backend
celery -A app.tasks.celery_app beat --loglevel=info
