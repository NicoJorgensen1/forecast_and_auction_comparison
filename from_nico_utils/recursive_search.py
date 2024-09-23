import os
import argparse
from typing import List
from natsort import natsorted
from time import perf_counter
from .convert_seconds_to_hr_min_sec import seconds_to_hrs_min_sec


# Recursive search for files with case-insensitive extension matching in a single directory
def recursive_search(directory, extensions, recursive=True) -> List[str]:
    """
    Recursively searches for files with specified extensions in a directory.

    Args:
        directory (str or List[str]): The directory path(s) to search for files.
        extensions (List[str]): The file extensions to match.
        recursive (bool, optional): Whether to search recursively in subdirectories. Defaults to True.

    Returns:
        List[str]: A list of file paths matching the specified extensions.

    Examples:
        >>> recursive_search("/path/to/directory", ["jpg", "png"])
        ['/path/to/directory/file1.jpg', '/path/to/directory/file2.png']
    """
    if isinstance(directory, list):
        if len(directory) > 1:
            raise ValueError("The recursive search function only accepts a single directory path!")
        directory = directory[0]
    matching_files = []

    # Iterate through the directory and its subdirectories if recursive is True
    for entry in os.scandir(directory):
        if entry.is_dir() and recursive:
            matching_files.extend(recursive_search(entry.path, extensions))
        elif entry.is_file() and entry.name.lower().endswith(tuple(extensions)):
            matching_files.append(entry.path)

    return matching_files


# Main function to search files, dynamically choosing the method based on start_path structure
def search_files(
        start_path,
        accepted_img_extensions: List[str] = ("jpg", "jpeg", "png"),
        recursive: bool = True,
        sort_by_basename: bool = False,
        return_unique_basenames_only: bool = False,
        verbose: bool = False,
        sort_files: bool = False,
        **kwargs
) -> List[str]:
    """
    Searches (potentially recursive) for files in the specified directories with the specified file extensions.

    Args:
        start_path (List[str]):                         The directories where files will be searched.
        accepted_img_extensions (List[str], optional):  The accepted image extensions. Defaults to ["jpg", "jpeg", "png"].
        recursive (bool, optional):                     Whether to search recursively in subdirectories. Defaults to True.
        sort_by_basename (bool, optional):              Whether to sort the files by their basenames. Defaults to False.
        return_unique_basenames_only (bool, optional):  Whether to return only unique basenames. Defaults to False.
        verbose (bool, optional):                       Whether to print additional information. Defaults to False.
        sort_files (bool, optional):                    Whether to sort the file paths. Defaults to False.
        **kwargs:                                       Additional keyword arguments.

    Returns:
        List[str]: A list of file paths.

    Raises:
        NotADirectoryError: If the provided path does not exist.

    Notes:
        - If the user does not specify any accepted image extensions, the default extensions ["jpg", "jpeg", "png"] will be used.
        - The start_path argument can be a single directory path or a list of directory paths.
        - The search is case-insensitive for file extensions.
        - If return_unique_basenames_only is True, only the unique basenames of the files will be returned.
        - If sort_files is True, the file paths will be sorted according to the chosen sorting method.
        - If sort_by_basename is True and return_unique_basenames_only is False, the files will be sorted by their basenames.
        - If verbose is True, additional timing information for each individual process will be printed during the search process.
        - If the user specifies sort_by_basename, we will force sort_files to be True.

    Examples:
        >>> search_files("/path/to/directory")
        ['/path/to/directory/file1.jpg', '/path/to/directory/file2.png']
    """

    # If the user has specified sort_by_basename, we will also sort the files
    if sort_by_basename:
        sort_files = True

    # Assure that the paths for where we want to detect files is a list
    if not isinstance(start_path, list):
        start_path = [start_path]

    # Iterating through each of the provided directories where we want to detect files and check if they are actually existing directories
    for path_idx, path_val in enumerate(start_path):
        if not os.path.exists(path_val) and "Image_Datasets" in path_val:
            start_path[path_idx] = f"{os.getenv('IMAGE_DATASETS', 'Image_Datasets')}{path_val.split('Image_Datasets')[-1]}"
        if not os.path.isdir(start_path[path_idx]):
            raise NotADirectoryError(
                f"The path(s) provided has to exist! Now the {path_idx + 1:d}. provided path does NOT exist => {start_path[path_idx]=}")

    # As we are case insensitive, we need to convert the extensions to lowercase
    if not isinstance(accepted_img_extensions, (list, tuple, set)):
        accepted_img_extensions = [accepted_img_extensions]
    accepted_img_extensions = {ext[1:] if ext.startswith(
        ".") else ext for ext in accepted_img_extensions}
    accepted_img_extensions = {ext.lower() for ext in accepted_img_extensions}

    # Perform the search
    t1 = perf_counter()
    filename_list = recursive_search(start_path, accepted_img_extensions, recursive=recursive)
    if verbose:
        print_time_spent(time_spent=perf_counter() - t1,
                         init_print_str='Time to search for files took ')

    # Return only unique basenames if specified
    if return_unique_basenames_only:
        t1 = perf_counter()
        filename_list = list({os.path.basename(x): x for x in filename_list}.values())
        if verbose:
            print_time_spent(time_spent=perf_counter() - t1,
                             init_print_str='Time to retrieve only unique basenames took ')

    # Sort the list of filepaths according to the chosen sorting method
    if sort_files:
        t1 = perf_counter()
        sort_func = os.path.basename if sort_by_basename and not return_unique_basenames_only else str
        filename_list = natsorted(filename_list, key=lambda x: sort_func(x).lower())
        if verbose:
            print_time_spent(time_spent=perf_counter() - t1,
                             init_print_str='Time to sort the file paths took ')

    return filename_list


def print_time_spent(time_spent: float, init_print_str: str):
    time_basenames_spent = seconds_to_hrs_min_sec(seconds=time_spent)
    print(f"{init_print_str}{time_basenames_spent}")


def recursive_case_insensitive_glob(*args, **kwargs):
    """ Wrapper function for backwards compatibility. """
    return search_files(*args, **kwargs)


# Run from CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively search for files in directories and subdirectories and return their file paths.")
    parser.add_argument("--start_path", type=str, required=True,
                        help="The path(s) to start the search from. It can be a single path or a list of paths.")
    parser.add_argument("--accepted_img_extensions", type=str, nargs="+", default=[
        "jpg", "jpeg", "png"], help="A list of accepted file extensions. Defaults to ['jpg', 'jpeg', 'png'].")
    parser.add_argument("--recursive", type=str2bool, default=True,
                        help="If True, search subdirectories recursively. Defaults to True.")
    parser.add_argument("--sort_by_basename", type=str2bool, default=False,
                        help="If True, sort the file paths by their basenames (case-insensitive). Defaults to False.")
    parser.add_argument("--return_unique_basenames_only", type=str2bool, default=False,
                        help="If True, return only the unique basenames of the files. Defaults to False.")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="If True, print out the time spent on each process. Defaults to False.")
    parser.add_argument("--sort_files", type=str2bool, default=False,
                        help="If True, sort the file paths. Defaults to False.")
    args = parser.parse_args()

    # Display the chosen arguments
    print_args(args=args, init_str="This is the options chosen when running a recursive and case insensitive search:",
               ljust_length=30)

    # Run the function and perform the search
    start_time = perf_counter()
    file_list = search_files(**args.__dict__)
    end_time = perf_counter()
    duration_str = seconds_to_hrs_min_sec(seconds=end_time - start_time)
    print(f"Found {len(file_list):d} files in total in {duration_str}")
