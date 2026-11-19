

import runpy
import shutil
import os.path


def main():
    def check_delete(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)

    shutil.rmtree('parks', ignore_errors=True)
    shutil.rmtree('summits', ignore_errors=True)

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


if __name__ == "__main__":
    main()
