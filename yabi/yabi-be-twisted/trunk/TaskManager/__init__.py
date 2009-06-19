
import TaskManager

Tasks = TaskManager.TaskManager()

def startup():
    """Start up the TaskManager, so it can go and get some jobs..."""
    print "Starting TaskManager..."
    Tasks.start()