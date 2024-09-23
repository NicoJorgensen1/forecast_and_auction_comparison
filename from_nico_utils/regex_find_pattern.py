from datetime import datetime
from typing import Union, Dict, Tuple
import re 

def regex_find_pattern(
        inp_string: str,
        pattern: str,
        get_first: bool = False,
        ignore_case: bool = True
) -> Union[str, None]:
    """
    Find a pattern in a string using regex
    """
    if isinstance(pattern, str):
        re.compile(pattern=pattern, flags=re.IGNORECASE if ignore_case else 0)
    match = re.findall(pattern, inp_string)
    return match[0 if get_first else -1] if match else None


def date_formats2pattern() -> Dict[str, str]:
    """Create a dictionary mapping date format strings to regex patterns.

    This function provides a convenient way to retrieve regex patterns that correspond 
    to various common date formats, facilitating date validation and parsing.

    Returns:
        Dict[str, str]: A dictionary where keys are date format strings and values are 
        their associated regex patterns.
    """
    return {
        "%Y%m%d_%H%M%S": r"\d{4}\d{2}\d{2}_\d{2}\d{2}\d{2}",
        "%Y%m%dT%H%M%S": r"\d{4}\d{2}\d{2}T\d{2}\d{2}\d{2}",
        "%Y-%m-%dT%H:%M:%S": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        "%Y_%m_%d_%H_%M_%S": r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}",
        "%Y-%m-%d %H %M %S": r"\d{4}-\d{2}-\d{2} \d{2} \d{2} \d{2}",
        "%d%m%y_%H%M%S": r"\d{2}\d{2}\d{2}_\d{2}\d{2}\d{2}",
        "%H%M_%d%b%Y": r"\d{2}\d{2}_\d{2}[A-Za-z]{3}\d{4}",
        "%H%M%S_%d%b%Y": r"\d{2}\d{2}\d{2}_\d{2}[A-Za-z]{3}\d{4}",
        "%Y-%m-%d %H_%M_%S": r"\d{4}-\d{2}-\d{2} \d{2}_\d{2}_\d{2}",
        "%d.%m.%Y": r"\d{2}\.\d{2}\.\d{4}",

    }


def datetime_from_string(
        inp_string: str,
        date_formats: Dict = date_formats2pattern()
) -> Tuple[datetime, str]:
    """Extract a datetime object and the remaining string from an input string.

    This function searches the input string for a date that matches any of the provided 
    formats, returning the first found datetime and the string with the date removed.

    Args:
        inp_string (str): The input string containing a date.
        date_formats (dict, optional): A dictionary of date formats and their regex patterns. 
                                       Defaults to the output of date_formats2pattern().

    Returns:
        tuple: A tuple containing the extracted datetime object and the remaining string 
               after the date has been removed.
    """
    string_wo_time = inp_string
    for start_date_format, start_date_pattern in date_formats.items():
        start_time = regex_find_pattern(inp_string=inp_string, pattern=start_date_pattern, get_first=True)
        if start_time:
            string_wo_time = inp_string.replace(start_time, "")
            start_time = datetime.strptime(start_time, start_date_format)
            break
    return start_time, string_wo_time
