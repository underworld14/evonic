from ._core import HANDLERS


def execute(agent, args):
    return HANDLERS['get_user_summary'](agent, args)
