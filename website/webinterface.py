from flask import Flask, render_template, request, session, redirect, url_for, flash
from os import urandom as rand
import pprint
import ts3

pp = pprint.PrettyPrinter(indent=4)



app = Flask(__name__)
app.secret_key = rand(24)

def teamspeakClientAdd(clientName): 
    with ts3.query.TS3Connection('magic.adam-ant.co.uk', '10011') as ts3conn:
        try:
            ts3conn.login(client_login_name='serveradmin',client_login_password='DE0xWKTx')
        except ts3.query.TS3QueryError as err:
            print(err)
        
        ts3conn.use(sid=1)
        
        try:
            clientdbid = ts3conn.clientdbfind(pattern=clientName)[0]['cldbid']
        except ts3.query.TS3QueryError:
            return False

        try:
            ts3conn.servergroupaddclient(sgid=9,cldbid=clientdbid)
            ts3conn.servergroupaddclient(sgid=10,cldbid=clientdbid)
            ts3conn.servergroupaddclient(sgid=11,cldbid=clientdbid)
            ts3conn.servergroupaddclient(sgid=12,cldbid=clientdbid)
            return True
        except:
            print("ERROR")

def teamspeakClientCheck(clientName):
    with ts3.query.TS3Connection('magic.adam-ant.co.uk', '10011') as ts3conn:
        try:
            ts3conn.login(client_login_name='serveradmin',client_login_password='DE0xWKTx')
        except ts3.query.TS3QueryError as err:
            print(err)
        
        ts3conn.use(sid=1)
        
        try:
            print('before')
            client = ts3conn.clientfind(pattern=clientName)
            print('after')
            clientid = client[0]['clid']
            groups = ts3conn.clientinfo(clid=clientid)[0]['client_servergroups']
        except ts3.query.TS3QueryError as ts3err:
            if ts3err.resp.error['id'] == '512':
                session.pop('username', None)
                flash("ERROR: Username not found. Type it carefully cos Clockwork PLUS! is gonna cost ya...","danger")
                return redirect(url_for('index'))
            return "Ooops! Tell Adam this: <br>" + ts3err.resp.error['msg']
        if "9," in groups:
            print("FeckOffMate!")
            flash("ERROR: You already have Clockwork PLUS, ya dingus","danger")
            session.pop('username', None)
            return redirect(url_for('index'))
        else:
            return redirect(url_for("payment"))
        

@app.route("/")
def index():
    if 'username' in session:
        #No longer in the checkout flow, reset!
        session.pop('username', None)
    return render_template("index.html")

@app.route("/collectsunlight")
def wait():
    if "username" in session:
        return render_template("wait.html")
    else:
        return redirect(url_for("buy"))

@app.route("/pay")
def payment():
    if "username" in session:
        return render_template("payment.html")
    else:
        return redirect(url_for("buy"))

@app.route("/activate")
def activate():
    if "username" in session:
        if teamspeakClientAdd(session['username']):
            session.pop('username', None)
            flash("Success! You have been upgraded to Clockwork PLUS! Enjoy!","success")
            return redirect(url_for('index'))
        else:
            return "Adam fucked up! go nag him"
    else:
        return redirect(url_for("buy"))


@app.route("/buy", methods=['GET', 'POST'])
def buy():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return teamspeakClientCheck(session['username'])
    return render_template("buy.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

