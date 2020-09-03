import os
from collections import deque
from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
#from app import create_app, socketio
from flask import Blueprint
main = Blueprint('main', __name__)
from flask import session, redirect, url_for, render_template, request
from flask_wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required
from flask import session
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
socketio = SocketIO(app)

existingusers = []
existingchannels = []
existingmemberchannels = []
channelsMessages = dict()
roomMessages = dict()
existingrooms = []


#login form for private channels
class LoginForm(Form):
    """Accepts a nickname and a room."""
   # name = StringField('Name', validators=[Required()])
    room = StringField('Room', validators=[Required()])
    submit = SubmitField('Enter Chatroom')

#navigates to private chatroom
@app.route("/chatroom", methods = ["POST"])
def chatroom():
	form = LoginForm()
	return render_template('memberchannel.html', form=form)

#begin chatting on private channels
@app.route('/memberchannel', methods=['GET', 'POST'])
def memberchannel():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = session['displayname']
        session['room'] = form.room.data
        return redirect(url_for('.memberchannel'))
    elif request.method == 'GET':
       # form.name.data = session['displayname']
        form.room.data = session.get('room', '')
        room = form.room.data
        existingrooms.append(room)
        loggedinuser = session['displayname']
        roomMessages[room] = deque()
    return render_template('memberchannel.html', form=form, room = room, rooms=existingrooms, loggedinuser=loggedinuser)

#on joining private chatroom
@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session['displayname'] + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', { 'msg': session['displayname'] + ': ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session['displayname'] + ' has left the room.'}, room=room)

#default route
@app.route("/")
def default():
	if session.get("displayname") is None:
		return render_template("login.html")
	loggedinuser = session['displayname']
	channelname = session['current_channel']
	return render_template("createchannel.html", channels = existingchannels, channellist = channelname, loggedinuser = loggedinuser, messages = channelsMessages[channelname])
#, channellist = channelname, loggedinuser = loggedinuser, messages = channelsMessages[channelname]

#for logging in with displayname
@app.route("/login", methods = ["GET" , "POST"])
def login():
	return render_template("login.html")	
	

#choose between private or public channels
@app.route("/selectchannel", methods = ["POST"])
def selectchannel():
	displayname = request.form.get("displayname")
	session['displayname'] = displayname
	existingusers.append(displayname)
	loggedinuser = session['displayname']
	session.permanent = True
	return render_template("selectchannel.html", loggedinuser = loggedinuser)
	if session.get("displayname") is None:
		return render_template("login.html")
	return render_template("selectchannel.html", loggedinuser = loggedinuser)	


@app.route("/registered" , methods = ["GET" , "POST"])
def registered():
	displayname = session['displayname']
	if request.method == "POST":	
		session['displayname'] = displayname
		existingusers.append(displayname)
		session.permanent = True
		return render_template("createchannel.html", channels = existingchannels)
	return render_template("createchannel.html", channels = existingchannels)

#create public channels
@app.route("/createchannel" , methods = ["GET" , "POST"])
def createchannel():
	createdchannel = request.form.get("channelname")
	if request.method == "POST":		
		if createdchannel in existingchannels:
			showmessages = 'Oops! This channel name already exist!'
			loggedinuser = session['displayname']
			channelname = session['current_channel']
			return render_template("createchannel.html",showmessages = showmessages, channels = existingchannels, channellist = channelname, loggedinuser = loggedinuser, messages = channelsMessages[channelname])
	
	existingchannels.append(createdchannel)
	channelsMessages[createdchannel] = deque()
	session.permanent = True
	loggedinuser = session['displayname']
	channelname = request.form.get("channelname")
	return render_template("createchannel.html",channels = existingchannels, loggedinuser = loggedinuser, channellist = channelname)

#logout from application
@app.route("/logout", methods = ["GET" , "POST"])
def logout():
	try:
		existingusers.remove(session['displayname'])
	except ValueError:
		pass
		session.clear()
	return render_template("login.html")

#enter a public channel
@app.route("/<channelname>", methods = ["GET" , "POST"])
def insidechannel(channelname):
	session['current_channel'] = channelname
	loggedinuser = session['displayname']
	chat = request.form.get("comment")
	#channelsMessages.append(chat)
	return render_template("createchannel.html", channels = existingchannels, channellist = channelname, loggedinuser = loggedinuser, messages = channelsMessages[channelname])


@socketio.on("enter", namespace='/')
def enter():
    """ Send message to announce that user has entered the channel """    
    # Save current channel to join room.
    room = session.get('current_channel')
    join_room(room)   
    emit('status', {
        'userJoined': session.get('displayname'),
        'channelname': room,
        'msg': session.get('displayname') + ' has entered the channel'}, 
        room=room)


@socketio.on("leave", namespace='/')
def leave():
    """ Send message to announce that user has left the channel """
    room = session.get('current_channel')
    leave_room(room)
    emit('status', {
        'msg': session.get('displayname') + ' has left the channel'}, 
        room=room)


@socketio.on('send message')
def send_msg(msg, timestamp):
    """ Receive message with timestamp and broadcast on the channel """
    # Broadcast only to users on the same channel.
    room = session.get('current_channel')
    # Save 100 messages and pass them when a user joins a specific channel.
    if len(channelsMessages[room]) > 100:
        # Pop the oldest message
        channelsMessages[room].popleft()
    channelsMessages[room].append([timestamp, session.get('displayname'), msg])
    emit('announce message', {
        'user': session.get('displayname'),
        'timestamp': timestamp,
        'msg': msg}, 
        room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)
