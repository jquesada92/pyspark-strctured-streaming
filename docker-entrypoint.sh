#!/bin/bash
set -e

echo "Starting fake data generator in background..."
python /workspace/generate_fake_data.py &

echo "Starting JupyterLab..."
exec python -m jupyterlab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --allow-root \
  --ServerApp.token= \
  --ServerApp.password= \
  --ServerApp.root_dir=/workspace