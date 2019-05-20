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

