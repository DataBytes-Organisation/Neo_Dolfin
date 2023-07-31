# NE0 DolFin 
Updated: 30/07/2023

## Local Deployment
### Requirements:
* IDE, like *Visual Studio Code*
* Python Version == **3.11**

### Deploy to ***Localhost***
* Pull this repo and select this branch, if you are unconfident in your GIT bash skills, please download GitHub Desktop: https://desktop.github.com/
* Once you have the repo folder open in your IDE, do the following in the BELOW ORDER:
	* Open a terminal window and move into the neo_dolfin directory via the terminal command: ```cd <path/to>/GitHub/dolfin_fe/neo_dolfin```
 		* (**NOTE: INSERT YOUR PATH AS REQUIRED, YOUR PATH MAY DIFFER**)  
  * Initiate a new *venv* env using the following terminal command: ```python -m venv venv``` 
  * Activate the *venv* env using the following terminal command: ```venv\scripts\activate```
  * Inside your IDE, create a new file inside your neo_dolfin folder called: ```.env``` (**MAKE SURE TO INCLUDE THE "." AT THE BEGINNING**) 
	* Ask one of the team leads for the credentials, that you must paste into the .env file and then save the file. 
  * Install the required libraries into the *venv* env using the following terminal command: ```pip install -r requirements.txt``` 
  * To run the flask application, use the following terminal command: ```python app.py``` 
  * Navigate to ```127.0.0.1``` in your web browser. 

## EC2 Deployment 
***WORK IN PROGRESS***
