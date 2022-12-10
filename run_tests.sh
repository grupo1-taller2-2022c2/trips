#!/bin/bash

pytest
pytest --cache-clear --cov=app tests/ --cov-report=xml > pytest-coverage.txt
echo "Ready"