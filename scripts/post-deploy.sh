#!/bin/bash

cd $APP_WORKDIR
poetry install
cd -

sudo systemctl restart gunicorn
#sudo systemctl reload gunicorn
