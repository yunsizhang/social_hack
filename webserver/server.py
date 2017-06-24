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
DATABASEURI = "postgresql://postgres:kl2912@35.185.17.247/postgres"
# This line creates a database engine that knows how to connect to the URI above
engine = create_engine(DATABASEURI)
@app.before_request

def before_request():
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
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

    print "running on %s:%d" % (HOST, PORT)

    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)





  run()
