import argparse
import sys
sys.dont_write_bytecode = True


# Define a function to convert a string into a boolean value
def str2bool(string: str) -> bool:
    """
    Convert a string into a boolean value.

    Args:
        string (str): The string to be converted.

    Returns:
        bool: The corresponding boolean value.

    Raises:
        argparse.ArgumentTypeError: If the input string is not a valid boolean value.

    Example:
        >>> str_value = "True"
        >>> result = str2bool(str_value)
        >>> print(result)
        True

    Notes:
        - The function converts a string into a boolean value.
        - The string argument should be a valid string representation of a boolean value.
        - The function performs case-insensitive checks to determine the boolean value.
        - Accepted string representations for True: ["yes", "y", "true", "t", "1"].
        - Accepted string representations for False: ["no", "n", "false", "f", "0"].
        - If the input string is already a boolean value, it is returned as is.
        - If the input string is not a valid boolean value, an argparse.ArgumentTypeError is raised.
        - The function is commonly used for parsing command-line arguments where boolean options are expected.
    """
    if isinstance(string, bool):
        return string
    if str(string).lower().strip() in ["yes", "y", "true", "t", "1"]:
        return True
    elif str(string).lower().strip() in ["no", "n", "false", "f", "0", "none"]:
        return False
    else:
        raise argparse.ArgumentTypeError(
            f"Boolean value expected. Input {string} was of {type(string)=}.")
