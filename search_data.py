
import json


if __name__ == "__main__":
    parks = 'search_data.json'
    summits = 'summit_search_data.json'

    with open(parks, encoding='utf-8') as park_data:
        data1 = json.load(park_data)

    with open(summits, encoding='utf-8') as summit_data:
        data2 = json.load(summit_data)

    # data 1 and 2 are json lists
    merged = data1 + data2

    print('merging files...')

    with open('full_data.json', 'w', encoding='utf-8') as f_out:
        json.dump(merged, f_out, indent=None)

    print('trimming search data for bootstrap5-autocomplete...')
    src_data = []

    for x in merged:
        # {'reference_id': 'W7Y/SL-063', 'name': 'Fish Creek Mountain', 'lat': 42.5886, 'lon': -110.5558, 'grid': ''}  # noqa
        # print(x)

        src_data.append({
            "v": x['reference_id'],
            "l": x['reference_id'] + ' - ' + x['name']
        })

    with open('merged_search_data.json', 'w', encoding='utf-8') as f_out:
        json.dump(src_data, f_out, indent=None, separators=(',', ':'))
