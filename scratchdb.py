useDB = False #always change to true if on replit or other online ides. only affects project info for now
import sys
import requests

SCRATCHDB = "https://scratchdb.lefty.one/v3/"
useDB = False #always change to true if on replit or other online ides. only affects project info for now



def use_scratchdb(value):
    global USE_SDB
    USE_SDB = value
    
def replit_mode(value):
    global REPLIT_MODE
    REPLIT_MODE = value

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
        if type(r.json()) != list:
            return {
                'error': True,
                'message': 'sdb_' + r.json()['error'].lower()
            }
        
        return {
            'error': False,
            'topics': remove_duplicates(r.json())
        }
    except requests.exceptions.JSONDecodeError:
        return {
            'error': True,
            'message': 'lib_scratchdbdown'
        }


def get_post_info(post_id):
    r = requests.get(f"{SCRATCHDB}forum/post/info/{post_id}")
    return r.json()


def get_author_of(post_id):
    return "user"
    # r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    # return r.json()['username']
def get_project_info(project_id):
    if useDB == True:
        r = requests.get(f'https://scratchdb.lefty.one/v2/project/info/id/{project_id}')
    else:
        r = requests.get(f'https://api.scratch.mit.edu/projects/{project_id}')
    return r.json()


def get_comments(project_id):
    if useDB == True:
        return None # i'll do this later
    try:
        project_creator = requests.get(f'https://api.scratch.mit.edu/projects/{project_id}').json()['author']['username']
    except:
        return None
    r = requests.get(f'https://api.scratch.mit.edu/users/{project_creator}/projects/{project_id}/comments?limit=40')
    return r.json()

def get_ocular(username):
    try:
        info = requests.get(f'https://my-ocular.jeffalo.net/api/user/{username}')
        a = info.json()["name"]
    except:
        return {"name":None,"status":None,"color":None} #i had  to spell colour wrong for it to work
    return info.json()

def get_featured_projects():
    r = requests.get("https://api.scratch.mit.edu/proxy/featured")
    return r.json()

>
def get_topic_data(topic_id):
    r = requests.get(f'{SCRATCHDB}forum/topic/info/{topic_id}')
    return r.json()

def get_topic_posts(topic_id, page = 0, order="oldest"):
    r = requests.get(f'{SCRATCHDB}forum/topic/posts/{topic_id}/{page}?o={order}')
    # post['author'], post['time'], post['html_content'], post['index'], post['is_deleted']
    try:
        if type(r.json()) != list:
            return {
                'error': True,
                'message': 'sdb_' + r.json()['error'].lower()
            }
        
        return {
            'error': False,
            'posts': [{'author': post['username'], 'time': post['time']['first_checked'], 'html_content': post['content']['html'], 'is_deleted': post['deleted']} for post in r.json()]
        }
    except requests.exceptions.JSONDecodeError:
        return {
            'error': True,
            'message': 'lib_scratchdbdown'
        }

# Below this line is all stuff used for the REPL mode which is used for debugging
# Generally, don't touch this, unless there's a severe flaw or something

def parse_token(token: str, i: int):
    if isinstance(token, str) and i > 0 and '.' in token:
        return token.replace('.', ' ')
    return token

def parse_cmd(cmd: str):
    if not isinstance(cmd, str):
        return None
    
    return_cmd = [parse_token(token, i) for i, token in enumerate(cmd.split(' '))]
    
    return return_cmd[0] + '(' + ', '.join(return_cmd[1:]) + ')'

if __name__ == '__main__':
    cmd = None
    while True:
        cmd = input('input> ')
        parsed_cmd = parse_cmd(cmd)
        print('running>', parsed_cmd)
        print('output>', eval(parsed_cmd))
