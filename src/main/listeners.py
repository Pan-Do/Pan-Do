class NullListener(object):
    def __init__(self, func):
        func(0)
        return

    def notify(self, val):
        return

class AddListener(object):

    def __init__(self, middleware):
        self.middleware = middleware

    def notify(self, val):
        self.middleware.add_task(val)
        self.middleware.set_tasks()

class DeleteListener(object):
    def __init__(self, middleware):
        self.middleware = middleware

    def notify(self, val):
        self.middleware.delete_task(val)
        self.middleware.set_tasks()

class LoginListener(object):
    def __init__(self, func):
        self.function = func

    def notify(self, val):
        # print("in notify: Login Listener" + str(val))
        self.function(val)
    
class ProjectSwapListener(object):
    def __init__(self, middleware):
        self.middleware = middleware
    
    def notify(self, val):
        self.middleware.set_project(val)
        self.middleware.set_tasks()

class GetProjectsListener(object):
    def __init__(self, middleware):
        self.middleware = middleware
    
    def notify(self, val):
        self.middleware.set_projects()

class ForceSyncListener(object):
    def __init__(self, middleware):
        self.middleware = middleware
    
    def notify(self, val):
        self.middleware.force_sync()

class UpdateListener(object):
    def __init__(self, middleware):
        self.middleware = middleware
    
    def notify(self, val):
        self.middleware.update_task(val[0], val[1])

class Listener(object):
    def __init__(self, func):
        self.func = func
    
    def notify(self, val):
        self.func(val)
