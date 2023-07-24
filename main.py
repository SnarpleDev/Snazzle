from flask import Flask, render_template, stream_template, request, redirect
from werkzeug import exceptions as werkexcept
import scratchdb

app = Flask(__name__)

HOST, PORT = '127.0.0.1', 3000

subforums_data = (("Welcome", ["Announcements", "New Scratchers"]),
        ("Making Scratch Projects", ["Help with Scripts", "Show and Tell", "Project Ideas", "Collaboration", "Requests", "Project Save & Level Codes"]),
        ("About Scratch", ["Questions about Scratch", "Suggestions", "Bugs and Glitches", "Advanced Topics", "Connecting to the Physical World", "Scratch Extensions", "Open Source Projects"]),
        ("Interests Beyond Scratch", ["Things I'm Making and Creating", "Things I'm Reading and Playing"]))

user_data = dict(user_theme="choco",user_name="CoolScratcher123",pinned_subforums=[])

categories = {
    "Announcements": 5,
    "New Scratchers": 6,
    "Help with Scripts": 7,
    "Show and Tell": 8,
    "Project Ideas": 9,
    "Collaboration": 10,
    "Requests": 11,
    "Project Save & Level Codes": 60,
    "Questions about Scratch": 4,
    "Suggestions": 1,
    "Bugs and Glitches": 3,
    "Advanced Topics": 31,
    "Connecting to the Physical World": 32,
    "Developing Scratch Extensions": 48,
    "Open Source Projects": 49,
    "Things I'm Making and Creating": 29,
    "Things I'm Reading and Playing": 30
}

def get_sfid_from_name(name):
    return categories[name] or 0

def get_name_from_sfid(sfid):
    arr = [None] * (max(categories.values()) + 1)
    for key, value in categories.items():
        arr[value] = key
    return arr

@app.context_processor
def context():
    # Play with this and the user_data dict to manipulate app state
    return dict(
        theme=user_data['user_theme'],
        username=user_data['user_name'],
        signed_in=False,
        get_sfid_from_name=get_sfid_from_name,
        to_str=lambda x: str(x),
        get_author_of=scratchdb.get_author_of,
        len=len,
        host=HOST
    )

@app.get('/')
def index():
    return stream_template('index.html')

@app.get('/editor')
def editor():
    # unused editor page
    return render_template('editor.html')

@app.get('/trending')
def trending():
    return render_template('trending.html')

@app.get('/forums')
def categories():
    return render_template('forums.html', data=subforums_data, pinned_subforums=user_data["pinned_subforums"])

@app.get('/forums/<category>')
def topics(category):
    topic_list = scratchdb.get_topics(category)
    if not topic_list:
        return
    return stream_template('forum-topics.html', category=category, topics=topic_list)

@app.get('/topic/<topic_id>')
def topic(topic_id):
    return f'<a href="https://scratch.mit.edu/discuss/topic/{topic_id}">view on scratch</a> (for now while we get the forums fully working and not slow as hell)'

@app.get('/projects/<project_id>')
def project(project_id):
    return f'<iframe src="https://turbowarp.org/{project_id}/embed" width="499" height="416" allowtransparency="false" frameborder="0" scrolling="no" allowfullscreen></iframe>'

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    # will have a form to change theme, instead of /change_theme
    return render_template('settings.html')

@app.get('/change_theme')
def theme_change():
    # to-be-unused route to change theme
    requested_theme = request.args.get('theme')
    user_data['user_theme'] = requested_theme
    return redirect('/settings')

@app.get('/downloads')
def downloads():
    # old download page
    return render_template('download.html')

@app.get('/secret/dl_mockup')
def dl_mockup():
    return render_template('dlm.html')

@app.get('/pin-subforum')
def pin_sub():
    sf = request.args.get('subforum')
    if not sf in user_data["pinned_subforums"]:
        arr = user_data["pinned_subforums"].copy()
        arr.append(request.args.get('subforum'))
        user_data['pinned_subforums'] = arr
        return redirect('/forums/' + request.args.get('subforum'))
    else:
        return '<script>alert("You already pinned this!");</script>'

@app.errorhandler(werkexcept.NotFound)
def err404(e):
    # route for 404 error
    return render_template('_err404.html'), 404

app.run(host=HOST, port=3000, debug=True)