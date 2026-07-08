from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("HomePage.html")

# Home page to about page
@app.route('/about')
def about():
    return render_template('about.html')

#  Home page to voice page
@app.route('/voice')
def voice():
    return render_template('voice.html')

# Home page to projects page
@app.route("/projects")
def projects():
    return render_template("projects.html")

# Home page to personalize page
@app.route("/personalize")
def personalize():
    return render_template("personalize.html")

# Home page to background page 
@app.route('/Background')
def background():
    return render_template('Change_BackgroundVideos.html')

# Home page to setting page
@app.route('/setting')
def setting():
    return render_template('settings.html')

# Home page to upgrade page
@app.route('/upgrade')
def upgrade():
    return render_template('upgrade.html')


# Home page to Help button pop up option common issue page 
@app.route('/common-issues')
def common_issues():
    return render_template('components/Common_Issue.html')


# Home page to Help button pop up option Personal issue page 
@app.route('/personal-issue')
def personal_issue():
    return render_template('components/Personal_Issue.html')


@app.route('/login')
def login():
    return render_template('auth/login.html')


@app.route('/signup')
def signup():
    return render_template('auth/signup.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')

if __name__ == "__main__":
    app.run(debug=True)