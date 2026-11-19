

from pathlib import Path
import runpy
import shutil
import os.path
import argparse


def main():
    def check_delete(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=str, help='dest dir', required=True)  # NOQA
    args = parser.parse_args()

    output_dir = args.output

    final_od = None

    if (output_dir is not None or output_dir != ''):
        final_od = Path(output_dir)
        if not final_od.exists():
            print(f'error output dir does not exists. {output_dir}')
            return
    else:
        print('No output dir given')
        return

    # delete old outputs
    shutil.rmtree('parks', ignore_errors=True)
    shutil.rmtree('summits', ignore_errors=True)
    check_delete('merged_search_data.json')

    # delete any temp search data files
    check_delete('full_data.json')
    check_delete('search_data.json')
    check_delete('summit_search_data.json')

    # Runs target_script.py as if executed directly from the command line
    runpy.run_path("main.py", run_name="__main__")
    runpy.run_path("summits.py", run_name="__main__")
    runpy.run_path("search_data.py", run_name="__main__")

    # we only care about merged_search_data.json
    check_delete('full_data.json')
    check_delete('search_data.json')
    check_delete('summit_search_data.json')

    if final_od:
        shutil.copytree("summits", final_od, dirs_exist_ok=True)
        shutil.copytree("parks", final_od, dirs_exist_ok=True)
        shutil.copy2("merged_search_data.json", final_od)


if __name__ == "__main__":
    main()
