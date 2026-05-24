from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['manage_user_groups'](agent, args)
