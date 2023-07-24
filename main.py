from flask import Flask, render_template, stream_template, request, redirect
from werkzeug import exceptions as werkexcept
import scratchdb

app = Flask(__name__)

HOST, PORT = '127.0.0.1', 3000

subforums_data = (("Welcome", ["Announcements", "New Scratchers"]),
        ("Making Scratch Projects", ["Help with Scripts", "Show and Tell", "Project Ideas", "Collaboration", "Requests", "Project Save & Level Codes"]),
        ("About Scratch", ["Questions about Scratch", "Suggestions", "Bugs and Glitches", "Advanced Topics", "Connecting to the Physical World", "Scratch Extensions", "Open Source Projects"]),
        ("Interests Beyond Scratch", ["Things I'm Making and Creating", "Things I'm Reading and Playing"]),
        ("My category", ["My subforum"]))

user_data = dict(user_theme="choco",user_name="CoolScratcher123",pinned_subforums=[])

# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(r):
    """
    Stops the page from being cached so that the forums actually work correctly
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    print(r)
    return r

@app.context_processor
def context():
    # Play with this and the user_data dict to manipulate app state
    return dict(
        theme=user_data['user_theme'],
        username=user_data['user_name'],
        signed_in=False,
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

@app.get('/forums/<subforum>')
def topics(subforum):
    response = scratchdb.get_topics(subforum)
    if response['error']:
        return render_template('scratchdb-error.html', err=response['message'])
    return stream_template('forum-topics.html', subforum=subforum, topics=response['topics'], pinned_subforums=user_data["pinned_subforums"])

@app.get('/topic/<topic_id>')
def topic(topic_id):
    return f'<a href="https://scratch.mit.edu/discuss/topic/{topic_id}">view on scratch</a> (for now while we get the forums fully working and not slow as hell)'

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

@app.get('/pin-subforum/<sf>')
def pin_sub(sf):
    if not sf in user_data["pinned_subforums"]:
        arr = user_data["pinned_subforums"].copy()
        arr.append(sf)
        user_data['pinned_subforums'] = arr
        return f'<script>history.back();</script>'
    else:
        return '<script>alert("You already pinned this!"); history.back()</script>'
    
@app.get('/unpin-subforum/<sf>')
def unpin_sub(sf):
    if sf in user_data["pinned_subforums"]:
        arr = user_data["pinned_subforums"].copy()
        arr.remove(sf)
        user_data['pinned_subforums'] = arr
        return f'<script>history.back();</script>'
    else:
        return '<script>alert("This is not pinned!");</script>'

@app.errorhandler(werkexcept.NotFound)
def err404(e):
    # route for 404 error
    return render_template('_err404.html', errdata=e), 404

app.run(host=HOST, port=3000, debug=True)