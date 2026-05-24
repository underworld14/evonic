from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['add_user_contact'](agent, args)
