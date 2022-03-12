import datetime
import win32com.client
import hjson
import sys
import os

locate_python = sys.exec_prefix
print(locate_python)

with open('config.hjson', 'r') as f:
    config = hjson.load(f)

daysToCompound = config["daysToCompound"]

location = os.path.dirname(os.path.abspath(__file__))

def createSchedule():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    task_def = scheduler.NewTask(0)

    # Create trigger
    start_time = datetime.datetime.now() + datetime.timedelta(days=daysToCompound)
    TASK_TRIGGER_TIME = 2
    trigger = task_def.Triggers.Create(TASK_TRIGGER_TIME)
    trigger.StartBoundary = start_time.isoformat()
    trigger.DaysInterval = daysToCompound

    # Create action
    TASK_ACTION_EXEC = 0
    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.ID = 'DO NOTHING'
    action.Path = locate_python+'\python.exe'
    action.Arguments = "Star_Bot.py"
    action.WorkingDirectory = location

    # Set parameters
    task_def.RegistrationInfo.Description = 'Compound Star'
    task_def.Settings.Enabled = True
    task_def.Settings.StopIfGoingOnBatteries = False

    # Register task
    # If task already exists, it will be updated
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_NONE = 0
    root_folder.RegisterTaskDefinition(
        'Compound Star',  # Task name
        task_def,
        TASK_CREATE_OR_UPDATE,
        '',  # No user
        '',  # No password
        TASK_LOGON_NONE)

    print('task created')

    
if __name__ == "__main__":
    createSchedule()
