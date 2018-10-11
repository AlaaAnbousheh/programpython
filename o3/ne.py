class ServerForm(Form):

    hostname = StringField('hostname', [validators.Length(min=1, max=200)])
    hostusername = StringField('hostusername', [validators.Length(min=4, max=200)])
    hostpassword = StringField('hostpassword', [validators.Length(min=0, max=200)])


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
        db,mycursor,flag=connect_server(tserver)
            if flag:
                # Passed
                session['hostlogged_in'] = True
                flash('server is connected you can log in', 'success')
                return redirect(url_for('login'))
            else:
                error = 'Failed to connect server, please try again'
                return render_template('/hosting.html', error=error)

     return render_template('/hosting.html')









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
