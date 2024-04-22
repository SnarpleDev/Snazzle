# Dazzle library

"""
    Dazzle is a helper library for Snazzle
    that helps get stuff from ScratchDB 
    and the Scratch API.
    
    It makes things easier to work with :)
    
    This library is mostly undocumented.
    Writing documentation would help us greatly :D
"""

from functools import lru_cache, wraps
import base64
import os

from datetime import datetime
from uuid import uuid4
import sqlite3

from dotenv import dotenv_values
import requests

env = dotenv_values(".env")

SCRATCHDB = "https://scratchdb.lefty.one/v3/"
DAZZLE_DIR = env["DAZZLE_DIR"] if "DAZZLE_DIR" in env else ".dazzle-archive"
ENABLE_SCRATCH_AUTH = True

useDB = False  # always change to true if on replit or other online ides. only affects project info for now
REPLIT_MODE = False
USE_PROXY = False

def fmt_time(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%B %d, %Y at %I:%M %p UTC")

def set_server_host(host):
    global SERVER_HOST
    SERVER_HOST = host

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
    for d in input_list:
        if d not in result_list:
            result_list.append(d)
    return result_list


@lru_cache(maxsize=15)
def get_topics(category, page):
    """
    Gets topics in a subforum from ScratchDB.
    """
    r = requests.get(
        f"{SCRATCHDB}forum/category/topics/{category}/{page}?detail=0&filter=1",
        timeout=10,
    )
    try:
        if type(r.json()) != list:
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}
        return {"error": False, "topics": remove_duplicates(r.json())}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}


@lru_cache(maxsize=15)
def get_post_info(post_id):
    """
    Gets info about a forum post from ScratchDB.
    """
    r = requests.get(f"{SCRATCHDB}forum/post/info/{post_id}", timeout=10)
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


@lru_cache(maxsize=15)
def get_project_info(project_id):
    try:
        """
        Get info about a project from ScratchDB.
        """
        if not useDB:
            r = requests.get(
                f"https://scratchdb.lefty.one/v2/project/info/id/{project_id}", timeout=10
            )
        else:
            r = requests.get(
                f"https://api.scratch.mit.edu/projects/{project_id}", timeout=10
            )
        return r.json()
    except Exception:
        return {"error": True, "message": "lib_scratchdbtimeout"}

@lru_cache(maxsize=15)
def get_comments(project_id):
    if not REPLIT_MODE:
        return None  # i'll do this later
    try:
        project_creator = requests.get(
            f"https://api.scratch.mit.edu/projects/{project_id}", timeout=10
        ).json()["author"]["username"]
    except Exception:
        return Exception
    r = requests.get(
        f"https://api.scratch.mit.edu/users/{project_creator}/projects/{project_id}/comments?limit=40",
        timeout=10,
    )
    return r.json()


@lru_cache(maxsize=5)
def get_ocular(username):
    """
    Get a user's status from ocular.
    """
    try:
        info = requests.get(
            f"https://my-ocular.jeffalo.net/api/user/{username}", timeout=10
        )
        info.json()["name"]
    except KeyError:
        return {
            "name": None,
            "status": None,
            "color": None,
        }  # i had to spell it the 'murican way for it to work
    return info.json()

def init_db():
    conn = sqlite3.connect(env["DB_LOCATION"])
    conn.cursor().execute(
        f"CREATE TABLE IF NOT EXISTS {env['DB_TABLE']}( username, token )"
    )
    conn.close()

def get_featured_projects():
    """
    Retrieve the featured projects from the Scratch API.

    Returns a JSON object containing the featured projects.
    """
    r = requests.get("https://api.scratch.mit.edu/proxy/featured", timeout=10)
    return r.json()


@lru_cache(maxsize=15)
def get_topic_data(topic_id):
    r = requests.get(f"{SCRATCHDB}forum/topic/info/{topic_id}", timeout=10)
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
        "https://api.scratch.mit.edu/explore/projects?limit=20&language=en&mode=trending&q=*",
        timeout=10,
    )
    return r.json()


def get_topic_posts(topic_id, page=0, order="oldest"):
    r = requests.get(
        f"{SCRATCHDB}forum/topic/posts/{topic_id}/{page}?o={order}", timeout=10
    )
    # post['author'], post['time'], post['html_content'], post['index'], post['is_deleted']
    try:
        if not isinstance(r.json(), list):
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}
        # Time formatting thanks to ChatGPT
        return {
            "error": False,
            "posts": [
                {
                    "id": post["id"],
                    "author": post["username"],
                    "time": fmt_time(post["time"]["first_checked"]),
                    "html_content": post["content"]["html"],
                    "bb_content": post["content"]["bb"],
                    "is_deleted": post["deleted"],
                    "index": i,
                }
                for i, post in enumerate(r.json())
            ],
        }
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}


def get_pfp_url(username, size=90):
    r = requests.get(f"https://api.scratch.mit.edu/users/{username}", timeout=10)

    return r.json()["profile"]["images"][str(size) + "x" + str(size)]


def get_redirect_url() -> str:
    assert not (
        not env["SERVER_MODE"] or not env["SERVER_MODE"]
    ), "Snazzle must be run in server mode for Scratch Auth to work. See https://tinyurl.com/snazzle-server"
    redir_loc = base64.b64encode(
        f"http://{env['SERVER_HOST']}/handle-scratch-auth".encode()
    ).decode()
    return f"https://auth.itinerary.eu.org/auth?name=snazzle&redirect={redir_loc}"


def login(code: str):
    data = requests.get(
        f"https://auth.itinerary.eu.org/api/auth/verifyToken?privateCode={code}",
        timeout=10,
    ).json()
    print(data)

    if (
        data["valid"]
        and data["redirect"] == f"http://{env['SERVER_HOST']}/handle-scratch-auth"
    ):
        session_id = str(uuid4())
        conn = sqlite3.connect(env["DB_LOCATION"])
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {env['DB_TABLE']}( username, token )"
        )
        cursor.execute(
            f"INSERT OR IGNORE INTO {env['DB_TABLE']} VALUES (?, ?)",
            (data["username"], session_id),
        )
        conn.commit()
        conn.close()
        return session_id


def token_matches_user(token: str):
    conn = sqlite3.connect(env["DB_LOCATION"])
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * from users WHERE token=?", (token,))
    return rows.fetchall()


def search_for_projects(q):
    r = requests.get(
        f"https://api.scratch.mit.edu/search/projects?q={q}&mode=popular&language=en",
        timeout=10
    )
    return r.json()

def get_studio_data(id):
    
    r = requests.get(f'https://api.scratch.mit.edu/studios/{id}')
    return {"error": True, "message": "api_notfound"} if 'code' in r.json().keys() else r.json()

def get_studio_comments(id):
    pass

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
