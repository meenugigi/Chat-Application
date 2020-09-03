Note: if on downloading this folder, you receive an error, then on the application.py file, edit line 91 (line 91 as on Sublime text) to " return render_template("createchannel.html", channels = existingchannels)"
This will prevent the error on page load. Once the page has loaded successfully, edit it back to what it was previously.

Features implemented:
- Display Name: When a user visits your web application for the first time, they should be prompted to type in a display name that will eventually be associated with every message the user sends. If a user closes the page and returns to your app later, the display name should still be remembered.
- Channel Creation: Any user should be able to create a new channel, so long as its name doesn’t conflict with the name of an existing channel.
- Channel List: Users should be able to see a list of all current channels, and selecting one should allow the user to view the channel. We leave it to you to decide how to display such a list.
- Messages View: Once a channel is selected, the user should see any messages that have already been sent in that channel, up to a maximum of 100 messages. Your app should only store the 100 most recent messages per channel in server-side memory.
- Sending Messages: Once in a channel, users should be able to send text messages to others the channel. When a user sends a message, their display name and the timestamp of the message should be associated with the message. All users in the channel should then see the new message (with display name and timestamp) appear on their channel page. Sending and receiving messages should NOT require reloading the page.
- Remembering the Channel: If a user is on a channel page, closes the web browser window, and goes back to your web application, your application should remember what channel the user was on previously and take the user back to that channel.
- Personal Touch: implemented private chatrooms. Only users having access to chtaroom key will be able to enter private chatrooms.


Explanation of the files contained:

- createchannel.html ---> contains html and Javascript code to allow users to create public channels and chat with other users on public channels. 

- login.html ---> allows users to enter the application by entering a displayname that will be remembered by the application.

- memberchannel.html ---> allows users to create private chatrooms by inputting the room key and supports messaging between users in the private chatroom.

- selectchannel.html ---> allows users to select private chatrooms or public channels and directs them accordingly as per the selections made.

- application.py ---> this is the main python file and to run this flask application type set flask_app=application.py on cmd.

- style.css ---> contains the css stylesheet

- app/main/events.py ---> contains the socket programming code in python to support private chatrooms

- app/main/forms.py --- contains python code for a form that is required to enter the private chatroom. The form contains an input 'room'. This is the chatroom key. Only users entering this key will have access to the private chatrooms.

- app/main/routes.py ---> contains python code for navigating the users to the required pages as per the button clicks (for private chatrooms)

Project Demo Link : https://youtu.be/BPXFfbc0w84
