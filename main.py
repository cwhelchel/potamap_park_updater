import json
import os
import shutil
import requests
from locations import US_LOCATIONS
from pathlib import Path
from geojson import Point, Feature, FeatureCollection, dumps

#
# This script grabs all parks from the pota /location/parks API endpoint for
# each location listed in US_LOCATIONS array. They are then converted into
# proper geojson files and put into individual folders to be plopped into the
# public/data directory of the potamap.us source.
#
# These parks are in a FEATURECOLLECTION geoJson obj and each feature has the
# following properties:
#   - NAME = the pota park reference (eg: K-7465)
#   - TITLE = the pota real name "Flat Creek Public Fishing Area"
# (more added later maybe)
#
# - Cainan
#


def convert(input: str, output: str, loc: str):
    features = []
    parks = None

    print(f"converting {input} for {loc}")

    with open(input, 'r', encoding='UTF-8') as read_file:
        parks = json.loads(read_file.read())
        for park in parks:
            point = Point((park['longitude'], park['latitude']))
            f = Feature(geometry=point, properties={
                        'NAME': park['reference'], 'TITLE': park['name']})
            features.append(f)

    fc = FeatureCollection(features=features, name=f"{loc} POTA PARKS")

    with open(output, 'w', encoding='UTF-8') as out_file:
        text = dumps(fc)
        out_file.write(text)


def save_json(url: str, file_name: str) -> int:
    '''Request json data from an endpoint and save it to the given file.'''

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        with open(file_name, 'w') as out_file:
            out_file.write(json.dumps(data, indent=4))

    return r.status_code


def _get_path(file_name: str) -> Path:
    return Path("parks", file_name)


def download_park(location: str):
    '''
    Checks if the data file is present for the given location, if not, it
    downloads the park data for the location.

    Parameters
    ------------
    location : string
        the POTA location string
    '''

    loc = location

    url = f"https://api.pota.app/location/parks/{loc}"
    json_file = f"parks-{loc}.json"
    file = _get_path(json_file)

    save_json(url, file)


if __name__ == "__main__":

    if not Path('parks').exists():
        os.mkdir('parks')

    for loc in US_LOCATIONS:
        print(f'downloading {loc}')
        download_park(loc)

    print('converting park files to geojson')

    for file in Path("parks").glob("parks*.json"):
        output = file.with_suffix(".geojson")

        x = file.name
        location_name = x[6:11]
        newDir = Path("parks", location_name)
        newDir.mkdir(exist_ok=True)

        convert(file, output, location_name)

        shutil.move(output, newDir.joinpath(output.name))
