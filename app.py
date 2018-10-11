from dash import Dash
from functools import wraps
from dash.dependencies import Output, Event ,Input ,State
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import mysql.connector
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import flask
import os
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_bootstrap import Bootstrap
from flask import Flask, render_template , flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
#CREATE TABLE IF NOT EXISTS user_raspberry (ID int NOT NULL AUTO_INCREMENT, Email varchar(20), Username varchar(20), Password varchar(20),PRIMARY KEY (ID))

tserver = ("localhost","root","")


def sconnect_server(tserver):
    flag=False
    cursor=''
    db=''
    try:
        serverlist=list(tserver)
        mydb = mysql.connector.connect(
          host=serverlist[0],
          user=serverlist[1],
          passwd=serverlist[2],

        )
        cursor=mydb.cursor()
        db=mydb
        flag=True

    except Exception as e:
            cursor=e
    return db,cursor,flag

def connect_server(tserver,mydatabase):
    flag=False
    cursor=''
    db=''
    try:
        serverlist=list(tserver)
        mydb = mysql.connector.connect(
          host=serverlist[0],
          user=serverlist[1],
          passwd=serverlist[2],
          database=mydatabase
        )
        cursor=mydb.cursor()
        db=mydb
        flag=True

    except Exception as e:
            cursor=e
    return db,cursor,flag



min_date=dt.strptime('2018-01-20T01:02', '%Y-%m-%dT%H:%M')
max_date=dt.strptime('2018-01-20T01:02', '%Y-%m-%dT%H:%M')


server = flask.Flask(__name__)
Bootstrap(server)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashapp1/' )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/dashapp2/')

dash_app1.title = 'Dash Static'
dash_app1.layout = html.Div([
          html.Div(
              html.A(html.Button('Home', className='one columns',  style = {'float': 'right',   'background-color': 'white'}),
                 href='http://127.0.0.1:8080/home' ,
                    )
                    ),


              html.Div(
                     children='Data Visualization',
                     style={
                            'color': 'black',
                            #'border': '2px green solid',
                            'padding':'20px',
                           'font-size': 'large',
                         'textAlign': 'center'
                     }
                 ),
             html.P(html.Label('Start Time:')),
             dcc.Input(
             id='start-time-input',
             type='datetime-local',
             value=dt.strftime(min_date, '%Y-%m-%dT%H:%M'),

             className='form-control'
             ),


             html.P(html.Label('End Time:')),
             dcc.Input(
             id='end-time-input',
             type='datetime-local',
             min=dt(1995, 8, 5),
             max=dt(2017, 9, 19),
             value=dt.strftime(max_date, '%Y-%m-%dT%H:%M'),
             className='form-control'
             ),

             html.P(html.Button(id='submit-button', n_clicks=0, children='OK')),

             html.P(html.Label('Channel selection :')),
             dcc.Dropdown(id='drop_id',
             options=[
                 {'label': 'Channel 1', 'value': 'ch1'},
                 {'label': 'Channel 2', 'value': 'ch2'},
                 {'label': 'channel 3', 'value': 'ch3'}
             ],

             value='None',
             multi=True
             ),

             dcc.Graph(id='graph')





])



@dash_app1.callback(Output(component_id='graph'  , component_property='figure'),
              [
              Input('submit-button', 'n_clicks'),
              Input(component_id='drop_id' , component_property='value')
              ],
              [
              State('start-time-input', 'value'),
              State('end-time-input', 'value')
              ]
              )

