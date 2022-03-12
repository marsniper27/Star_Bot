install python if not installed https://www.python.org/downloads/

run the following command in cmd or powershell to install required packages:

pip install hjson 
pip install pywin32
pip install web3

Open config.hjson in a text editor and update the settings to match your needs.

run Star_Bot.py Bot will run until the set compound time and perform a compound on the Star Pool. Once compound is done a new task will be scheduled and the bot will close. The bot will run again at the scheduled time/date.

First compound will occure at the time set on the day the bot is initially run.

Changes to the config file will take effect either the next time the scheduled task runs or if you run the Star_Bot.py file manually (this will do a ccompound the day it is run and start the scheduling form that day on)

*curently task scheduling is only working on windows. I am working on the Linux/Mac scheduling still