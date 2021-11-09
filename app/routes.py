from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Post, CompletedBoard, BoardTemplate
from flask import request,g
from werkzeug.urls import url_parse
from flask_login import login_required
from app import app,db, cache
from app.forms import *
from datetime import datetime
from app.email import send_password_reset_email
from flask_babel import _,get_locale
from wtforms import Label
import json
import copy

@app.before_request
def before_request():
    g.locale = str(get_locale())
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    if cache.get('current_game') is not None: #give option to resume current game
        #add button or list item to resume current game
        pass
    form=TemplateForm()
    if form.validate_on_submit():
        #name=form.name.data
        #nteams=form.nteams.data
        cache.clear()
        board = BoardTemplate(name=form.name.data,nteams=form.nteams.data, npoints=form.npoints.data,segments=form.segments.data)
        db.session.add(board) #how to delete after use?
        db.session.commit()
        #flash(_('Your post is now live!'))
        cache.add("nteams", board.nteams)
        #cache.add("name", board.name)
        return redirect(url_for('new_game_setup'))
        
    #else select an option from existing templates

    return render_template('index.html', title='Quick Score', form=form) #no records

@app.route('/new_game_setup', methods=['GET','POST'])
def new_game_setup():
    #name = cache.get("name")
    nteams = cache.get("nteams")
    team_start=[]
    for n in range(nteams):
        team_start.append({"team_name":f"Team {n+1}"})
    form = CurrentGameForm(teams=team_start)

    for n,team in enumerate(form.teams):
        team.label=Label(team.id,f"Team {n+1}")
        #print(team.team_name(class_='form_control')) #html that goes into rendering form
    
    if form.validate_on_submit():
        teamnames=[]
        for team in form.teams:
            teamnames.append(team.data)
        #cache teamnames...
        for team_name in teamnames:
            team_name['team_id']=team_name['team_name'].replace(' ','_')
            team_name['scorestr']=team_name['team_id']+'_score'
        cache.add("teamnames", teamnames)
 
        #teamnames=form.teams.data
        return redirect(url_for('new_game'))
    return render_template('new_game_setup.html',form=form)

@app.route('/new_game', methods=['GET','POST'])
def new_game():
    if request.method == "GET":
        #remove any flashed messages...
        #session['_flashes'].clear()
        
        nteams = cache.get("nteams")
        teamnames = cache.get("teamnames")
        current_game=cache.get("current_game")
        #print(current_game)
        if current_game is None:
            game=[{'timestamp':datetime.now(),'type':'game_start'}]
            for teamn in teamnames:
                game[0][f"{teamn['team_id']}_score"]=0
                game[0][f"{teamn['team_id']}_TO"]=0
            cache.add('current_game',game)
            game=game[0]
        else:
            game=current_game[-1] #latest row
    elif request.method=='POST': #save or end game...
        if request.form.get('save'): #data is already in cache
            #current_game=request.get_data()
            #print(teamnames,scores,current_game)
            #cache.set("current_game",current_game)
            flash(_('Game Saved!'))
            return redirect(url_for('new_game'))
        elif request.form.get('game_over'):
            current_game=cache.get('current_game')
            final_score=current_game[-1]
            teamnames = cache.get("teamnames")
            greatest_score=0
            for team in teamnames:
                if final_score[team['team_id']+'_score'] > greatest_score:
                    winning_team=team['team_name']
                    greatest_score=final_score[team['team_id']+'_score']
            flash(_(f'Game Over! {winning_team} wins! <br><a href="/index">Back to index</a>'))
            #if logged in, save (whole game or final score) to history
            record = CompletedBoard(owner=current_user,team1=teamnames[0]['team_name'], team2=teamnames[1]['team_name'],score1=final_score[teamnames[0]['team_id']+'_score'],score2=final_score[teamnames[1]['team_id']+'_score']) #this will change later anyway
            db.session.add(record)
            db.session.commit()
            #clear cache
            game=final_score
            cache.clear()
            #freeze scoreboard somehow...
            
    return render_template('new_game.html',teamnames=teamnames,game=game)

@app.route('/increment', methods=['GET','POST'])
def increment():
    '''js updates contents of /increment? not sure...'''
    current_game = cache.get("current_game")
    #print('len current_game',len(current_game))
    if request.method == "POST":
        tnow=datetime.now()
        changed_score = request.get_json()
        print('POST',changed_score,tnow)
        this_point=copy.deepcopy(current_game[-1])
        this_point['timestamp']=tnow
        this_point['type']=changed_score['type']
        this_point[changed_score['type']]=changed_score['score']
        print('this_point',this_point)
    result={'new_score':changed_score}
    current_game.append(this_point)
    #print('updated',current_game)
    #just cache it...
    cache.set("current_game",current_game) #is there cache.update?
    return json.dumps(result)
    #return render_template('new_game.html',teamnames=teamnames)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)
                           
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
#    posts = [
#        {'author': user, 'body': 'Test post #1'},
#        {'author': user, 'body': 'Test post #2'}
#    ]

    page = request.args.get('page', 1, type=int)

    try:
        records = current_user.records().paginate(page, app.config['POSTS_PER_PAGE'], False)
#        next_url = url_for('index', page=records.next_num) \
#        if records.has_next else None
#        prev_url = url_for('index', page=records.prev_num) \
#       if records.has_prev else None
        return render_template('user.html', user=user,posts=records.items)
    except AttributeError:
        return render_template('user.html', user=user, posts=None)
    
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
    
@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    try:
        records = current_user.records().paginate(
            page, app.config['POSTS_PER_PAGE'], False)

        next_url = url_for('history', page=records.next_num) \
            if records.has_next else None
        prev_url = url_for('history', page=records.prev_num) \
           if records.has_prev else None
        return render_template('history.html', title='Records',
                               posts=records.items, next_url=next_url,prev_url=prev_url)
    except AttributeError:
        return render_template('history.html', title='Records', posts=[]) #no records

@app.route('/edit_history', methods=['GET', 'POST'])
@login_required
def edit_history():
    form=PastGameForm()
    if form.validate_on_submit():
        record = CompletedBoard(owner=current_user,team1=form.team1.data, team2=form.team2.data,score1=form.score1.data,score2=form.score2.data)
        db.session.add(record)
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('history'))
#    elif request.method == 'GET':
#        form.owner.data = current_user.username
#        form.about_me.data = current_user.about_me
    return render_template('edit_history.html', title='Edit History',
                           form=form)



@app.route('/templates')
@login_required
def templates():
    posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!'
            },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!'
            }
        ]
    return render_template('templates.html', title='Scoreboards', posts=posts)

@app.route('/edit_template', methods=['GET', 'POST'])
#@app.route('/')
#@app.route('/index')#@login_required
def edit_template():
    form = TemplateForm()
#    if form.validate_on_submit():
#        current_user.username = form.username.data
#        current_user.about_me = form.about_me.data
#        db.session.commit()
#        flash('Your changes have been saved.')
#        return redirect(url_for('edit_template'))
#    elif request.method == 'GET':
#        form.username.data = current_user.username
#        form.about_me.data = current_user.about_me
    return render_template('edit_template.html', title='Edit Template',
                           form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
