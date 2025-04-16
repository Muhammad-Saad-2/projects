#!/bin/bash

# Start the services in the background
python -m uvicorn app.auth.main:app --host 0.0.0.0 --port 8001 --reload &
python -m uvicorn app.posts.main:app --host 0.0.0.0 --port 8002 --reload &
python -m uvicorn app.notifications.main:app --host 0.0.0.0 --port 8003 --reload &
python -m uvicorn app.users.main:app --host 0.0.0.0 --port 8004 --reload &
python -m uvicorn app.gateway.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait for all background processes to complete
wait 