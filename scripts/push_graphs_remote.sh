#!/usr/bin/env bash
set -euo pipefail

# Sube los grafos OFICIALES de coloreado (gc_50_7.txt, gc_1000_9.txt) al
# servidor remoto. Necesario porque data/graphs/ esta en .gitignore -- un
# "git pull" alla NO trae estos archivos, asi que hay que copiarlos aparte,
# una sola vez (o cada vez que cambien), ANTES de correr
# scripts/run_remote_heavy.sh en el remoto. Una vez subidos,
# experiments/run_graph_coloring.py los usa directo (ensure_instance() solo
# genera un grafo aleatorio si el path no existe -- con el archivo ya ahi,
# esa rama nunca se ejecuta).
#
# Uso, desde la laptop (el repo ya debe existir clonado en el remoto):
#   bash scripts/push_graphs_remote.sh

cd "$(dirname "${BASH_SOURCE[0]}")/.."

REMOTE_HOST="diego@132.248.52.48"
REMOTE_PORT="264"
REMOTE_DIR="csp-adversarial-search-hw2/data/graphs"

# -p en el ssh crea el directorio si no existe todavia (primera vez).
ssh -p "${REMOTE_PORT}" "${REMOTE_HOST}" "mkdir -p ~/${REMOTE_DIR}"

rsync -avz -e "ssh -p ${REMOTE_PORT}" \
    data/graphs/gc_50_7.txt \
    data/graphs/gc_1000_9.txt \
    "${REMOTE_HOST}:~/${REMOTE_DIR}/"

echo "Grafos subidos a ${REMOTE_HOST}:~/${REMOTE_DIR}/"
echo "Ahora, ya en el remoto (tras git pull):"
echo "  nohup bash scripts/run_remote_heavy.sh > logs/run_all.log 2>&1 &"
echo "  disown"
