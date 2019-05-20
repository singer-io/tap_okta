# tap-okta
This is a singer tap that produces JSON-formatted data following the Singer spec.

This tap:
  - Pulls raw data from the Okta Api
  - Extracts the following resources: 
      - Users
      - Groups
      - Applications
      -	Applications Groups
      -	Applications Users
  - Outputs the schema for each resource
  - Full table load 
  
## Requirements
  - pip3
  - python 3.5+
  - mkvirtualenv
  
## Installation
In the directory:
  - $ mkvirtualenv -p python3 tap-okta
  - $ pip3 install -e .
  
## Usage
Source config file 
  - This config is to authenticate into okta. The Authorization is the Authorization code provide by the okta application manager .

  {
    "accept": "application/json",
     "content-type": "application/json",
  
  "Authorization": "SSWS 0XXXXXX",
  
  "password": "",
  
  "username": "",
  
  "service_url": ""
}


