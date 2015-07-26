# Dropbox-Xerocon
Potential demo integrations for Xerocon

Machine Setup
-----
Recommended: brew (http://brew.sh/)

- Install Postgres (database - used for Heroku compatability): `brew install postgres`
- Create database: `createdb dropbox-xerocon`

Setup
-----
Recommended: pip (http://pip.readthedocs.org/en/latest/installing.html)
Required: python2.7

- Clone this project into an empty directory of your choice
- Install python virtual environment `pip install virtualenv`
- Setup virtual environment `virtualenv venv`
- Go into virtual environment `source venv/bin/activate` (note: to exit, type deactivate)
- Install dependencies with `pip install -r requirements.txt`
- Install Dropbox v2 SDK (required since not currently in pip): `pip install dropbox-sdk-python-master.zip`
- Set up database: `python db_create.py`

Launch (currently always launches in developer mode)
-----
- Go into virtual environment `source venv/bin/activate` (note: to exit, type deactivate)
- Make sure your database is running, and that config.py settings are accurate for your environment
- Launch webserver: `python run.py`