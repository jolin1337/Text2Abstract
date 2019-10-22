from dotenv import load_dotenv
load_dotenv()

import json
import requests
import pickle
import os
import binascii


def get_mm_land():
    return json.loads(open("match_cities_and_areas/municipality_mmarea_map.json").read())


def soldr_request(payload, endpoint='locations', use_cache=False, timeout=1):
    try:
        if not 'SOLDR_TOKEN' in os.environ:
            print("No soldr token found. export the `SOLDR_TOKEN` environment variable and try again")
            print("> export SOLDR_TOKEN=<Soldr Token>")
            exit()
        if not 'SOLDR_URL' in os.environ:
            print("No soldr url found. export the `SOLDR_URL` environment variable and try again")
            print("> export SOLDR_URL=<Soldr url>")
            exit()
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + os.environ['SOLDR_TOKEN']
        }
        # payload = { 'searchString' : location }
        cache_file = '.cache/soldr_request_' + str(endpoint) + str(binascii.hexlify(pickle.dumps(list(payload.items()))))
        if use_cache: os.makedirs('.cache', exist_ok=True)
        if use_cache and os.path.exists(cache_file):
            return pickle.load(open(cache_file, 'rb'))
        r = requests.get(
                os.environ['SOLDR_URL'] + str(endpoint),
                params=payload,
                headers=headers,
                timeout=timeout)
        res = r.json()
        if use_cache: pickle.dump(res, open(cache_file, 'wb'))
        return res
    except:
        return None
