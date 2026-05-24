from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['list_users'](agent, args)
