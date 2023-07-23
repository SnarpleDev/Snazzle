from flask import Flask, render_template, stream_template, request, redirect
from werkzeug import exceptions as werkexcept
import scratchdb

app = Flask(__name__)

DBG = {}
DBG['signed_in'] = False

data = (("Welcome", ["Announcements", "New Scratchers"]),
        ("Making Scratch Projects", ["Help with Scripts", "Show and Tell", "Project Ideas", "Collaboration", "Requests", "Project Save & Level Codes"]),
        ("About Scratch", ["Questions about Scratch", "Suggestions", "Bugs and Glitches", "Advanced Topics", "Connecting to the Physical World", "Scratch Extensions", "Open Source Projects"]),
        ("Interests Beyond Scratch", ["Things I'm Making and Creating", "Things I'm Reading and Playing"]))

user_data = dict(user_theme="choco",user_name="CoolScratcher123")

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
        signed_in=True,
        get_sfid_from_name=get_sfid_from_name,
        to_str=lambda x: str(x),
        get_author_of=scratchdb.get_author_of,
        len=len
    )

@app.get('/')
def index():
    return stream_template('index.html')

@app.get('/dbg')
def debug():
    # unused route to change debug settings
    DBG[request.args.get('k')] = request.args.get('v')
    return redirect('/')

@app.get('/editor')
def editor():
    # unused editor page
    return render_template('editor.html')

@app.get('/trending')
def trending():
    return render_template('trending.html')

@app.get('/forums')
def categories():
    return render_template('forums.html', data=data)

@app.get('/forums/<category>')
def topics(category):
    return render_template('forum-topics.html', category=category, topics=scratchdb.get_topics(category))

@app.get('/topic/<topic_id>')
def topic(topic_id):
    return f'<a href="https://scratch.mit.edu/discuss/topic/{topic_id}">view on scratch</a>'

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

@app.errorhandler(werkexcept.NotFound)
def err404(e):
    # route for 404 error
    return render_template('_err404.html'), 404

app.run(host='127.0.0.1', port=3000, debug=True)