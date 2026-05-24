from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['manage_user_tags'](agent, args)
