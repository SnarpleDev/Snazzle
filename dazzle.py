# Dazzle library

"""
   Dazzle is a helper library for Snazzle that helps get things from ScratchDB and the Scratch API.
"""

from functools import lru_cache
import base64

from datetime import datetime
from uuid import uuid4
import sqlite3

from dotenv import dotenv_values
import requests

env = dotenv_values(".env")

SCRATCHDB = "https://scratchdb.lefty.one/v3/"
DAZZLE_DIR = env["DAZZLE_DIR"] if "DAZZLE_DIR" in env else ".dazzle-archive"
ENABLE_SCRATCH_AUTH = True

useDB = True  # False will fetch data from ScratchDB
REPLIT_MODE = False
USE_PROXY = False

def fmt_time(timestamp: str) -> str:
    """
    Formats a timestamp to a human-readable format.
    - `timestamp` (str): The timestamp to format.

    Returns:
    - str: The formatted timestamp.
    """
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%B %d, %Y at %I:%M %p UTC")

# TODO: deprecate the config functions because the .env file supersedes them
def set_server_host(host) -> None:
    """
    Sets the server host for the application.

    - `host` (str): The host to set.

    NOTE: May be removed in the future as it is not used.
    """
    global SERVER_HOST
    SERVER_HOST = host

def use_scratchdb(value: bool) -> None:
    """
    Force ScratchDB usage.

    - `value` (bool): True to force ScratchDB usage, False otherwise.
    """
    global USE_SDB
    USE_SDB = value

def remove_duplicates(input_list) -> list:
    """
    Removes duplicates from a list.

    - `input_list` (list): The list to remove duplicates from.

    Returns:
    - list: A list that is a copy of `input_list`, but with duplicates removed.
    """
    result_list = []
    for d in input_list:
        if d not in result_list:
            result_list.append(d)
    return result_list


@lru_cache(maxsize=15)
def get_topics(category, page) -> dict:
    """
    Gets topics in a subforum from ScratchDB.

    - `category` (str): The category to retrieve topics from.
    - `page` (int): The amount of pages of topics to retrieve.

    Returns:
    - dict: A dictionary containing the error status and topics.
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
def get_post_info(post_id) -> dict:
    """    
    Gets information about a forum post from ScratchDB.

    - `post_id` (str): The ID of the post to retrieve information for.

    Returns:
    - dict: Information about the forum post.
    """
    r = requests.get(f"{SCRATCHDB}forum/post/info/{post_id}", timeout=10)
    return r.json()


def get_author_of(post_id) -> str:
    """
    Gets the author of a forum topic.

    - `post_id` (str): The ID of the post to retrieve the author for.

    Returns:
    - str: The author of the forum topic.
    """
    return "user"
    # r = requests.get(f'{SCRATCHDB}forum/post/info/{post_id}')
    # return r.json()['username']


@lru_cache(maxsize=15)
def get_project_info(project_id) -> dict:
    """
    Gets information about a project from ScratchDB.

    - `project_id` (str): The ID of the project to retrieve information for.

    Returns:
    - dict: Information about the project.
    """
    try:
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
def get_comments(project_id: str) -> dict:
    """
    Gets comments for a project.

    - `project_id` (str): The ID of the project to retrieve comments for.

    Returns:
    - dict: Comments for the project.
    """
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
def get_ocular(username) -> dict:
    """
    Gets a user's status from Ocular.

    - `username` (str): The username of the user.

    Returns:
    - dict: User's status information.
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

def init_db() -> None:
    """
    Initializes the database.
    """
    conn = sqlite3.connect(env["DB_LOCATION"])
    conn.cursor().execute(
        f"CREATE TABLE IF NOT EXISTS {env['DB_TABLE']}( username, token )"
    )
    conn.close()

def get_featured_projects() -> dict:
    """
    Retrieves the featured projects from the Scratch API.

    Returns:
    - dict: Featured projects.
    """
    r = requests.get("https://api.scratch.mit.edu/proxy/featured", timeout=10)
    return r.json()


@lru_cache(maxsize=15)
def get_topic_data(topic_id) -> dict:
    """
    Gets data about a topic from ScratchDB.

    - `topic_id` (str): The ID of the topic to retrieve data for.

    Returns:
    - dict: Topic data.
    """
    r = requests.get(f"{SCRATCHDB}forum/topic/info/{topic_id}", timeout=10)
    try:
        if "error" in r.json().keys():
            return {"error": True, "message": "sdb_" + r.json()["error"].lower()}
        return {"error": False, "data": r.json()}
    except requests.exceptions.JSONDecodeError:
        return {"error": True, "message": "lib_scratchdbdown"}

def get_topic_posts(topic_id, page=0, order="oldest") -> dict:
    """
    Gets posts for a topic.

    - `topic_id` (str): The ID of the topic to retrieve posts for.
    - `page` (int): The page number of posts.
    - `order` (str): The order of posts (oldest or newest).

    Returns:
    - dict: Topic posts.
    """
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


def get_pfp_url(username, size=90) -> str:
    """
    Gets the profile picture URL for a user.

    - `username` (str): The username of the user.
    - `size` (int): The size of the requested image.

    Returns:
    - str: Profile picture URL."""
    r = requests.get(f"https://api.scratch.mit.edu/users/{username}", timeout=10)

    return r.json()["profile"]["images"][str(size) + "x" + str(size)]


def get_redirect_url() -> str:
    """
    Gets the redirect URL for Scratch Auth.

    Returns:
    - str: Redirect URL.
    """
    assert not (
        not env["SERVER_MODE"] or not env["SERVER_MODE"]
    ), "Snazzle must be run in server mode for Scratch Auth to work. See https://tinyurl.com/snazzle-server"
    redir_loc = base64.b64encode(
        f"http://{env['SERVER_HOST']}/handle-scratch-auth".encode()
    ).decode()
    return f"https://auth.itinerary.eu.org/auth?name=snazzle&redirect={redir_loc}"


def login(code: str) -> str:
    """
    Logs in a user with the provided code.

    - `code` (str): The authentication code.

    Returns:
    - str: Session ID.
    """
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


def token_matches_user(token: str) -> list:
    """
    Checks if the token matches the user.

    - `token` (str): The token to check.

    Returns:
    - list: List of matching users.
    """
    conn = sqlite3.connect(env["DB_LOCATION"])
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * from users WHERE token=?", (token,))
    return rows.fetchall()


def search_for_projects(q) -> dict:
    """
    Searches for projects.

    - `q` (str): The query string.

    Returns:
    - dict: Search results.
    """
    r = requests.get(
        f"https://api.scratch.mit.edu/search/projects?q={q}&mode=popular&language=en",
        timeout=10
    )
    return r.json()

def get_studio_data(id) -> dict:
    """
    Gets data about a studio.

    - `id` (str): The ID of the studio.

    Returns:
    - dict: Studio data.
    """
    r = requests.get(f'https://api.scratch.mit.edu/studios/{id}')
    return {"error": True, "message": "api_notfound"} if 'code' in r.json().keys() else r.json()

def get_studio_comments(id):
    pass

def get_trending_projects(limit: int = 20, page: int = 1):
    """
    Gets a list of trending projects for the explore page

    - `page` (int): The page of results

    Returns:
    - list: Projects
    """
    offset = limit * (page - 1)
    r = requests.get(
        f"https://api.scratch.mit.edu/search/projects?q=*&mode=trending&language=en&limit={limit}&offset={offset}",
        timeout=10
    )
    return r.json()

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
