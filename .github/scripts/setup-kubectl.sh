#!/usr/bin/env bash

set -euo pipefail

readonly KUBE_HOME="$HOME/.kube"
readonly KUBE_CONFIG_PATH="$KUBE_HOME/config"
readonly KUBE_CONFIG="
apiVersion: v1
kind: Config
clusters:
- cluster:
    insecure-skip-tls-verify: true
    server: $KUBE_API_SERVER
  name: arvan
contexts:
- context:
    cluster: arvan
    namespace: $KUBE_NAMESPACE
    user: kube-user
  name: main-context
current-context: main-context
preferences: {}
users:
- name: kube-user
  user:
    token: $KUBE_API_TOKEN
"

mkdir -p "$KUBE_HOME"
echo "$KUBE_CONFIG" >"$KUBE_CONFIG_PATH"
