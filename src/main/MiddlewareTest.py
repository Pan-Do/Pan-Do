import time
from pytodoist import todoist
from middleware import TaskManager

print("Starting middleware test")

print("\n========================================")
print("=========  Testing login  ==============")
print("========================================\n")

print("\t- Logging in")

user = todoist.login("malikjp@rose-hulman.edu", "roeshulman")
taskManager = TaskManager('', user)

print("\t- Login successfull")

print("\n========================================")
print("========  Test getting tasks  ==========")
print("========================================\n")

print("\t- Getting tasks")

taskManager.set_project("Personal")
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Tasks: " + repr(tasks))

print("\t- Got tasks")

print("\n========================================")
print("=========  Test adding task  ===========")
print("========================================\n")

print("\t- Adding task \"Middleware test task\"")

taskName = "Middleware test task"

taskManager.add_task(taskName)

print("\t- checking if task added")
time.sleep(2)
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Task added: " + repr(taskName in tasks))

print("\n========================================")
print("=========  Test editing task  ==========")
print("========================================\n")

print("\t- Editing task \"Middleware test task\" to \"Middleware edited task\"")

taskName = "Middleware test task"
editName = "Middleware edited task"

taskManager.update_task([taskName, editName])

print("\t- checking if edited added")
time.sleep(2)
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Old task found: " + repr(taskName in tasks))
print("\t- New task found: " + repr(editName in tasks))

print("\n========================================")
print("========  Test deleting task  ==========")
print("========================================\n")

print("\t- Deleting task \"Middleware edited task\"")

taskName = "Middleware edited task"

taskManager.delete_task(taskName)

print("\t- checking if task added")
time.sleep(2)
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Task deleted: " + repr(taskName not in tasks))

print("\n========================================")
print("=======  Test swapping project  ========")
print("========================================\n")

print("\t- Swapping project to \"Inbox\"")
oldProj = taskManager.get_project()

taskManager.set_project("Inbox")

newProj = taskManager.get_project()

print("\t- Project Swapped: " + repr(oldProj != newProj and newProj == "Inbox"))

print("\n========================================")
print("= Test previous methods in new project =")
print("========================================\n")

print("\n========================================")
print("========  Test getting tasks  ==========")
print("========================================\n")

print("\t- Getting tasks")

taskManager.set_project("Personal")
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Tasks: " + repr(tasks))

print("\t- Got tasks")

print("\n========================================")
print("=========  Test adding task  ===========")
print("========================================\n")

print("\t- Adding task \"Middleware test task\"")

taskName = "Middleware test task"

taskManager.add_task(taskName)

print("\t- checking if task added")
time.sleep(2)
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Task added: " + repr(taskName in tasks))

print("\n========================================")
print("=========  Test editing task  ==========")
print("========================================\n")

print("\t- Editing task \"Middleware test task\" to \"Middleware edited task\"")

taskName = "Middleware test task"
editName = "Middleware edited task"

taskManager.update_task([taskName, editName])

print("\t- checking if edited added")
time.sleep(2)
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Old task found: " + repr(taskName in tasks))
print("\t- New task found: " + repr(editName in tasks))

print("\n========================================")
print("========  Test deleting task  ==========")
print("========================================\n")

print("\t- Deleting task \"Middleware edited task\"")

taskName = "Middleware edited task"

taskManager.delete_task(taskName)

print("\t- checking if task added")
time.sleep(2)
tasks = [t.content for t in taskManager.get_tasks()]
print("\t- Task deleted: " + repr(taskName not in tasks))

