import requests
from collections import OrderedDict

SCRATCHDB = "https://scratchdb.lefty.one/v3/"

def remove_duplicates(input_list):
    # needs to work on unhashable datatypes
    result_list = []
    for dict in input_list:
        if dict not in result_list:
            result_list.append(dict)
    return result_list

def get_topics(category):
    r = requests.get(f'{SCRATCHDB}forum/category/topics/{category}/2?detail=0&filter=1')
    try:
        return remove_duplicates(r.json())
    except requests.exceptions.JSONDecodeError:
        return None

def get_post_info(post_id):
    r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    return r.json()

def get_author_of(post_id):
    return 'user'
    # r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    # return r.json()['username']

def get_project_name(project_id):
    r = requests.get(f'https://scratchdb.lefty.one/v2/project/info/id/{project_id}')
    print(r.json())
    try:
        return r.json()['title']
    except:
        return "A project..."
