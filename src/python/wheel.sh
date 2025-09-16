#!/bin/bash
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
bumpversion patch --allow-dirty
python setup.py bdist_wheel -d dist
