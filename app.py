"""
       **** Snazzle Server Code ****
 Made in Flask by Snarple over at 
https://github.com/SnarpleDev/Snazzle/
"""

# automatically install deps
import install_reqs

from os import listdir
from sys import version_info, exit
from datetime import timedelta
from flask import (
    Flask,
    render_template,
    stream_template,
    make_response,
    request,
    redirect,
)
import requests
import webbrowser

from werkzeug import exceptions as werkexcept

import dazzle

REPLIT_MODE = True if dazzle.env["REPLIT_MODE"] == "yes" else False
USE_SCRATCHDB = True if dazzle.env["USE_SCRATCHDB"] == "yes" else False
HOST, PORT = dazzle.env["SERVER_HOST"].split(":")
DEBUG = True if dazzle.env["DEBUG"] == "yes" else False
FLASK_DEBUG = True if dazzle.env["FLASK_DEBUG"] == "yes" else False

app = Flask(__name__)

if not (version_info.major == 3 and version_info.minor >= 8):
    print(
        """Snazzle does not work on Python 3.7 or lower. Please upgrade.
3.8 is old now anyways, and you should be using the latest version of Python unless you absolutely cannot."""
    )
    exit(0)

user_data = dict(
    theme="choco",
    user_name="CoolScratcher123",
    pinned_subforums=[],
    saved_posts=[],
    max_topic_posts=20,
    show_deleted_posts=True,
    ocular_ov=True,  # for 'ocular override'
    signed_in=True,
    use_sb2=False,
    sb_scale=1,
    use_old_layout=False,
)


dazzle.use_scratchdb(True)

global get_status
get_status = dazzle.get_ocular


def get_themes():
    return [
        item[7 : item.index(".css")]
        for item in listdir("static")
        if item.startswith("styles-") and item.endswith(".css")
    ]


# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(r):
    """
    Stops forum pages from being cached so that they actually work correctly
    """
    if "/forums" in request.url or "/settings" in request.url:
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
    return r


subforums_data = (
    ("Welcome", ["Announcements", "New Scratchers"]),
    (
        "Making Scratch Projects",
        [
            "Help with Scripts",
            "Show and Tell",
            "Project Ideas",
            "Collaboration",
            "Requests",
            "Project Save & Level Codes",
        ],
    ),
    (
        "About Scratch",
        [
            "Questions about Scratch",
            "Suggestions",
            "Bugs and Glitches",
            "Advanced Topics",
            "Connecting to the Physical World",
            "Scratch Extensions",
            "Open Source Projects",
        ],
    ),
    (
        "Interests Beyond Scratch",
        ["Things I'm Making and Creating", "Things I'm Reading and Playing"],
    ),
)


@app.context_processor
def context():
    # Play with this and the user_data dict to manipulate app state
    username, signed = None, False
    if request.cookies.get("snazzle-token"):
        matched = dazzle.token_matches_user(request.cookies.get("snazzle-token"))
        signed = len(matched) == 1
        username = matched[0][0] if signed else None
    return dict(
        theme=user_data["theme"],
        username=username or user_data["user_name"],
        signed_in=signed,
        to_str=str,
        get_author_of=dazzle.get_author_of,
        len=len,
        host=HOST,
        get_status=get_status,
        sb_scale=user_data["sb_scale"],
        use_sb2=user_data["use_sb2"],
    )


@app.get("/")
def index():
    """
    The home page of the app
    """
    projects = dazzle.get_featured_projects()
    trending = dazzle.get_trending_projects()
    return stream_template(
        "index.html",
        featured_projects=projects["community_featured_projects"],
        featured_studios=projects["community_featured_studios"],
        trending_projects=trending,
        loving=projects["community_most_loved_projects"],
        remixed=projects["community_most_remixed_projects"],
    )


@app.get("/trending")
def trending():
    """
    Explore page.
    """
    projects = dazzle.get_trending_projects()
    if filter := request.args.get("filter"):
        return render_template("trending.html", filter=filter)
    return stream_template("trending.html")

@app.get("/api/trending/")
def get_trending():
    """
    Gets trending projects and returns them as json

    Requires a `page` argument in url
    """
    return dazzle.get_trending_projects(40, int(request.args.get("page")))

@app.get("/forums")
def categories():
    """
    A page that lists all the subforums in the forums
    """
    return render_template(
        "forums.html",
        data=subforums_data,
        pinned_subforums=user_data["pinned_subforums"],
        legacy_layout=user_data["use_old_layout"],
    )


