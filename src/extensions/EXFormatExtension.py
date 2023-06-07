from traceback import format_exception

from colorama import Fore


def ex_format(ex, func_name):
    """_summary_

    Args:
        ex (_type_): _description_
        func_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    exception = "".join(format_exception(ex, ex, ex.__traceback__))
    exception = f"{Fore.RED + '-'*20}ex in {func_name}{'-'*20 + Fore.RESET}\n{exception}\n"
    return exception
