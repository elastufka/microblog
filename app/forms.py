from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField,SubmitField, TextAreaField, FieldList,FormField, Form
from wtforms.validators import ValidationError, DataRequired, InputRequired, Email, EqualTo,DataRequired, Length
from app.models import User
from flask_babel import _,lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
            
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class TemplateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    nteams = IntegerField('Number of Teams', validators=[DataRequired()])
    #for i in range(nteams):
    #    teamname=StringField(f"Team {i+1} Name") #if not, then use numbers
    npoints = IntegerField('Number of Points to win')
    #duration = IntegerField('Duration of Game') #should be clock thingy - time field
    segments = IntegerField('Game format') #checkbox - halves, quarters, innings, etc
    submit = SubmitField('Start')

class TeamNameForm(Form):
    #def __init__(self,nteams,*arg, **kwarg):
    #    super(TeamNameForm, self).__init__(*arg, **kwarg)
    #    self.team_name=StringField('Team {teams}', default=f'Team {teams}')
    team_name=StringField(default=True)#, default=f'Team {teams}')
        #self.submit = SubmitField('Go!')

class CurrentGameForm(FlaskForm):
#    def __init__(self, *arg, **kwarg):
#        #self.game_name=name
#        self.hidden=None
#
#    def get_form(self,nteams,*arg, **kwarg):
#        #game_name = StringField('Name your game', default='New Game')
#        teams=FieldList(FormField(TeamNameForm),min_entries=2)
#        return TeamNameForm(teams)
    teams=FieldList(FormField(TeamNameForm),min_entries=1)
    submit = SubmitField('Go!')

class PastGameForm(FlaskForm):
    name = StringField('Name', default='New Game')
    team1 = StringField('Team 1', default='Team 1')
    #for i in range(nteams):
    #    teamname=StringField(f"Team {i+1} Name") #if not, then use numbers
    score1 = IntegerField('Score',validators=[InputRequired()])
    team2 = StringField('Team 2',default='Team 2')
    score2 = IntegerField('Score',validators=[InputRequired()]) #should be clock thingy - time field

    submit = SubmitField('Save Record')
