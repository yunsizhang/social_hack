import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# XXX: The URI should be in the format of: 
#
#     postgresql://zy2232:4ayq7@104.196.175.120/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
DATABASEURI = "postgresql://postgres:kl2912@35.196.40.248/postgres"
# This line creates a database engine that knows how to connect to the URI above
engine = create_engine(DATABASEURI)
@app.before_request

def before_request():
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None



@app.teardown_request

def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass
 
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
@app.route('/')
def index():
  return render_template("index.html")

#sign in
@app.route('/signin',methods=['POST'])
def sign():
  username = request.form['username']
  password = request.form['password']
  t=request.form['name']
  record=g.conn.execute('SELECT username FROM Person WHERE username = %s',username)
  if not record.fetchone():
    return render_template("signinerror.html")
    record.close()
  else:
    record=g.conn.execute('SELECT password FROM Person WHERE username = %s',username)
    p= record.fetchone()
    record.close()
    if p[0] == password:
      if t =='Staff':
        cur=g.conn.execute("select s.* from Staff as s, Person as p  where s.user_id=p.user_id and p.username=%s;",username)
        a=cur.first()
        if a==None:
          return render_template("signinerror.html")
        else:                  
          return redirect('/Staff/%s'%username)
      else:
        cur=g.conn.execute("select a.* from Alumni as a, Person as p  where a.user_id=p.user_id and p.username=%s;",username)
        a=cur.first()
        if a==None:
          return render_template("signinerror.html")
        else:
          return redirect('/Alumni/%s'%username)  
    else: 
      return render_template("signinerror.html")
    
#sign up
@app.route('/signup')
def signup():
  return render_template("signup.html")

#add user
@app.route('/signup/add',methods=['POST'])
def add():
    username = request.form['username']
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    usertype = request.form['usertype']
    
    if username=='' or firstname=='' or lastname=='' or email=='' or password=='':
        return render_template("signupinvalid.html")

    start=str(username[0])
    #username exists
    cursor = g.conn.execute("SELECT username FROM Person;")
    allnames = []
    for result in cursor:
        allnames.append(result[0])  # can also be accessed using result[0]
    cursor.close()

  #username exists end

  #

  #email exists
    cursor1 = g.conn.execute("SELECT email FROM Person;")
    allemails = []
    for result in cursor1: 
        allemails.append(result[0])  # can also be accessed using result[0]

    cursor1.close()

  #email exists end
    if username in allnames or email in allemails:
        return render_template("signuperror.html")
    else:
        #Check username valid
        if str.isdigit(start) or email.count('@')!=1 or len(password)<8:
            return render_template("signupinvalid.html")
        else:        
            #new user_id
            record = g.conn.execute("select max(user_id)+1 from Person")
            uid=record.first()[0]
            #new user_id end
            cmd = 'INSERT INTO Person VALUES (:username1, :uid1, :firstname1, :lastname1, :email1, :password1)';
            g.conn.execute(text(cmd), username1=username,uid1=uid, firstname1=firstname,lastname1=lastname,email1=email, password1=password);
            #g.conn.commit()
            if usertype=='Alumni':
                recorda = g.conn.execute("select max(record_ID)+1 from Alumni")
                aid=recorda.first()[0]
                g.conn.execute("insert into Alumni values (%s, %s);",(uid,aid))
                #g.conn.commit()
            else:
                records = g.conn.execute("select max(staff_ID)+1 from Staff")
                sid=records.first()[0]
                g.conn.execute("insert into Staff values (%s, %s,%s)",(uid,sid,username))
                #g.conn.commit()
            return render_template("sus.html")
         
#staff

@app.route('/Staff/<username>')
def profile_s(username): 
  cursor=g.conn.execute("select user_id from person where username=%s;",username)
  uid=cursor.first()[0]
  cur=g.conn.execute("select m.* from Staff as s, M_O as m where s.staff_ID=m.staff_ID and s.name=%s;",username)
  s=cur.fetchall()
  cur.close()
  cursor.close()
  activities=[]
  alljid=[]
  allname=[]
  for m in s:
  #cursor=g.conn.execute("select p.username from jobseeker as j,person as p where j.jobseeker_id=%s and     #p.user_id=j.user_id;",m[0])
  #n=cursor.first()[0]
  #cursor=g.conn.execute("select title from job_posted where job_id=%s;",m[1])
  #n1=cursor.first()[0]
    activities.append(('Outreach&Meeting',m[0],m[1],m[2],m[3]))
# if m[1] not in alljid:
#   alljid.append(m[1])
# if n not in allname:
 #  allname.append(n)
    
  cursor=g.conn.execute("select * from Friendlist where user_ID=%s;",uid)
  friends=cursor.first()
  if friends==None:
    update_time_f=''
    friendlist=''
  else:
    update_time_f=friends[1]
    friendlist=friends[2].split(',')
  return render_template("staff.html",**locals())

if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)

  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.

    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)





  run()