@app.get("/forums/<subforum>")
def topics(subforum):
    """
    A page that lists all the topics in the subforum
    """

    sf_page = request.args.get("page")

    try:
        response = dazzle.get_topics(subforum, sf_page)
    except requests.exceptions.ReadTimeout:
        return render_template(
            "_error.html",
            errdata={
                "code": 500,
                "name": "Internal server error",
                "description": "A request took too long and has been aborted. Please try again later, or check your internet connection.",
            },
        )

    if response["error"]:
        ErrorMessage = response["message"] if "message" in response.keys() else response["error"]
        print("Error when loading", subforum, sf_page, ErrorMessage)
        return render_template("scratchdb-error.html", err=ErrorMessage)
    return stream_template(
        "forum-topics.html",
        subforum=subforum,
        topics=response["topics"],
        pinned_subforums=user_data["pinned_subforums"],
        url=request.url,
        str=str,
        topic_page=int(sf_page),
        len=len,
    )


@app.get("/forums/topic/<topic_id>")
def topic(topic_id):
    """
    Shows all posts in a topic.
    """

    if post_to_save := request.args.get("save"):
        user_data["saved_posts"].append((topic_id, post_to_save))
    show_deleted_posts = user_data["show_deleted_posts"]

    topic_page = request.args.get("page")

    topic_data = dazzle.get_topic_data(topic_id)
    topic_posts = dazzle.get_topic_posts(topic_id, page=topic_page)

    if topic_data["error"]:
        ErrorMessage = topic_data["message"] if "message" in topic_data.keys() else topic_data["error"]
        print("Error when loading", topic_id, ErrorMessage)
        return render_template("scratchdb-error.html", err=ErrorMessage)
    if topic_posts["error"]:
        ErrorMessage = topic_posts["message"] if "message" in topic_posts.keys() else topic_posts["error"]
        print("Error when loading", topic_id, ErrorMessage)
        return render_template("scratchdb-error.html", err=ErrorMessage)
    data_dict = {
        "topic_id": topic_id,
        "topic_title": topic_data["data"]["title"],
        "topic_posts": [
            {"author_status": get_status(post["author"]), **post}
            for post in topic_posts["posts"]
        ],
        "topic_page": int(topic_page),
        "max_posts": user_data["max_topic_posts"],
        "show_deleted": show_deleted_posts,
        "list": list,
        "len": len,
        "get_pfp": dazzle.get_pfp_url,
        "get_status": get_status,
    }

    # if topic_id == 'Suggestions':
    #     return stream_template(
    #         "suggestions-post.html",
    #         **data_dict
    #     )
    # else:
    return stream_template("forum-topic.html", **data_dict)


@app.get("/img-fullscreen")
def img():
    return render_template("img.html", img_url=request.args.get("url"))


@app.get("/projects/scratch/<project_id>")
def scratchproject(project_id):
    return stream_template("projects-scratch.html", project_id=project_id)


@app.get("/projects/<project_id>")
def project(project_id):
    global user_data
    project_info = dazzle.get_project_info(project_id)
    if "error" in project_info.keys(): 
        ErrorMessage = project_info["message"] if "message" in project_info.keys() else project_info["error"]
        print("Error when loading", project_id, ErrorMessage)
        return render_template("scratchdb-error.html", err=ErrorMessage)
    try:
        project_name = project_info["title"]
        creator_name = project_info["username"]
    except Exception:
        try:
            project_name = project_info["title"]
            creator_name = project_info["author"]["username"]
        except Exception:
            project_name = "A scratch project..."
            creator_name = "A scratch user..."
    theme = user_data["theme"]
    if theme == "choco":  # add new elif at the end
        colour = "%23282320"
    elif theme == "hackerman":
        colour = "%23212820"
    elif theme == "ice":
        colour = "%23202d38"
    elif theme == "newspaper":
        colour = "%23c8c8c8"
    elif theme == "nord":
        colour = "%232e3440"
    elif theme == "gruvbox":
        colour = "%23282828"
    # elif theme == "new theme":
    # colour = "%23[hex colour]"
    ocular = dazzle.get_ocular(creator_name)
    ocular_colour = ocular["color"]
    if ocular_colour in (None, "null"):
        ocular_colour = "#999999"
    else:
        creator_name = str(creator_name) + " ●"  # add the dot
    ocular_colour = f"color:{ocular_colour}"
    if not DEBUG:
        return stream_template(
            "projects.html",
            project_id=project_id,
            colour=colour,
            name=project_name,
            creator_name=creator_name,
            ocularcolour=ocular_colour,
        )
    else:
        # scomments = scratchdb.get_comments(project_id)
        return stream_template(
            "projects.html",
            project_id=project_id,
            colour=colour,
            name=project_name,
            creator_name=creator_name,
            # comments=[{"username": comment["author"]["username"], "content": comment["content"], "visibility": comment["visibility"]} for comment in scomments],
            ocularcolour=ocular_colour,
        )


