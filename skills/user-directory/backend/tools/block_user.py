from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['block_user'](agent, args)
