from pytodoist import todoist
from listeners import Listener
import threading
import time

class TaskManager(object):
    """
        Manages tasks, interacts with the Wrapper class
    """
    def __init__(self, gui, user):
        self.gui = gui
        self.user = user
        self.actionQueue = list()
        self.queueFlag = False
        self.queueWaitTime = 0
        self.queueBatchCount = 1
        self.serverPingCounterLimit = 45
        self.serverPingCounter = 0
        self.setTaskSemaphore = threading.BoundedSemaphore(1)
        self.queueSemaphore = threading.BoundedSemaphore(1)
    
    """
        Starts up the GUI.  Does so by creating the listeners, and then passing them to the GUI.
        Next it tells the GUI what project its on, and send the GUI the tasks.  Finally calls the GUI's
        startGui method.
    """
    def startGui(self):
        self.setup = True

        # using a generic listener that takes in the method to call
        add = Listener(self.add_task)
        delete = Listener(self.delete_task)
        projectSwap = Listener(self.set_project)
        setProjectNames = Listener(self.set_projects)
        forceSync = Listener(self.force_sync)
        edit = Listener(self.edit_task)
        moveTask = Listener(self.move_task)

        self.gui.setAddListener(add)
        self.gui.setRemoveListener(delete)
        self.gui.setProjectSwapListener(projectSwap)
        self.gui.setProjectNamesListener(setProjectNames)
        self.gui.setForceSync(forceSync)
        self.gui.setEditListner(edit)
        self.gui.setTaskMovedListener(moveTask)


        self.set_project("Personal")
        self.gui.setCurrentProject(self.get_project().name)
        self.set_tasks()

        self.gui.startGui()

        self.setup = False

    """
        This is an internal method for adding methods to the queue.  The queue exists to enable control on how fast
        the middleware executes things and pings the server.  Partially invalidated by the existance of the
        serverPingCounter, but still being used because its helpful to be able to meter execution speed.
    """
    def _add_to_queue(self, val, method):
        print('_add_to_queue Method:', method.__name__, 'val:', val)
        ls = [val, method]
        if self.queueFlag:
            self.actionQueue.append(ls)
        else:
            self.actionQueue.append(ls)
            self.queueFlag = True
            syncThread = threading.Timer(self.queueWaitTime, self._queueLoop)
            # print("Start queue thread")
            syncThread.start()

    """
        The main loop that pulls things from the Queue and executes them.  Should be ran inside of a separate thread.
    """
    def _queueLoop(self):
        try:
            self.queueSemaphore.acquire()
            print('_queueLoop start')
            # print('\tqueue: ', [x[1].__name__ for x in self.actionQueue])
            if len(self.actionQueue) > 0:
                # print('\t_queueLoop addQueue > 0')
                i = 0
                while (i < self.queueBatchCount and len(self.actionQueue) > 0):
                    print('\tqueue: ',
                    [x[0] for x in self.actionQueue])
                    ls = self.actionQueue.pop(0)
                    ls[1](ls[0])
                    i = i + 1
                if self.queueFlag:
                    syncThread = threading.Timer(self.queueWaitTime, self._queueLoop)
                    syncThread.start()
            else:
                # print('\tadd_loop addQueue <= 0')
                self.queueFlag = False
                if self.gui:
                    self.set_tasks()
            try:
                self.queueSemaphore.release()
            except:
                # needs to do something, I guess?
                print()
        except:
            self.queueFlag = False
            try:
                self.queueSemaphore.release()
            except:
                # needs to do something, I guess?
                print()
            raise

    """
        increments the counter of times server has been pinged, and then checks
        if it has gone past the limit.  If it has, it sends a message to the GUI
        to notify the user that they need to wait a minute
    """
    def _increment_counter_and_check_for_limit(self, amt):
        print('Number of pings:', self.serverPingCounter)
        if self.serverPingCounter == 0:
            # kick off thread to reset the counter to zero one minute from when you started
            # incrementing the counter
            syncThread = threading.Timer(60, self._reset_counter)
            syncThread.daemon = True
            syncThread.start()
        self.serverPingCounter = self.serverPingCounter + amt
        if self.serverPingCounter > self.serverPingCounterLimit:
            # Tell the Gui to wait, and halt the queue.  display error is the current fix, but if gui had a
            # please_wait method, that would be called.
            # gui.please_wait()
            self.gui.displayError("PLEASE WAIT")
            self.queueSemaphore.acquire()
            print('test')

    """
        resets the serverPingCounter to zero, and frees the queue
    """
    def _reset_counter(self):
        self.serverPingCounter = 0
        try:
            # let the queue continue, and tlel the gui to stop waiting.  display error is a placeholder, should instead call
            # gui.stop_waiting() to let the gui know to allow more inputs
            self.queueSemaphore.release()
            self.gui.displayError("OK STOP WAITING")
            # gui.stop_waiting()
        except:
            # needs to do something, I guess?
            print()
            
        
    # pings server once
    """
        Gets the projects from the pytodoist user object, and returns them
    """
    def get_projects(self):
        self._increment_counter_and_check_for_limit(1)
        try:
            return self.user.get_projects()
        except:
            self.gui.displayError("S500 ERROR: Error getting the projects")
            raise

    # calls _find_project which pings server
    """
        Finds the project it is trying to be set to, and sends the tasks to the gui
        it then adds the change of project to the queue, so that things can still execute in order
        but the gui doesn't have to wait on the queue
    """
    def set_project(self, projects_to):
        self._increment_counter_and_check_for_limit(1)
        try:
            project = self._find_project(projects_to[0])
            self.set_tasks_from_project(project)
            if not self.setup:
                self._add_to_queue(project, self._set_project_helper)
            else:
                self._set_project_helper(project)
        except:
            self.gui.displayError("S500 ERROR: Error setting the project")
            raise

    """
        helper method that is sent to the queue to call after a set_project is called
    """
    def _set_project_helper(self, project_to):
        self.project = project_to
        
    # pings server once
    """
        helper method to locate and return a project from the list of projects
    """
    def _find_project(self, project_to):
        self._increment_counter_and_check_for_limit(1)
        found = False
        projects = self.get_projects()
        for p in projects:
            if p.name == project_to:
                project = p
                found = True
                break
        if not found:
            project = projects[0]
        return project

    # pings server twice
    """
        adding a new project and syncing it to the server
    """
    def add_project(self, project_to_add):
        self._increment_counter_and_check_for_limit(2)
        try:
            return self.user.add_project(project_to_add)
        except:
            self.gui.displayError("S500 ERROR: Error adding a project")
            raise

    """
        returns the current project held by middleware
    """
    def get_project(self):
        try:
            return self.project
        except:
            self.gui.displayError("M001 ERROR: Error getting the project")
            raise

    # pings server once
    """
        gets the list of tasks from a given project and sorts it by the task.item_order value, and then returns that
        sorted list
    """
    def get_tasks(self, project):
        self._increment_counter_and_check_for_limit(1)
        try:
            tasks = project.get_tasks()
            # print('get_tasks',[t.item_order for t in tasks])
            # print('get_tasks',[t.content for t in tasks])
            return sorted(tasks, key=lambda task: task.item_order)
        except:
            self.gui.displayError("M001 ERROR: Error getting the tasks")
            raise

    # calls get tasks which pings server once
    """
        hands the tasks of the current project to the gui
    """
    def set_tasks(self):
        self.setTaskSemaphore.acquire()
        try:
            tasks = self.get_tasks(self.get_project())
            # print([t.item_order for t in tasks])
            # print([t.content for t in tasks])
            self.gui.addListOfTasks([t.content for t in tasks])
            self.setTaskSemaphore.release()
        except:
            self.gui.displayError("G001 ERROR: Error setting the tasks")
            self.setTaskSemaphore.release()
            raise

    # calls get tasks which pings server once
    """
        hands the tasks of the given project to the gui
    """
    def set_tasks_from_project(self, project):
        self.setTaskSemaphore.acquire()
        try:
            tasks = self.get_tasks(project)
            # print([t.item_order for t in tasks])
            # print([t.content for t in tasks])
            self.gui.addListOfTasks([t.content for t in tasks])
            self.setTaskSemaphore.release()
        except:
            self.gui.displayError("G001 ERROR: Error setting the tasks")
            self.setTaskSemaphore.release()
            raise
        

    # takes in a list of task descriptions [old, new] to update old to new
    """
        adds the _edit_task_helper method to the queue
    """
    def edit_task(self, info):
        self._add_to_queue(info, self._edit_task_helper)

    # pings server twice, calls get_tasks and t.update()
    """
        Edits the task with given text into the new text
    """
    def _edit_task_helper(self, info):
        try:
            old = info[0]
            new = info[1]
            tasks = self.get_tasks(self.get_project())
            for t in tasks:
                if t.content == old:
                    t.content = new
                    t.update()
        except:
            self.gui.displayError("S500 ERROR: Error editing the task")
            raise

    # pings server once, calls get_projects()
    """
        passes off the user's project list to the gui
    """
    def set_projects(self, val):
        self._increment_counter_and_check_for_limit(1)
        self.gui.setProjectNames([p.name for p in self.get_projects()])

    # pings server n times where n is the number of tasks
    # takes in a list of task descriptions to add
    """
        adds to the queue an _add_task_helper for every task in the array passed in
    """
    def add_task(self, task_contents):
        for task_content in task_contents:
            self._add_to_queue(task_content, self._add_task_helper)

    # pings server once
    """
        adds the task to the current project
    """
    def _add_task_helper(self, task_content):
        self._increment_counter_and_check_for_limit(1)
        try:
            self.get_project().add_task(task_content)
            
        except:
            self.gui.displayError("S500 ERROR: Error adding the task")
            raise

    """
        takes in an array [original location, new location], and adds to the queue the _move_task_helper
    """
    def move_task(self, val):
        self._add_to_queue(val, self._move_task_helper)

    # pings server n times where n is the number of tasks, calls _update_task_helper
    """
        swaps locations of tasks so that it moves the task at the first location to the second location
    """
    def _move_task_helper(self, task_locs):
        start_loc = task_locs[0]
        end_loc = task_locs[1]
        tasks = self.get_tasks(self.get_project())

        # print('MOVING', start_loc, 'TO', end_loc)

        # print('_move_task_helper before tasks:', [t.content for t in tasks])
        # print('_move_task_helper before order:', [t.item_order for t in tasks])

        if(start_loc < end_loc):
            for i in range(start_loc, end_loc, 1):
                # print('swap(',i + 1, i, ')')
                temp = tasks[i + 1].item_order
                tasks[i + 1].item_order = tasks[i].item_order
                tasks[i].item_order = temp
        elif(start_loc > end_loc):
            for i in range(start_loc, end_loc, -1):
                # print('swap(',i, i - 1, ')')
                temp = tasks[i].item_order
                tasks[i].item_order = tasks[i - 1].item_order
                tasks[i - 1].item_order = temp

        # print('_move_task_helper after tasks:', [t.content for t in tasks])
        # print('_move_task_helper after order:', [t.item_order for t in tasks])

        # adds to the queue the task update
        for t in tasks:
            self._add_to_queue(t, self._update_task_helper)
            
    # pings server once
    """
        calls update on the given task
    """
    def _update_task_helper(self, task):
        self._increment_counter_and_check_for_limit(1)
        try:
            task.update()
        except:
            self.gui.displayError("S500 ERROR: Error updating a task")
            raise


    # pings server 2*n where n is number of tasks to delete by calling _delete_task_helper
    # takes in a list of task descriptions to delete
    """
        adds to the queue the delete task helper for each task in to the method
    """
    def delete_task(self, descriptions):
        for description in descriptions:
            self._add_to_queue(description, self._delete_task_helper)

    # pings server twice
    """
        removes the tasks from the current project
    """
    def _delete_task_helper(self, description):
        # print("deleting:", description)
        self._increment_counter_and_check_for_limit(2)
        try:
            for t in self.get_tasks(self.get_project()):
                if description == t.content:
                    task = t
            task.delete()
        except:
            self.gui.displayError("S500 ERROR: Error deleting the task")
            raise


    # def complete_task(self, description):
    #     try:
    #         for t in self.get_tasks():
    #             if description == t.content:
    #                 task = t
    #         task.complete()
    #     except:
    #         self.gui.displayError("S500 ERROR: Error completing the task")

    # pings server 4 times
    """
        resets everything and gets all the info from the server.  This is a syncronous method that happens immediatly,
        regardelss of what is in the queue
    """
    def force_sync(self, val):
        self._increment_counter_and_check_for_limit(4)
        try:
            self.user = todoist.login(self.user.email, self.user.password)
            self.project = self.user.get_project(self.project.name)
            self.set_projects(val)
            self.set_tasks()
        except:
            self.gui.displayError("S500 ERROR: Error syncing")