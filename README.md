# Logbook Submission Automation
Improved the old logbook submission automation using selenium for login, so no need for manual digging for cookies inside the browser everytime you want to submit a logbook entry.

## Script setup
Create a python environment with python 3.9+ (example using conda)
```bash
$ conda create -n browser_automation
```
Activate the environment and install the required libraries
```bash
$ conda activate browser_automation
$ pip install -r requirements.txt
```
Fill your email and password as environment variables and execute the script
```bash
$ cp .env.example .env
$ code .env (fill your credentials)
$ python logbook_submission_automation.py
```
