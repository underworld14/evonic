from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['list_groups'](agent, args)
