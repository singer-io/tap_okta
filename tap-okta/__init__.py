import requests
import json
import singer
import os
import datetime

from singer import metadata


header = {}
args = {}
schemas = {}
schema = {}
groups_for_user = []
lst_urs_assign_app = []
LOGGER = singer.get_logger()
session = requests.session()
REQUIRED_CONFIG_KEYS = ['accept', 'content-type', 'Authorization', 'service_url']
schema_list = ['groups','users','applications']


def header_payload(p_data):

    global header
    header = {
        'accept': p_data['accept'],
        'content-type': p_data['content-type'],
        'Authorization': p_data['Authorization']
    }
    return header


def load_data():
    for lst_schema in schema_list:
        if lst_schema == 'users':
            url = args.config['service_url'] + "users"
            url_pagination(lst_schema,url)
        elif lst_schema == 'groups':
            url = args.config['service_url'] + "groups"
            url_pagination(lst_schema, url)
        elif lst_schema == 'applications':
            url = args.config['service_url'] + "apps"
            url_pagination ('applications' , url )


def url_pagination(p_schema, p_url):

    next = False
    first = True
    next_url = ""
    singer.write_schema(p_schema, schema[p_schema], 'id')
    while (next or first):
        if next:
            response = requests.request("GET", next_url, headers=header)
            response_links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,<', ',<'))
            next_url = ""
            for linkobj in response_links:
                if linkobj['rel'] == 'next':
                    next_url = linkobj['url']
                    next = True
                else:
                    next = False
        if first:
            response = requests.request("GET", p_url , headers=header)
            if (response.status_code == 200):
                response_links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,<', ',<'))
                next_url = ""
                for linkobj in response_links:
                    if linkobj['rel'] == 'next':
                        next_url = linkobj['url']
                        next = True
                        first = False
                    else:
                        first = False
            else:
                exit(1)

        data = json.loads(response.text)
        for record in data:
            if p_schema == 'groups':
                groups_for_user.append(record['id'])
            if p_schema == 'applications':
                lst_urs_assign_app.append(record['id'])
            singer.write_record(p_schema, record)
    if p_schema == 'groups':
        get_groups_for_user(groups_for_user)
    if p_schema == 'applications':
        list_assigned_groups_app(lst_urs_assign_app)
        list_users_assigned_to_app(lst_urs_assign_app)


def get_groups_for_user(p_groups_for_user):
    for grp_list in p_groups_for_user:
        p_get_group_user_url = args.config['service_url'] + "groups/" + grp_list + "/users"
        url_pagination('group_users' , p_get_group_user_url )


def list_users_assigned_to_app(p_lst_urs_assign_app):
    for usr_app_list in p_lst_urs_assign_app:
        p_url = args.config['service_url'] + "apps/" + usr_app_list + "/users"
        url_pagination('application_users' , p_url)


def list_assigned_groups_app(p_lst_urs_assign_app):
    for usr_grp_list in p_lst_urs_assign_app:
        appid_groups_url = args.config['service_url'] + "apps/" + usr_grp_list + "/groups"
        url_pagination('application_groups' ,appid_groups_url )


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '\\' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)
    return schemas


def main():

    global args
    global schema
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.config:
        schema = load_schemas()
        header_payload(args.config)
        load_data()
    LOGGER.info('End Date Time : %s', datetime.datetime.now())

        
if __name__ == '__main__':
    LOGGER.info('Start Date Time : %s',datetime.datetime.now())
    main()
