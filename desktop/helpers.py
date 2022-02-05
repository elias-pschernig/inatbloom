# desktop python helpers - will not work under brython
import re
import requests
import time
import json
import hashlib
import os

id_usa = "1"
id_state = {}

sleep_seconds = 0.5
sleep_counter = 0
def cache(site, query, ignore_cache=False):
    global sleep_counter
    global sleep_seconds
    query = site + query

    md5 = False
    cache_name = "cache/" + re.sub(r"\W", "_", query)
    orig_cache_name = cache_name
    if len(cache_name) > 200:
        cache_name = cache_name[:200] + hashlib.md5(cache_name.encode("utf8")).hexdigest()
        md5 = True

    if not ignore_cache and os.path.exists(cache_name):
        return cache_name
    #if md5:
    #    verbose("original cache name: {}".format(orig_cache_name))
    #    verbose("     md5 cache name: {}".format(cache_name))
    verbose("requesting", query)
    if args.offline:
        raise Exception("Offline mode but missing request in cache.")
    if not os.path.exists("cache"):
        os.mkdir("cache")
    r = requests.get(query)
    if r.status_code == 429:
        sleep_seconds += 1
        sleep_counter = 10
        verbose("delay now", sleep_seconds)
    else:
        if sleep_counter > 0:
            sleep_counter -= 1
            if sleep_counter == 0:
                if sleep_seconds > 1:
                    sleep_seconds -= 1
                if sleep_seconds > 1:
                    sleep_counter = 10
    open(cache_name, "wb").write(r.content)
    time.sleep(sleep_seconds)
    return cache_name

def get3(site, query, ignore_cache = False):
    cache_name = cache(site, query, ignore_cache = ignore_cache)
    return open(cache_name).read()

def get2(site, query, ignore_cache = False):
    for t in range(4):
        text = get3(site, query, ignore_cache = ignore_cache)
        try:
            j = json.loads(text)
            return j
        except json.decoder.JSONDecodeError:
            if t == 3:
                raise
            cache_name = cache(site, query)
            warning("Retrying", cache_name)
            os.remove(cache_name)
            time.sleep(3 * sleep_seconds)
    raise Exception(f"Could not load {site + query}")

def get(query, ignore_cache = False):
    return get2("https://api.inaturalist.org/v1/", query, ignore_cache = ignore_cache)

def get_old(query):
    return get2("https://www.inaturalist.org/", query)

def get_states():
    j = get_old(f"places.json?place_type=State&ancestor_id={args.country}&per_page=100")
    for c in j:
        name = c["name"].lower()
        id_state[name] = c["id"]
        verbose("state", name, c["id"])

def verbose(*p):
    if not args.quiet:
        print(*p)

def warning(*p):
    print(*p)


