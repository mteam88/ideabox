"""
flask app that shows a list of ideas from a database
the database is a sqlite database
the app has a form to add new ideas
each ideas is automatically deleted after 30 days
"""

from datetime import datetime #, timedelta
import shelve
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template, request, redirect

DATABASE_PATH = 'shelve-database.db'
# intialize the shelve database
with shelve.open(DATABASE_PATH) as db:
    try:
        db["ideas"]
    except KeyError:
        db["ideas"] = []

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        idea_text = request.form['ideatext']
        print(f"idea added: {idea_text}")
        try:
            with shelve.open(DATABASE_PATH, writeback=True) as shelf:
                shelf["ideas"].append({"idea_time": datetime.now(), "idea_text": idea_text})
            return redirect('/')
        except:
            return 'There was an issue adding your idea'
    else:
        with shelve.open(DATABASE_PATH, writeback=True) as shelf:
            ideas = shelf["ideas"]
        return render_template('index.html', ideas=ideas)
        
@app.route('/about')
def about():
    return render_template('about.html')

def delete_old_ideas():
    "delete ideas older than 30 days"
    with shelve.open(DATABASE_PATH, writeback=True) as shelf:
        ideas = shelf["ideas"]
        for idea in ideas:
            if (datetime.now() - idea["idea_time"]).days > 30:
                print(f"idea deleted: {idea['idea_text']}")
                ideas.remove(idea)
        shelf["ideas"] = ideas

if __name__ == "__main__":
    deleter = BackgroundScheduler()
    deleter.add_job(func=delete_old_ideas, trigger="interval", seconds=800)
    deleter.start()
    app.run(debug=True)
