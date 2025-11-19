#!/bin/bash

# # Start the backend server in the background
# echo "Starting backend server..."
# cd app
# uvicorn main:app --reload &
# BACKEND_PID=$!
# cd ..

# # Start the frontend server
# echo "Starting frontend server..."
# cd frontend
# streamlit run streamlit_app.py

# # Kill the backend server when the script is stopped
# kill $BACKEND_PID


echo "Starting backend server..."
# uv run fastapi dev 
python -m uvicorn app.main:app --reload 
BACKEND_PID=$!

echo "Starting frontend server..."
python3 -m streamlit run frontend/streamlit_app.py

kill $BACKEND_PID


