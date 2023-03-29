#!/usr/bin/env bash

set -eu

main() {
  python manage.py migrate
  # TODO: Use Gunicorn in production
  python manage.py runserver 0.0.0.0:80 --insecure
}

main "$@"
