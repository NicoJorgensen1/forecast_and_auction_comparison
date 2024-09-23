import numbers
import argparse
import numpy as np
from natsort import natsorted
from copy import deepcopy
from typing import Callable, Optional
from .str2bool_func import str2bool


# Define a function capable of printing the arguments from our Namespace object
def print_args(
        args: argparse.Namespace,
        init_str: str = 'This is the input args chosen when running this function',
        ljust_length: Optional[int] = None,
        verbose_func: Callable = print
) -> None:
    """
    Prints the arguments and their corresponding values.

    Args:
        args (argparse.Namespace): The namespace object containing the arguments.
        init_str (str, optional): The initial string to be printed before the arguments. Defaults to 'This is the input args chosen when running this function'.
        ljust_length (int, optional): The length used for left-justifying the argument names. 
        verbose_func (Callable, optional): The function used for printing. Defaults to print.

    Returns:
        None

    Raises:
        None
    """
    # Always use flush==True, if verbose_func==print, to ensure that the output is printed immediately
    kwargs = {"flush": True} if verbose_func == print else {}

    # First copy the namespace as a dictionary and sort it by the keys
    args_dict = deepcopy(args.__dict__)
    args_dict_sorted = {k: args_dict[k]
                        for k in natsorted(args_dict.keys(), key=lambda x: x.lower())}
    if not init_str.endswith(":"):
        init_str += ":"

    # Read the ljust_length from the longest key in the args_dict_sorted, if not provided
    if ljust_length is None:
        try:
            ljust_length = int(np.ceil(np.max([len(k) for k in args_dict_sorted]) / 5) + 5)
        except Exception as ex:
            print(f"Experienced an error when trying to determine the ljust_length:\n{ex}")
            ljust_length = 25

    # Initiate the string to be printed
    string_to_output = f'\n{init_str}'

    # Run through each argument and the corresponding value and print those
    for arg_key, arg_val in args_dict_sorted.items():
        start_of_string_print = f"\n{arg_key}:".ljust(
            ljust_length) + f"of type: {type(arg_val)}".ljust(38)
        if arg_val is None or arg_val == "":
            print_arg_val = "None"
        elif isinstance(arg_val, (list, tuple, set)):
            print_arg_val = format_sequence_argval(arg_val, start_of_string_print)
        else:
            print_arg_val = arg_val
        string_to_output += f"{start_of_string_print}{print_arg_val}"
    string_to_output += "\n"
    verbose_func(string_to_output, **kwargs)


def format_sequence_argval(arg_val, start_of_string_print) -> str:
    """
    Formats the argument value as a string representation of a sequence.

    Args:
        arg_val (list or tuple): The argument value to be formatted.
        start_of_string_print (str): The starting string to be printed before the formatted argument value.

    Returns:
        str: The formatted string representation of the argument value.

    Raises:
        None

    Notes:
        - If the argument value is a list, it will be formatted as [item1, item2, ...].
        - If the argument value is a tuple, it will be formatted as (item1, item2, ...).
        - If the argument value is neither a list nor a tuple, it will be formatted as {item1, item2, ...}.

    Examples:
        >>> format_sequence_argval([3, 1, 2], "Start:")
        '[1,\n 2,\n 3]'
        >>> format_sequence_argval((5, 4, 6), "Start:")
        '(4,\n 5,\n 6)'
    """
    sorted_arg_vals = (
        list(arg_val) if any(
            isinstance(arg_item, numbers.Number)
            for arg_item in arg_val
        ) else sorted(arg_val)
    )
    init_pad_string = " " * len(start_of_string_print)
    bracket_start = '[' if isinstance(arg_val, list) else (
        "(" if isinstance(arg_val, tuple) else "{")
    bracket_end = ']' if isinstance(arg_val, list) else (
        ")" if isinstance(arg_val, tuple) else "}")
    print_arg_val = f"{bracket_start}"
    if len(arg_val) > 0:
        print_arg_val += f"{sorted_arg_vals[0]}"
        for item in sorted_arg_vals[1:-1]:
            print_arg_val += f",\n {init_pad_string}{item}"
        print_arg_val += f",\n{init_pad_string} {sorted_arg_vals[-1]}" if len(
            sorted_arg_vals) > 1 else ''
    print_arg_val += f"{bracket_end}"
    return print_arg_val


# Test from CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print the arguments from a Namespace object')
    parser.add_argument('--str_test_key', type=str, default='str_test_val',
                        help='Testing how the function will print a string value')
    parser.add_argument('--empty_str_test_key', type=str, default="",
                        help='Testing how the function will print an empty string value')
    parser.add_argument('--int_test_key', type=int, default=1,
                        help='Testing how the function will print an integer value')
    parser.add_argument('--float_test_key', type=float, default=2.0,
                        help='Testing how the function will print a float value')
    parser.add_argument('--bool_test_key', type=str2bool, default=True,
                        help='Testing how the function will print a bool value')
    args = parser.parse_args()

    # Edit the input args
    args.list_test_key = [1, 2, 3]
    args.tuple_test_key = (4, 5, 6)
    args.set_test_key = {7, 8, 9}
    args.none_test_key = None

    # Print the arguments
    print_args(args, ljust_length=25,
               init_str="This is the testing input args for when testing this print_args function:")
