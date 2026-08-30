#!/usr/bin/env bash
# Gera classificador_pb2.py e classificador_pb2_grpc.py a partir do .proto.
# Requer: pip install -r ../requirements-opcionais.txt
set -euo pipefail
cd "$(dirname "$0")"
python -m grpc_tools.protoc -I. \
  --python_out=. --grpc_python_out=. \
  classificador.proto
echo "stubs gerados em $(pwd)"
