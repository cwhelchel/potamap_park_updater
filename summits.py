from datetime import datetime
import json
import os
import re
import shutil
import requests
import csv
from locations import US_SUMMITS
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

regions: list[str] = []
summits: dict[str, list[str]] = {}


def convert():
    for region in summits.keys():
        features = []
        output = _get_path(f"{region.replace('/','--')}.geojson")
        for summit in summits[region]:
            point = Point((summit['longitude'], summit['latitude']))
            f = Feature(geometry=point,
                        properties={
                            'NAME': summit['reference'],
                            'TITLE': summit['name'],
                            'REGION': summit['region'],
                            'ASSOCIATION': summit['assoc'],
                            'POINTS': summit['pts'],
                            'BONUSPOINTS': summit['bonuspts'],
                        })
            features.append(f)

        fc = FeatureCollection(features=features, name=f"{region} SUMMITS")

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


def save(url: str, file_name: str) -> int:
    '''Request json data from an endpoint and save it to the given file.'''

    r = requests.get(url)
    if r.status_code == 200:
        data = r.text
        with open(file_name, 'w', encoding='utf-8') as out_file:
            out_file.write(data)

    return r.status_code


def _get_path(file_name: str) -> Path:
    return Path("summits", file_name)


def download_summit_list() -> Path:
    url = "https://storage.sota.org.uk/summitslist.csv"
    json_file = "summitslist.csv"
    file = _get_path(json_file)
    save(url, file)
    return file


def _parse(row: list[str]):
    ref = row[0]
    name = row[3]
    valid_until = row[8]  # date ex: 31/12/2099
    json = {
        "reference": ref,
        "name": name,
        'longitude': row[4],
        'latitude': row[5],
        'region': row[2],
        'assoc': row[1],
        'pts': row[6],
        'bonuspts': row[7]
    }

    valid_dt = datetime.strptime(valid_until, '%d/%m/%Y')
    now = datetime.now()

    if now > valid_dt:
        print('skipping summit that is no longer valid!')
        return

    # get the association and region part of the summit code
    m = re.match(r'(.*\/[A-Z]{2})-', ref)
    if m:
        region = m.group(1)
        if region not in summits.keys():
            regions.append(region)
            summits[region] = [json]
        else:
            summits[region].append(json)


if __name__ == "__main__":

    assoc = []

    if not Path('summits').exists():
        os.mkdir('summits')

    print('downloading summit list')
    downloaded_fname = download_summit_list()

    with open(downloaded_fname, encoding='utf-8') as csv_file:
        # first line is file metadata
        # this skip that first line so the header is used for DictReader
        print(csv_file.readline())

        reader = csv.DictReader(csv_file, quotechar='"')

        for row in reader:
            cols = [
                row['SummitCode'],
                row['AssociationName'],
                row['RegionName'],
                row['SummitName'],
                float(row['Longitude']),
                float(row['Latitude']),
                row['Points'],
                row['BonusPoints'],
                row['ValidTo']
            ]

            if cols[0].startswith('W'):
                # print(','.join(cols))
                _parse(cols)

        print('\n'.join(regions))
        print('\nconverting summits to geojson...')
        convert()

    print('moving files')

    for file in Path("summits").glob("*.geojson"):
        output = file.with_suffix(".geojson")
        fn_no_ext = file.stem

        layer = {
            'title': f'Summits { fn_no_ext.replace("--", "/") } ',
            'file': str(output)
        }
        print(json.dumps(layer))

        region = fn_no_ext[:fn_no_ext.find('--')]

        for state in US_SUMMITS[region]:
            newDir = Path("summits", state)
            newDir.mkdir(exist_ok=True)
            shutil.copy(output, newDir.joinpath(output.name))

        # delete the file
        file.unlink(missing_ok=True)
