#!/bin/bash

set -e

sudo aptitude update
sudo aptitude --quiet --assume-yes install python3.3 python3.3-dev postgresql-9.3 libpq-dev

pyvenv-3.3 venv
source venv/bin/activate
wget --no-verbose https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python3 get-pip.py
rm get-pip.py
pip3 install -r /vagrant/requirements.txt
cat <<EOF >> /home/vagrant/.bashrc
VIRTUAL_ENV_DISABLE_PROMPT=1 source /home/vagrant/venv/bin/activate
EOF

sudo sed 's/\(local\s\+all\s\+all\s\+\)peer/\1trust/' -i /etc/postgresql/9.3/main/pg_hba.conf
sudo invoke-rc.d postgresql restart
sudo -u postgres psql --command "CREATE USER lpmc;"
sudo -u postgres psql --command "CREATE DATABASE lpmc;"
sudo -u postgres psql --command "GRANT ALL PRIVILEGES ON DATABASE lpmc to lpmc;"
psql -U lpmc < /vagrant/schema.sql
