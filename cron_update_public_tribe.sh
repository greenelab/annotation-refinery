#! /bin/bash

script_directory=`dirname "${BASH_SOURCE[0]}" | xargs realpath`

cd $script_directory
source annotenv/bin/activate

rm -r download_files/

python run_refinery.py --INI_file=main_config.ini
