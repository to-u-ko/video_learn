#!/bin/sh

# Dockerコンテナを一括で停止・削除
# docker compose down -v
docker compose down -v
# 停止中のDockerコンテナを一括で削除
docker rm $(docker ps -a -q)
# Dockerイメージを一括で削除
docker rmi $(docker images -q)
# Dockerのシステムなどを削除
docker system prune