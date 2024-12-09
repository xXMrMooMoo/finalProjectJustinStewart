### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project

## Description
This program acts as a Cradlepoint inventory system.
It consists of 7 Pages:
* Home Page
  * This page contains links to all other sections of the program and a description of what it does
* Admin Dashboard
  * An administrative dashboard allowing user creation, deletion, and database reset
    * Note: a database reset will re-initialize the database but will preserve the admin users. It will wipe all extra (likely invalid) cradlepoints added to the database by other users.
    * Note x2: Admin login required
* Full Inventory
  * A page that shows all Cradlepoint Inventory Tables in their entierty.
* Router Status Lookup
  * A page that allows API calls based on a valid router ID to the NetCloud Manager (NCM) API. It will return the router status and how since when its been in that state.
* Router Detail Finder
  * A page that allows searching all tables via mac address and returns all Cradlepoint details in a table.
* Add A Router
  * A page that allows a router to be added to the database. 
    * Note: validation is not done on the address
    * Note x2: Admin login required
* Admin Login Page
  * Log in page for admins

### Pip Install Instructions/Dependencies
* This program required Cradlepoint NCM API keys to work properly. A file must be named root_rw.ini located in the same folder as app.py, the file must be structured like so:
  * [KEYS]
  * X-ECM-API-ID = xx
  * X-ECM-API-KEY= xx
  * X-CP-API-ID = xx
  * X-CP-API-KEY = xx


* Please run the following to install all the packages:
```
pip install -r requirements.txt
```
* To initialize the database please run the following from the programs working directory:
```
flask init-db
```
* To create an Admin user please run the following from the programs working directory::
```
python db.py AddAdminUser username password
```

### Executing program

* To run the program, from the programs working directory, please run:
```
flask run
```

### Output
By default, when running, this program will output a link to navigate the user to a html environment:
```
http://127.0.0.1:5000
```
The program will also have a log streaming to the terminal, and also in a log.csv file.
## Authors
Justin Stewart

## Acknowledgments
* [Cradlepoint Developer Documentation](https://developer.cradlepoint.com/)
* [Flask Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/)
* [Bootstrap Modals](https://getbootstrap.com/docs/4.0/components/modal/)