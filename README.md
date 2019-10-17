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
To start the app locally, first pull the the latest changes, then navigate to the project top-level directory (clueless_project) and run the command
```
python .\manage.py runserver
```
This will start the Django server, and now you can navigate to http://127.0.0.1:8000/ in your browser to see the app.
