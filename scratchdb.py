import requests

SCRATCHDB = "https://scratchdb.lefty.one/v3/"

def dict_in_list(d, l):
    return any(d.items() == item.items() for item in l)

def remove_duplicates_from_list_of_dicts(input_list):
    result_list = []
    for dictionary in input_list:
        if not dict_in_list(dictionary, result_list):
            result_list.append(dictionary)
    return result_list

def get_topics(category):
    r = requests.get(f'{SCRATCHDB}forum/category/topics/{category}/2?detail=0&filter=1')
    print(r.json())
    return remove_duplicates_from_list_of_dicts(r.json())

def get_post_info(post_id):
    r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    return r.json()

def get_author_of(post_id):
    r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    return r.json()['username']