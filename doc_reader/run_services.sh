#!/bin/bash

uv run uvicorn auth.main:app --reload --host 0.0.0.0 --port 8001