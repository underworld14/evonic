from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['merge_users'](agent, args)
