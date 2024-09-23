import numpy as np
import argparse
import sys
sys.dont_write_bytecode = True                      # Dont create the __pycache__ folder


# A function to convert a amount of seconds into a time string with proper formatted days:hrs:min:sec
def seconds_to_hrs_min_sec(seconds: int, sec_precision: int = None) -> str:
    """
    Converts a given duration in seconds to a formatted string representing hours, minutes, and seconds.

    Args:
        seconds (float):            The duration in seconds.
        sec_precision (int):        The precision for displaying the seconds. Defaults to None.

    Returns:
        str:                        A formatted string representing the duration in hours, minutes, and seconds.

    Example:
        duration = 3665.75
        time_str = secondsToHrsMinSec(duration, sec_precision=2)
        print(time_str)
        >>> Output: "1hr:1min:5.75sec"

    """

    # Change the sec_precision according to the number of seconds, if the precision isn't chosen by the user
    if sec_precision is None:
        sec_precision = 2 if seconds < 20 else 0

    # Compute the number of days, hrs, minutes, seconds are present in this amount of seconds
    days = np.floor(seconds/(3600*24))
    hrs = np.floor((seconds-days*3600*24)/3600)
    mins = np.floor((seconds-days*3600*24-hrs*3600)/60)
    secs = np.mod(seconds, 60)

    # Convert the time periods into strings
    days_string = "{:.0f}days:".format(days) if days > 0 else ""
    hrs_string = "{:.0f}hr:".format(hrs) if (days > 0 or hrs > 0) else ""
    mins_string = "{:.0f}min:".format(mins) if (days > 0 or hrs > 0 or mins > 0) else ""
    secs_string = "{:.{sec_precision}f}sec".format(secs, sec_precision=sec_precision)

    # Concatenate the string parts into one time_string and return that
    time_string = days_string+hrs_string+mins_string+secs_string
    return time_string


def secondsToHrsMinSec(*args, **kwargs):
    return seconds_to_hrs_min_sec(*args, **kwargs)


# Test from CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--secs", type=int, default=1800, help="The number of seconds passed")
    parser.add_argument("--sec_precision", type=int, default=1,
                        help="The precision we want for our timing string. Default: 1")
    FLAGS = parser.parse_args()

    # Run the function
    time_string = seconds_to_hrs_min_sec(seconds=FLAGS.secs, sec_precision=FLAGS.sec_precision)
    print(f"We had an input of {FLAGS.secs} secons, which we want to convert to a time_string with a second precision of {FLAGS.sec_precision}.\nThis gives: {time_string}")
