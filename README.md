# mmo-bot

## Installation
### Windows
1. Make sure python3 is installed
2. Open the Windows command prompt, navigate to the directory where you want the project work to be done
3. Run the command `git clone https://github.com/yehric2018/mmo-bot.git`: this clones the repository
4. Run the command `cd mmo-bot`: this changes your current directory to the newly cloned repository
5. Run the command `python -m venv env`: this creates a Python virtual environment
6. Run the command `env\Scripts\activate.bat`: this activates the newly created Python virtual environment
7. Run the command `pip install -r requirements.txt`: This installs all the dependencies needed for the project.

## Setup
1. Create a file called `.env` that contains the following contents (you can request for these from yehric2018):
```
DISCORD_TOKEN={}
DISCORD_GUILD={}

MYSQL_USERNAME={}
MYSQL_PASSWORD={}
MYSQL_HOSTNAME={}
MYSQL_DATABASE_NAME={}
```
2. Add the following line to your ~/.bashrc:
```
export PYTHONPATH='C:\\Users\\[path to your project]\\src
```
This will allow your imports across the project to work.

On Linux or Mac, you might need to use forward slashes instead.

Once this line is added, save the file and run `source `/.bashrc`.