@app.route("/settings", methods=["GET"])
def settings():
    """
    Settings page.
    Change theme, status, link github account
    """
    for key, value in request.args.items():
        user_data[key.replace("-", "_")] = value
    return render_template(
        "settings.html",
        themes=get_themes(),
        str_title=str.title,
        values=[
            user_data["theme"],
            user_data["max_topic_posts"],
            user_data["show_deleted_posts"],
            user_data["ocular_ov"],
            user_data["use_sb2"],
            user_data["use_old_layout"],
        ],
    )


@app.get("/downloads")
def downloads():
    """old download page"""
    return render_template("download.html")


@app.get("/secret/dl_mockup")
def dl_mockup():
    return render_template("dlm.html")


@app.get("/pin-subforum/<sf>")
def pin_sub(sf):
    """route that pins a subforum"""

    def flatten_comprehension(matrix):
        return [item for row in matrix for item in row]

    if sf not in flatten_comprehension(
        [subforum for subforum in [subforums for _, subforums in subforums_data]]
    ):
        return '<script>alert("Haha nice try ;)"); history.back()</script>'

    if sf not in user_data["pinned_subforums"]:
        arr = user_data["pinned_subforums"].copy()
        arr.append(sf)
        user_data["pinned_subforums"] = arr
        return "<script>history.back();</script>"
    else:
        return '<script>alert("You already pinned this!"); history.back()</script>'


@app.get("/unpin-subforum/<sf>")
def unpin_sub(sf):
    """route that unpins a subforum"""
    if sf in user_data["pinned_subforums"]:
        arr = user_data["pinned_subforums"].copy()
        arr.remove(sf)
        user_data["pinned_subforums"] = arr
        return "<script>history.back();</script>"


@app.get("/handle-scratch-auth")
def scratch_auth():
    if not request.args:
        try:
            if sa_login := dazzle.get_redirect_url():
                return redirect(sa_login)
        except SyntaxError:
            return render_template("")
        return "<script>alert('Auth failed');history.back()</script>"
    code = request.args.get("privateCode")
    session_id = dazzle.login(code)
    response = make_response(
        "<h1>Login successful</h1><script>window.location.href = `${window.location.protocol}//${window.location.host}`</script>"
    )
    response.set_cookie("snazzle-token", session_id, timedelta(days=30))

    return response


@app.route("/search", methods=["POST", "GET"])  # search feature
def search():
    query = request.form["query"]
    result = dazzle.search_for_projects(query)
    return stream_template("search.html", result=result, query=query)


# Studio pages
@app.get("/studios/<id>/<tab>")
def studios(id, tab):
    data = dazzle.get_studio_data(id)
    if "error" in data.keys():
        ErrorMessage = data["message"] if "message" in data.keys() else data["error"]
        print("Error when loading", id, ErrorMessage)
        return render_template("scratchapi-error.html", message=ErrorMessage)

    return render_template(
        "studio.html",
        studio_name=data["title"],
        studio_description=data["description"],
        studio_id=id,
        studio_tab=tab,
        studio_banner=data["image"],
        studio_stats=data["stats"],
        name_len=len(data["title"]),
    )

@app.get("/editor")
def editor():
    return render_template("editor.html")

@app.errorhandler(werkexcept.NotFound)
def err404(e: Exception):
    # route for error
    return render_template("_error.html", errdata=e), 404


# CHANGE THIS IF YOU'RE RUNNING A PUBLIC SERVER
if __name__ == "__main__":
    dazzle.init_db()
    webbrowser.open(f"{HOST}:{PORT}", 2)
    app.run(host=HOST, port=PORT, debug=FLASK_DEBUG)
