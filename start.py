from flask import Flask,render_template,request,redirect,url_for,session,logging,request,flash
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='amit'
app.config['MYSQL_PASSWORD']='asdf'
app.config['MYSQL_DB']='myapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql=MySQL(app)



@app.route('/')
def index():
    return render_template("index.html")
@app.route('/home')
def home():
    return render_template("home.html")
@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")
@app.route('/articles')
def articles():
    return render_template("articles.html")

@app.route('/post/<string:id>')
def post(id):
    return render_template("post.html",id=id)

#registration forms  page for users
class RegisterForm(Form):
    name=StringField("Enter your Full Name", [validators.length(min=1,max=50)],render_kw={"placeholder": "Amit rai"})
    username = StringField("Choose Username", [validators.length(min=1, max=50)],render_kw={"placeholder": "my username"})
    email = StringField("email", [validators.length(min=1, max=20)],render_kw={"placeholder": "email@example.com"})
    password = PasswordField("password", [validators.DataRequired(),validators.EqualTo('confirm', message="no match")],render_kw={"placeholder": "password"})
    confirm=PasswordField('confirm password')
    jee=StringField("Enter your JEE marks",[validators.length(min=1,max=3)],render_kw={"placeholder": "Enter your JEE marks"})
    cet=StringField("Enter your CET marks",[validators.length(min=1,max=3)],render_kw={"placeholder": "Enter your CET marks"})

#registration form frontend logic and database connection
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        jee=form.jee.data
        cet=form.cet.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor() #cursore to connect datatbase
        #quarry to execute the insertion into database
        cur.execute("INSERT INTO users(name, email, username, password,jee,cet) VALUES(%s, %s, %s, %s,%s,%s)", (name, email, username, password,jee,cet))
        #commete to the database
        mysql.connection.commit()
        #college connection
        cur.close()
        flash('You are now registered and can log in' )

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#login form front end
@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']#connection for login.html
        password_candidate = request.form['password'] #this the the password entered by users

        # this is to connect the database to mysql data base cursore
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password'] #fatch the password to for the username

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):#this is to comapare the password user entered and stored in database
                # if the stored password matches this will start a session for the user
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('myprofile',))#after sucessful login redirect user to the myprofile page
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template("login.html")

def is_logged_in(f): #this is tp protrct the users from getng access with out login
  @wraps(f)
  def wrap(*args,**kwards):
     if "logged_in" in session:
       return f(*args)
     else:
        flash("please login")
        return redirect(url_for("login"))
  return wrap






@app.route('/myprofile') #route for profile page
@is_logged_in #cant access with login
def myprofile():

    return render_template("myprofile.html",)

@app.route('/college/<string:location>/') #route for page with the location, location is retrive from myprofile page
def college(location): #location is paseed in the defination college
    cur = mysql.connection.cursor() #creating a connection to mysql
    result = cur.execute("SELECT * FROM collegedata WHERE location = %s",[location]) #get the colleges by location, location is passed from myprofile page
    data = cur.fetchall() #fatched all the colleges and store in the data
    data1=location #onlu store the location
    if result > 0:
        return render_template('college.html', clocation=data,data1=location) #passes the location and all colleges to college.html
    else:
        msg = 'No nocollege Found'
        return render_template('college.html', msg=msg) #if no colleges found return massega no college is found
        # Close connection
    cur.close() #connection to data base is closed

@app.route('/college/<string:location>/data/<string:nameofc>') #for particular college location and name of the college is passed
def collegedetail(location,nameofc): #location and name of the college is passed, location and name of the college is retrived fr9m college.html
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM collegedata WHERE nameofc = %s" ,[nameofc]) #this to select the college
    colleged = cur.fetchone() #fatches all the data stored in database for the college(onlu one )

    return render_template('collegedetail.html', passcolleged=colleged) #the fatched data is passed into collegedetail.html page






@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")




class CollegForm(Form):
    nameofc=StringField("nameofc", [validators.length(min=1,max=50)])
    city= StringField("city", [validators.length(min=1, max=50)])
    location = StringField("location", [validators.length(min=1, max=20)])
    faclity=StringField("faclity",[validators.length(min=1,max=40)])
    lastyearc=StringField("lastyearc",[validators.length(min=1,max=50)])
    yearofest=StringField("yearofc ",[validators.length(min=1,max=50)])
    dept=StringField("dept",[validators.length(min=1,max=100)])

@app.route('/addcollege' ,methods=['GET', 'POST'])
def addcollege():
    form = CollegForm(request.form)
    if request.method == 'POST' and form.validate():
        nameofc = form.nameofc.data
        city = form.city.data
        location = form.location.data
        faclity=form.faclity.data
        lastyearc=form.lastyearc.data
        yearofest=form.yearofest.data
        dept=form.dept.data
        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO collegedata(nameofc, city, location, faclity,lastyearc,yearpofest,dept) VALUES(%s, %s, %s, %s,%s,%s,%s)",
                    (nameofc, city, location, faclity,lastyearc,yearofest,dept))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()


        return redirect(url_for('index'))
    return render_template('addcollege.html', form=form)



if __name__=="__main__":
    app.secret_key="amitrai123"
    app.run(debug=True)