import os
import sys
import argparse

from download_files import download_all_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Package to download and process knowledge in annotations '
        'databases and convert to JSON.')

    parser.add_argument(
        '-i', '--INI_file', required=True, dest='ini_path',
        help='INI config file with locations of desired files.')

    parser.add_argument(
        '-d', '--download_folder', required=True, dest='download_folder',
        help='Folder where all annotations files will be downloaded to '
        '(absolute or relative path).')

    args = parser.parse_args()
    download_all_files(args)
