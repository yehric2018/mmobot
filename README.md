# mmo-bot

## Dependencies
- Make sure python3.10 is installed, as well as python3.10-venv

## Installation
### Linux
1. Open the Linux command prompt, navigate to the directory where you want the project work to be done
2. Run the command `git clone https://github.com/yehric2018/mmo-bot.git`: this clones the repository
3. Run the command `cd mmobot`: this changes your current directory to the newly cloned repository
4. Run the command `python3 -m venv env`: this creates a Python virtual environment
5. Run the command `source env/bin/activate`: this activates the newly created Python virtual environment
6. Run the command `pip install -r requirements.txt`: This installs all the dependencies needed for the project.

### Windows
1. Open the Windows command prompt, navigate to the directory where you want the project work to be done
2. Run the command `git clone https://github.com/yehric2018/mmo-bot.git`: this clones the repository
3. Run the command `cd mmobot`: this changes your current directory to the newly cloned repository
4. Run the command `python -m venv env`: this creates a Python virtual environment
5. Run the command `env\Scripts\activate.bat`: this activates the newly created Python virtual environment
6. Run the command `pip install -r requirements.txt`: This installs all the dependencies needed for the project.

## Setup
1. Create a file called `.env` that contains the following contents (you can request for these from yehric2018):
```
DISCORD_TOKEN={}
DISCORD_GUILD={}

PROJECT_PATH={path to project folder}

MYSQL_USERNAME={}
MYSQL_PASSWORD={}
MYSQL_HOSTNAME={}
MYSQL_DATABASE_NAME={}
MYSQL_TEST_DATABASE_NAME={}
```
2. Add the following line to your ~/.bashrc:
```
export PYTHONPATH='C:\\Users\\[path to your project]\\src'
```
This will allow your imports across the project to work.

On Linux or Mac, you might need to use forward slashes instead.
```
export PYTHONPATH='/home/user/mmobot/src'
```

Once this line is added, save the file and run `source `/.bashrc`.
