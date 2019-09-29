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
