from traceback import format_exception
import datetime
import os

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
    file_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', '..', 'exceptions'
    )
    file_path = os.path.join(file_dir, "errors_from_ex_format.txt")
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a") as file:
        file.write(formatted_datetime + '\n' + exception + '\n\n')
    return exception
