How to call the Basiq open banking API's using these files:


File structure:
API.py - this file contains methods to call each of the key Basiq API's. If any additional API connections need to be added, they should be added in here.

get_data.py - this has been created to test the functionality of all of the API methods.

use_data.py - this has been created to extract the outputs of key data oriented Basiq API's and store the outputs in dataframes so they can be used in interim to progress other streams.

.env - contains the API key required to access Basiq API's


Getting started:

Before being able to use any of the Basiq API's, you need to swap your API Key for an Auth Token. This function is in API.py, in the Core class and is called 'get_auth_token'.

The Auth token expires every 60 minutes, so needs to be refreshed. Best practice is to refresh this 2-3 times an hour.

To access data from one of the Basiq test accounts, run use_data.py.