def print_str(n_clicks ,channel,start,end ):

    db,mycursor,flag=connect_server(tserver,'abc')
    # ORDER BY Date DESC LIMIT 20

    mycursor.execute("SELECT A0,A1,A2,Date FROM adc_signal ")
    rows = mycursor.fetchall()
    str(rows)[0:5000]
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'A0', 1: 'A1', 2: 'A2', 3: 'Date'}, inplace=True);
    global min_date
    min_date=min(df['Date'])
    global max_date
    max_date=max(df['Date'])
    traces=[]
    start =dt.strptime(start, '%Y-%m-%dT%H:%M')
    end =dt.strptime(end , '%Y-%m-%dT%H:%M')
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    df = df.loc[mask]
    df=df.sort_values(by=['Date'])
    print(df)
    t1= go.Scatter(
        x=df['Date'],
        y=df['A0'],
         fill='tozeroy',
        mode = 'lines+markers',
        line=dict(shape='spline'),
        name='ch1',
        marker = {
            'size': 2,
            'color': 'rgb(39, 108, 221)',
            'symbol':'pentagon',
            'line': {'width': 5}
            }
    )

    t2= go.Scatter(
    x=df['Date'],
    y=df['A1'],

     fill='tozeroy',
    mode = 'lines+markers',
    line=dict(shape='spline'),
    name='ch2'
    )

    t3= go.Scatter(
    x=df['Date'],
    y=df['A2'],
     fill='tozeroy',

    mode = 'lines+markers',
    line=dict(shape='spline'),
    name='ch3'
    )

    for tic in channel:
        if(tic=='ch1'):
            traces.append(t1)

        if(tic=='ch2'):
            traces.append(t2)
        if(tic=='ch3'):
            traces.append(t3)



    return {'data': traces,'layout' : go.Layout(
        title = 'Channel',
        xaxis = {'title': 'Time'},
        yaxis = {'title': 'Value'},
        hovermode='closest'
    )}
dash_app2.title = 'Dash Live'
dash_app2.layout = html.Div([
  html.Div(
         html.A(html.Button('Home', className='one columns',  style = {'float': 'right',   'background-color': 'white'}),
           href='http://127.0.0.1:8080/home' ,
              )
              ),
     html.Div(
            children='Data Visualization',
            style={
                   'color': 'black',
                  # 'border': '2px green solid',
                  'padding' : '20px',
                  'font-size': 'large',
                'textAlign': 'center'
            }
        ),

        dcc.Graph(id='live-graph'),
        dcc.Interval(
            id='graph-update',
            interval=1*1000 ,
            n_intervals=0

            )
])
@dash_app2.callback(Output('live-graph', 'figure'),
             [Input('graph-update', 'n_intervals')])

def update_graph_scatter(n):
    db,mycursor,flag=connect_server(tserver,'abc')
    if  flag:
        mycursor.execute("SELECT A0,A1,A2,Date FROM adc_signal ORDER BY Date DESC LIMIT 20")
        rows = mycursor.fetchall()
        str(rows)[0:5000]
        df = pd.DataFrame( [[ij for ij in i] for i in rows] )
        df.rename(columns={0: 'A0', 1: 'A1', 2: 'A2', 3: 'Date'}, inplace=True);
        df.sort_values('Date', inplace=True)
        X = df['Date']
        Y = df['A0']
        data = go.Scatter(
            x=X,
            y=Y,
             fill='tozeroy',
             mode= 'lines+markers',
            line=dict(shape='spline'),
            marker = {
                'size': 2,
                'color': 'rgb(39, 108, 221)',
                'symbol':'pentagon',
                'line': {'width': 5}
                }
    )


        return {'data': [data],'layout' : go.Layout(
            title = 'Channel1',
            xaxis = {'title': 'Time'},
            yaxis = {'title': 'Value'},
            hovermode='closest'
        )}

    else:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
    '/dash2': dash_app2.server
})

css_directory = os.getcwd()
stylesheets = ['stylesheet.css']
static_css_route = '/static/'



@dash_app1.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return flask.send_from_directory(css_directory, stylesheet)


for stylesheet in stylesheets:
    dash_app1.css.append_css({"external_url": "/static/{}".format(stylesheet)})


for stylesheet in stylesheets:
    dash_app2.css.append_css({"external_url": "/static/{}".format(stylesheet)})

#   ---------------------------------------------------- Server login




