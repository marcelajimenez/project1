# Project1

# Create virtual environment 
$ python3 -m venv myvirtualenv

# Run virtual environment
$ source myvirtualenv/bin/activate 

# Install necessary packages
$ pip install -r requirements.txt

# Set the flask app
$ export FLASK_APP=run.py

# Set the database URL
$ export DATABASE_URL="postgres://fhtmmpjjvejjxs:a4fc62fd0a563452b14a6900423cd903199060e28207fb93fc06ccf9ae034723@ec2-3-222-30-53.compute-1.amazonaws.com:5432/d11g6lfpjmbrjn"

# Set good reads key
$ export GOODREADS_KEY="xRjIm68xlsyHJHEXN6MPw"

# Initiate database
$ flask db init

# Migrate tables
flask db migrate -m "tables"

# Commit table migration
flask db upgrade