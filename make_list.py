#!/usr/bin/env python3
import requests
import re
import os
import json
import math
import plot_matplotlib as plot
import time
import shutil
import argparse
import web
import time
import desktop.list_plot as list_plot
import hashlib
import wildflower.shared as shared
from wildflower.shared import Parameters
from wildflower.shared import SpeciesList
import wildflower.shared
import queue
from wildflower.api import database
import desktop.helpers

def main():
    global args
    without = ",".join([str(x) for x in shared.exclude_taxons])
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--places")
    p.add_argument("-m", "--months")
    p.add_argument("-s", "--species")
    p.add_argument("-i", "--include")
    p.add_argument("-e", "--exclude")
    p.add_argument("-r", "--remove")
    p.add_argument("-t", "--title")
    p.add_argument("-f", "--footers")
    p.add_argument("-o", "--output")
    p.add_argument("-c", "--columns")
    p.add_argument("-C", "--columnsize")
    p.add_argument("-P", "--pictures")
    p.add_argument("-E", "--extra")
    p.add_argument("-q", "--quiet", action = "store_true")
    p.add_argument("-off", "--offline", action = "store_true")
    p.add_argument("-nc", "--nocache", action = "store_true")
    p.add_argument("-ncf", "--nocachefor", default = "")
    p.add_argument("--min-count")
    p.add_argument("--database")
    p.add_argument("--inatquery")
    p.add_argument("--list-found", action = "store_true")
    p.add_argument("--count", action = "store_true")
    p.add_argument("--scientific", action = "store_true")
    p.add_argument("--check-native", action = "store_true")
    p.add_argument("--maybe-introduced", action = "store_true")
    p.add_argument("--check-wikispecies", action = "store_true")
    p.add_argument("--check-rare", action = "store_true")
    p.add_argument("--want-histogram", type=int, default=1)
    p.add_argument("--want-pictures", type=int, default=1)
    p.add_argument("--want-seen", type=int, default=1)
    p.add_argument("--month-headers", type=int, default=0)
    p.add_argument("--remove-file") # species to remove
    p.add_argument("--only1", action="store_true")
    args = p.parse_args()

    args.check_rare = "1" if args.check_rare else "0"
    args.check_native = "1" if args.check_native else "0"
    args.maybe_introduced = "1" if args.maybe_introduced else "0"
    args.check_wikispecies = "1" if args.check_wikispecies else "0"
    p = Parameters()
    p.fix_arguments(args)

    desktop.helpers.args = args

    if args.database:
        database.credentials = args.database

    if args.list_found:
        print_found()
        return

    if args.count:
        count_flowers()
        return

    list_species()

class Downloader(wildflower.shared.Downloader):
    def download(self, url, ignore_cache, on_success):
        j = desktop.helpers.get2(url, "", ignore_cache = ignore_cache)
        state.queue.put((on_success, j))

    def progress(self, done, p):
        if done:
            state.done = True
            names, weeks, pictures = state.sl.result
            if args.want_pictures == 1:
                pictures = [desktop.helpers.cache(url, "") for url in pictures]
            #list_plot.plot(names, weeks, pictures, args)
        else:
            pass
            #print("%.0f%%" % (p * 100))

class State:
    pass

state = State()

def list_species():
    args.downloader = Downloader()
    state.queue = queue.Queue()
    state.done = False
    state.sl = SpeciesList()
    state.sl.from_parameters(args)
    while not state.done:
        cb, j = state.queue.get()
        cb(j)

    print("listed {} species".format(len(state.sl.result[0])))

    names, weeks, pictures = state.sl.result
    with open("new.txt", "w") as f:
        for name in sorted(names, key = lambda x: x.lower()):
            f.write(name + "\n")

    with open("names.txt", "w") as f:
        scpecies = [state.sl.species_by_id[inid].scientific for inid in state.sl.ids]
        for name in sorted(scpecies, key = lambda x: x.lower()):
            f.write(name + "\n")

    with open("dump.txt", "w") as f:
        for i in range(len(names)):
            print(names[i], weeks[i], pictures[i], file=f)

    with open("saved_new.js", "w") as f:
        f.write(json.dumps(state.sl.to_saved(), indent=1))

    p2 = []
    if args.want_pictures == 1:
        for p in pictures:
            filename = desktop.helpers.cache(p, "")
            p2.append(filename)
    pictures = p2

    months = []
    for x in state.sl.bloom_start:
        months.append((x - 1) * 12 // 52 + 1)
    list_plot.state = state
    list_plot.plot(names, weeks, pictures, args, months)

def print_found():
    args.downloader = Downloader()
    state.queue = queue.Queue()
    state.done = False
    state.sl = SpeciesList()
    state.sl.from_parameters(args)
    while not state.done:
        cb, j = state.queue.get()
        cb(j)

    r = database.list_found()
    by_date = sorted(r, key = lambda found: (found[2],found[1],found[0]))
    already = set()
    names = []
    for found in by_date:
        if found[0] in already: continue
        already.add(found[0])
        names.append(found)
    for x in names:
        name = state.sl.species_by_id[str(x[0])].name
        location = x[1]
        day = x[2]
        print(day, name, location)

def count_flowers():
    args.downloader = Downloader()
    state.queue = queue.Queue()
    state.done = False
    state.sl = SpeciesList()
    state.sl.from_parameters(args)
    while not state.done:
        cb, j = state.queue.get()
        cb(j)

    print(len(state.sl.species))

if __name__ == "__main__":
    main()
