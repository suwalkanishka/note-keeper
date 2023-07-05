# Notekeeper
#### Video Demo: https://youtu.be/DU2TMO_Kl5Q
#### Description:
Notekeeper is a simple markdown notes app built using Python Flask, SQL, and HTML/CSS/JS. The main text editor is an implementation of the SimpleMDE library found [here](https://simplemde.com/). The main features of the app are described below.

###### 1. Register
The user starts by registering for the app. This is almost identical to the register code from week 9, but with the addition of a security question to allow users to change their passwords later on.

###### 2. Login
The user can now Log in to get to the home page. The logic here is identical to week 9.

###### 3. Notes Home
The home page is divided into two vertical columns.

The left column is a sidebar that lets the user create or switch between notes, or logout. This sidebar collapses inside a menu button when the screen is too small.

The right column shows the title of the active note along with Save, Edit and Delete buttons, and the main text editor from SimpleMDE. Here, users can type notes in markdown syntax and it will get partly formatted in real time. To fully render the markdown, users can click the preview button, which allows for a better view of the content. The preview mode is especially important for code, tables and images.

Whenever a new user registers for the app, a Sample Note is automatically created to avoid showing an empty home page. The Delete button prompts a confirmation for users to delete a note. If there is only one note, users are not allowed to delete, and are instead prompted to rename the existing note. This is also done to avoid having an empty home page.

The Edit button creates a pop-up for a new title. Special characters other than spacebar and hyphen are disabled and repetition of titles is not allowed. The user input is validated on the back-end to make sure any front-end manipulation does not cause issues.

Each button click triggers a POST request to the server. However, I did not want the whole page to reload everytime a button was pressed, as that could get frustrating to use. So I set up multiple AJAX requests to allow the front-end to communicate with the Flask backend while only partially updating the content in the browser. This allows for a seamless experience to the user. Implementing this properly was the trickiest part of the code since this was not covered in the lectures.

###### 4. Forgot Password
Here, I've again used an AJAX request to first verify the username and then present the appropriate security question to the user. All information is, again, verified on the back-end to ensure any front-end manipulation doesn't cause errors.

###### 5. UI Notes
1. I used the Bootstrap framework for the UI, along with several custom styling options.
2. The two columns in the home page scroll independently to allow for easier navigation when the list of notes or a note itself is very large.
3. I used Lottie animations in most of the pages to make them feel more lively.


#### That's all!