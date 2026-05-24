from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['create_group'](agent, args)
