from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['get_access_control_info'](agent, args)