class ServerForm(Form):

    hostname = StringField('hostname', [validators.Length(min=1, max=20)])
    hostusername = StringField('hostusername', [validators.Length(min=4, max=20)])
    hostpassword = StringField('hostpassword', [validators.Length(min=0, max=20)])



# connect server

# connect server
@server.route('/hosting', methods=['GET', 'POST'])
def serverfunc():
    global tserver
    form =  ServerForm(request.form)
    if request.method == 'POST' and form.validate():
            hostname = form.hostname.data
            hostusername = form.hostusername.data
            hostpassword = form.hostpassword.data
            tserver=(hostname,hostusername,hostpassword)
            db,mycursor,flag=sconnect_server(tserver)
            if flag:
                    # Passed
                    session['hostlogged_in'] = True
                    flash('server is connected you can log in', 'success')
                    return redirect(url_for('login'))
            else:
                    flash('server is not connected you can log in', 'danger')
                    return render_template('/hosting.html', form=form)
    return render_template('/hosting.html',form=form)







#  ----------------------------------------------- Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Passwords', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


#--------------- -----------------------------------------User Register
@server.route('/register', methods=['GET', 'POST'])

def register():
    serverlist=list(tserver)
    ghost=serverlist[0]
    guser=serverlist[1]
    gpasswd=serverlist[2]
    gdatabase="abc"
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        #password = sha256_crypt.encrypt(str(form.password.data),rounds=12345)
        password =form.password.data
        # Create cursor

        userdb = mysql.connector.connect(
              host=ghost,
              user=guser,
              passwd=gpasswd,
              database=gdatabase
            )
        usercursor = userdb.cursor()



        # Execute query
        usercursor.execute("INSERT INTO  user_raspberry( Email, Username, Passwords) VALUES(%s, %s, %s)", ( email, username, password))

        # Commit to DB
        userdb.commit()

        # Close connection
        usercursor.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#------------------------------------------------------------ User login
@server.route('/login', methods=['GET', 'POST'])
def login():
    serverlist=list(tserver)
    ghost=serverlist[0]
    guser=serverlist[1]
    gpasswd=serverlist[2]
    gdatabase="abc"
    userdb = mysql.connector.connect(
          host=ghost,
          user=guser,
          passwd=gpasswd,
          database=gdatabase
        )
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        usercursor = userdb.cursor()
        usercursor = userdb.cursor(dictionary=True)

        # Get user by username
        result =usercursor.execute("SELECT * FROM user_raspberry WHERE Email = '%s' "%(email))
        result = usercursor.fetchone()

        if result != 'None' :
            # Get stored hash
            data = result
            password = data['Passwords']
            username = data['Username']


            # Compare Passwords
            #hash = sha256_crypt.encrypt(password_candidate)

            #if sha256_crypt.verify(hash, password):
            if password_candidate == password:

                # Passed
                session['logged_in'] = True
                session['username'] = username.upper()

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('/login.html', error=error)
            # Close connection
            usercursor.close()
        else:
            error = 'Username not found'
            return render_template('/login.html', error=error)

    return render_template('/login.html')
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap
@server.route('/home')
def index():
    print (tserver)
    return flask.render_template('home.html')

@server.route('/dashapp1')
@is_logged_in

def render_dashboard():
    return flask.redirect('/dash1')


@server.route('/dashapp2')
@is_logged_in
def render_reports():
    return flask.redirect('/dash2')
@server.route('/logout')
@is_logged_in
def logout():

    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
    #------------------------------------------------------ disconnect server
@server.route('/hostdis')
def hostdis():

    session.clear()
    flash('server is disconnected Now', 'danger')
    return flask.render_template('home.html')
#-------------------------------------------------------------- Dashboard
@server.route('/dashboard')
@is_logged_in
def dashboard():
    return flask.render_template('dashboard.html')
#--------------------------------------------------------------- default root
@server.route('/')
def homeRedir():
    print(session)
    return flask.render_template('home.html')
server.secret_key='secret123'
#------------------------------------------------------------------ register

run_simple('127.0.0.1', 8080, app, use_reloader=True, use_debugger=True )
