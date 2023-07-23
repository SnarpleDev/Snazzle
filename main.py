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

user_data = dict(user_theme="choco",user_name="CoolScratcher123")

@app.context_processor
def context():
    # Play with this and the user_data dict to manipulate app state
    return dict(
        theme=user_data['user_theme'],
        username=user_data['user_name'],
        signed_in=False
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
def forums():
    return render_template('forums.html', data=data)

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

@app.errorhandler(werkexcept.NotFound)
def err404(e):
    # route for 404 error
    return render_template('_err404.html'), 404

app.run(host='127.0.0.1', port=3000, debug=True)