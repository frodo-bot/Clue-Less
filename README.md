# Clue-Less
## Git Workflow
#### Initial
- [ ] git clone https://github.com/frodo-bot/Clue-Less.git
- [ ] git checkout origin/development
- [ ] git pull development
#### Feature Branch Workflow
- [ ] git checkout -b <feature_branch_name>
- [ ] Do work
- [ ] git commit -am "MEANING COMMIT MESSAGE"
#### Before Submitting Pull Request
- [ ] git rebase origin/development
- [ ] Meaningful Commit Message
- [ ] git push -u origin <feature_branch_name>
#### Submitting Pull Request
After pushing the branch go to the online UI. There should be a 
"Your recently pushed branches:"
- [ ] Click Compare & pull request
- [ ] Set PR to merge feature branch to development branch


## Setting up environment and installing Django
To start, you'll need some kind of virtual envrionment. I use Anaconda for this, because it comes with Python out of the box, as well as a tool for managing virtual environments. The steps to set this up are:
- [ ] Download Anaconda installer from https://www.anaconda.com/distribution/. Select your operating system, and then download the Python 3.7 version. 
- [ ] Open the installer once it downloads, go through the usuall application install process. In general, the default settings for everything should be fine.
- [ ] Once it's installed, search your computer for the "Anaconda Prompt". This is like a terminal for Anaconda. 
- [ ] Type the following command to create an Anaconda envrionment (this creates an environment with the name "software_eng", but you can replace this with any name that you want):
```
conda create --name software_eng python=3.7.4
```
- [ ] Activate your Anaconda envrionment with the following command (replace software_eng with the name of your environment if you chose a different one in the step above):
```
conda activate software_eng
```
- [ ] Install Django with the following command:
```
conda install django
```
- [ ] Install Django Channels with the following command (Anaconda doesn't come with channels, so we have to use pip. Make sure to do this with your envrionment activated):
```
pip install channels
```

Next, you'll need to install Docker desktop. This is the easiest way to install and run Redis, which is a queuing system that Django channels uses to queue messages. 
- [ ] Go to the Docker website and sign in: https://hub.docker.com/ (the login info is the same as was used for all of the other accounts, and the Docker ID is "fellowshipoftheswe")
- [ ] Once signed in, click "get started with Docker Desktop".
- [ ] Download and install Docker
- [ ] Once it's installed, try to run it (no GUI will come up, but I got a system message saying that Docker Desktop is running)

Now, anytime you want to be running/testing the application Redis will need to be running. You can do this by opening a terminal and entering the following command:
```
docker run -p 6379:6379 -d redis:2.8
```
Once Redis is running you should be able to run the app. To do this, first pull the the latest changes, then navigate to the project top-level directory (clueless_project) and run the command
```
python .\manage.py runserver
```
This will start the Django server, and now you can navigate to http://127.0.0.1:8000/ in your browser to see the app.
