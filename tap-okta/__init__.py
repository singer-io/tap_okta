import requests
import json
import singer
import os
import datetime


from singer import metadata


schemas = {}
LOGGER = singer.get_logger()
session = requests.session()
REQUIRED_CONFIG_KEYS = ['api_key', 'service_url']
schema_list = ['groups','users','applications']


KEY_PROPERTIES = {
    'application_groups': ['id'],
    'application_users': ['id'],
    'applications': ['id'],
    'group_users': ['id'],
    'groups': ['id'],
    'users':['id']
}

def header_payload(p_data):

    header = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': 'SSWS ' + p_data['api_key']
    }
    return header


def populate_metadata(schema_name, schema):
    mdata = metadata.new()
    mdata = metadata.write(mdata, (), 'table-key-properties', KEY_PROPERTIES[schema_name])
    for field_name in schema['properties'].keys():
        if field_name in KEY_PROPERTIES[schema_name]:
            mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'automatic')
        else:
            mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'available')
    return mdata


def get_catalog():
    raw_schemas = load_schemas()
    streams = []
    for schema_name, schema in raw_schemas.items():
       # get metadata for each field
        mdata = populate_metadata(schema_name, schema)
       # create and add catalog entry
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata' : metadata.to_list(mdata),
            'key_properties': KEY_PROPERTIES[schema_name],
        }

        streams.append(catalog_entry)
    return {'streams': streams}


def do_discover():

    LOGGER.info('Loading schemas')
    catalog = get_catalog()
    """LOGGER.info (json.dumps(catalog, indent=2))"""


def load_data(p_data):
    for lst_schema in schema_list:
        if lst_schema == 'users':
            url = p_data['service_url'] + "users"
            url_pagination(lst_schema,url, p_data)
        elif lst_schema == 'groups':
            url = p_data['service_url'] + "groups"
            url_pagination(lst_schema, url, p_data)
        elif lst_schema == 'applications':
            url = p_data['service_url'] + "apps"
            url_pagination ('applications' , url, p_data )


def url_pagination(p_schema, p_url, p_data):
    groups_for_user = []
    lst_urs_assign_app = []
    next_url = p_url

    header = header_payload(p_data)
    singer.write_schema(p_schema, schemas[p_schema], 'id')
    while (next_url):

        response = requests.request("GET", next_url, headers=header)
        if (response.status_code == 200):
            response_links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,<', ',<'))
            next_url = ""

            for linkobj in response_links:
                if linkobj['rel'] == 'next':
                    next_url = linkobj['url']

        else:
            exit(1)
        data = response.json()
        for record in data:
            if p_schema == 'groups':
                groups_for_user.append(record['id'])
            if p_schema == 'applications':
                lst_urs_assign_app.append(record['id'])
            singer.write_record(p_schema, record)
    if p_schema == 'groups':
        get_groups_for_user(groups_for_user, p_data)
    if p_schema == 'applications':
        list_assigned_groups_app(lst_urs_assign_app, p_data)
        list_users_assigned_to_app(lst_urs_assign_app, p_data)

def get_groups_for_user(p_groups_for_user,p_data):
    for grp_list in p_groups_for_user:
        p_get_group_user_url = p_data['service_url'] + "groups/" + grp_list + "/users"
        url_pagination('group_users' , p_get_group_user_url, p_data )


def list_users_assigned_to_app(p_lst_urs_assign_app,p_data):
    for usr_app_list in p_lst_urs_assign_app:
        p_url = p_data['service_url'] + "apps/" + usr_app_list + "/users"
        url_pagination('application_users' , p_url, p_data)


def list_assigned_groups_app(p_lst_urs_assign_app,p_data):
    for usr_grp_list in p_lst_urs_assign_app:
        appid_groups_url = p_data['service_url'] + "apps/" + usr_grp_list + "/groups"
        url_pagination('application_groups' ,appid_groups_url, p_data )


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():
    global schemas
    for filename in os.listdir(get_abs_path('tap_okta\schemas')):
        path = get_abs_path('tap_okta\schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)
    return schemas


def main():

    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    if args.config:
        if args.discover:
            do_discover()
        load_schemas()
        load_data(args.config)

    LOGGER.info('End Date Time : %s', datetime.datetime.now())

        
if __name__ == '__main__':
    LOGGER.info('Start Date Time : %s',datetime.datetime.now())
    main()
