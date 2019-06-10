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
  - This config is to authenticate into okta. The Authorization code provide by the okta application manager.
  
        {
            "Authorization": "SSWS 0XXXXXX",
            
            "password": "",
            
            "username": "",
             
            "service_url": ""
        }
 
## Run the Tap
    tap-okta.py -c config.json | target-stitch -c target_config.json
  
 Messages are written to standard output following the Singer specification. The resultant stream of JSON data can be consumed by a Singer target.
    
### Pagination:
 By Default 200 records are extracted from  the source json payload, so the pagination logic is implemented to loop through all the records from source json payload and load into the stitch target 
  
## Replication Methods and State File
  - Full Table
       - groups
       - users
       - applications
  - State File
       - None.
