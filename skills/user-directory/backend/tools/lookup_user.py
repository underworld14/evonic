from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['lookup_user'](agent, args)
