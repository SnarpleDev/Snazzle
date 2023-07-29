# Dazzle v0.1

from functools import lru_cache, wraps
import requests
from datetime import datetime

SCRATCHDB   = "https://scratchdb.lefty.one/v3/"
DAZZLE_DIR  = "./.dazzle-archive"
useDB       = False  # always change to true if on replit or other online ides. only affects project info for now
REPLIT_MODE = False
USE_PROXY   = False

def archive_result(filename):
    """
        Archives a function's results in `filename`.
        This is mainly used for functions 
        that get stuff from ScratchDB so that 
        Snazzle can be used when ScratchDB is down.
        
        The only reason this exists is because ScratchDB goes down all the time, but there's no alternative.
        I wish Lefty would just fix their service but it's not an option.
    """
    def decorate(ofunc):
        @wraps(ofunc)
        def wrapper(*args, **kwargs):
            print(args)
            fname = filename
            func_result = ofunc(*args, **kwargs)
            
            if '$' in fname:
                count = 0
                while '$' in fname:
                    print(count)
                    fname = fname.replace('$', str(args[count]))
                    count += 1
                count = 0
                while '%' in fname:
                    fname = fname.replace('$', str(kwargs.values()[count]))
                    count += 1
            
            with open(f'{DAZZLE_DIR}/{fname}', "wt", encoding='utf-8') as f:
                f.write(str(func_result))
            
            return func_result
        
        return wrapper
    return decorate

def use_scratchdb(value):
    """
        Force ScratchDB to be used.
    """
    global USE_SDB
    USE_SDB = value

def replit_mode(value):
    """
        Enable Replit mode so that Snazzle can be used on Replit.
        
        This is a stricter version of the `use_scratchdb` function.
    """
    global REPLIT_MODE
    REPLIT_MODE = value
    
def use_proxy(value):
    """
        Force proxy to be used so that Snazzle
        can be used on Replit without ScratchDB
        because ScratchDB goes down all the time
        and it's also a little slow.
        
        The archiving solution may work but it's
        not ideal.
    """
    global USE_PROXY
    USE_PROXY = value

def remove_duplicates(input_list):
    """
        Removes duplicates from a list.
        
        Needs to work on unhashable datatypes
        which is why it's so slow and hacky and ew.
    """
    result_list = []
    for dict in input_list:
        if dict not in result_list:
            result_list.append(dict)
    return result_list


@archive_result(f'gettopics-category_$-page_$')
@lru_cache(maxsize=15)
def get_topics(category, page):
    """
        Gets topics in a subforum from ScratchDB.
    """
    r = requests.get(f"{SCRATCHDB}forum/category/topics/{category}/{page}?detail=0&filter=1")
    try:
        if type(r.json()) != list:
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}

        return {"error": False, "topics": remove_duplicates(r.json())}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}


@archive_result(f'getpostinfo-$')
@lru_cache(maxsize=15)
def get_post_info(post_id):
    """
        Gets info about a forum post from ScratchDB.
    """
    r = requests.get(f"{SCRATCHDB}forum/post/info/{post_id}")
    return r.json()


def get_author_of(post_id):
    """
        Intended to get the author of a forum topic.
        
        For now it just returns "user" because it's very slow
        when you have to loop over all the posts in a topic
        to get one singular piece of data.
    """
    return "user"
    # r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    # return r.json()['username']


@archive_result(f'projectinfo-id_$')
@lru_cache(maxsize=15)
def get_project_info(project_id):
    """
        Get info about a project from ScratchDB.
    """
    if not useDB:
        r = requests.get(f'https://scratchdb.lefty.one/v2/project/info/id/{project_id}')
    else:
        r = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
    return r.json()


@lru_cache(maxsize=15)
def get_comments(project_id):
    if not REPLIT_MODE:
        return None # i'll do this later
    try:
        project_creator = requests.get(
            f"https://api.scratch.mit.edu/projects/{project_id}"
        ).json()["author"]["username"]
    except Exception:
        return Exception
    r = requests.get(
        f"https://api.scratch.mit.edu/users/{project_creator}/projects/{project_id}/comments?limit=40"
    )
    return r.json()


@archive_result(f'ocular-username_$')
@lru_cache(maxsize=5)
def get_ocular(username):
    """
        Get a user's status from ocular.
    """
    try:
        info = requests.get(f"https://my-ocular.jeffalo.net/api/user/{username}")
        info.json()["name"]
    except Exception:
        return {
            "name": None,
            "status": None,
            "color": None,
        }  # i had  to spell colour wrong for it to work
    return info.json()

@archive_result(f'aviate-username_$')
@lru_cache(maxsize=5)
def get_aviate(username):
    """
        Get a user's status from Aviate.
    """
    # Aviate API is much simple very wow
    # Better than ocular API imo
    r = requests.get(f"https://aviate.scratchers.tech/api/{username}")
    if r['success'] == False:
        return ''
    else:
        return r["status"]

def get_featured_projects():
    r = requests.get("https://api.scratch.mit.edu/proxy/featured")
    return r.json()

@archive_result(f'topic-data-id_$')
@lru_cache(maxsize=15)
def get_topic_data(topic_id):
    r = requests.get(f"{SCRATCHDB}forum/topic/info/{topic_id}")
    try:
        if "error" in r.json().keys():
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}

        return {"error": False, "data": r.json()}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}


@lru_cache(maxsize=15)
def get_trending_projects():
    # TODO: implement limits and offsets
    # language parameter seems to be ineffectual when set to another lang
    r = requests.get(
        "https://api.scratch.mit.edu/explore/projects?limit=20&language=en&mode=trending&q=*"
    )
    return r.json()

@archive_result(f'posts-id_$-page_$')
def get_topic_posts(topic_id, page=0, order="oldest"):
    r = requests.get(f"{SCRATCHDB}forum/topic/posts/{topic_id}/{page}?o={order}")
    # post['author'], post['time'], post['html_content'], post['index'], post['is_deleted']
    try:
        if type(r.json()) != list:
            return {'error': True, 'message': 'sdb_' + r.json()['error'].lower()}

        # Time formatting thanks to ChatGPT
        return {'error': False, 'posts': [{'author': post['username'], 'time': datetime.fromisoformat(post['time']['first_checked'].replace("Z", "+00:00")).strftime("%B %d, %Y at %I:%M %p UTC"), 'html_content': post['content']['html'], 'is_deleted': post['deleted'], 'index': i} for i, post in enumerate(r.json())]}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}

@archive_result('pfp_url')
def get_pfp_url(username, size = 90):
    r = requests.get(f"https://api.scratch.mit.edu/users/{username}")
    
    return r.json()['profile']['images'][str(size) + 'x' + str(size)]

# Below this line is all stuff used for the REPL debugging mode
# Generally, don't touch this, unless there's a severe flaw or something

def parse_token(token: str, i: int):
    if isinstance(token, str) and i > 0 and "." in token:
        return token.replace(".", " ")
    return token


def parse_cmd(cmd: str):
    if not isinstance(cmd, str):
        return None

    return_cmd = [parse_token(token, i) for i, token in enumerate(cmd.split(" "))]

    return return_cmd[0] + "(" + ", ".join(return_cmd[1:]) + ")"


if __name__ == "__main__":
    cmd = None
    while True:
        cmd = input("input> ")
        parsed_cmd = parse_cmd(cmd)
        print("running>", parsed_cmd)
        print("output>", eval(parsed_cmd))
