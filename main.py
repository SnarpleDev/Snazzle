from flask import Flask, render_template, stream_template, request, redirect
from werkzeug import exceptions as werkexcept
from werkzeug import http

app = Flask(__name__)

DBG = {}
DBG['signed_in'] = False

data = (("Welcome", ["Announcements", "New Scratchers"]),
        ("Making Scratch Projects", ["Help with Scripts", "Show and Tell", "Project Ideas", "Collaboration", "Requests", "Project Save & Level Codes"]),
        ("About Scratch", ["Questions about Scratch", "Suggestions", "Bugs and Glitches", "Advanced Topics", "Connecting to the Physical World", "Scratch Extensions", "Open Source Projects"]),
        ("Interests Beyond Scratch", ["Things I'm Making and Creating", "Things I'm Reading and Playing"]),
        ("Scratch Around the World", ["Hell naw I ain't putting in all that 💀"]))

available_themes = [
    'old', 'dark', 'choco', 'ice', 'hackerman'
]

user_data = dict(user_theme="dark")

@app.context_processor
def context():
    return dict(
        theme=user_data['user_theme'],
        username="redstone1080",
        signed_in=False
    )

@app.get('/')
def index():
    return stream_template('index.html')

@app.get('/dbg')
def debug():
    DBG[request.args.get('k')] = request.args.get('v')
    return redirect('/')

@app.get('/editor')
def editor():
    return render_template('editor.html')

@app.get('/trending')
def trending():
    return render_template('trending.html')

@app.get('/forums')
def forums():
    return render_template('forums.html', data=data)

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    return render_template('settings.html', available_themes=available_themes)

@app.get('/change_theme')
def theme_change():
    requested_theme = request.args.get('theme')
    if requested_theme in available_themes:
        user_data['user_theme'] = requested_theme
    return redirect('/settings')

@app.get('/downloads')
def downloads():
    return render_template('download.html')

@app.errorhandler(werkexcept.NotFound)
def err404(e):
    return render_template('_err404.html'), 404

app.run(host='127.0.0.1', port=3000, debug=True)