import json
from browser import document, ajax, html, window, timer
from shared import Parameters
from shared import SpeciesList
import html5_plot
import wildflower
import saved
import math

state = wildflower.State()

def picture_click(ev):
    last = state.last_clicked
    if last is not None:
        last.style["width"] = None
        last.style["height"] = None
        last.style["z-index"] = None
        last.style["left"] = None
        last.style["top"] = None
        if last == ev.target:
            state.last_clicked = None
            return

    ev.target.style["width"] = "16em"
    ev.target.style["height"] = "16em"
    ev.target.style["z-index"] = "2"
    ev.target.style["left"] = "-4em"
    ev.target.style["top"] = "-4em"
    state.last_clicked = ev.target

    taxon = str(ev.target.id)

class Found:
    def __init__(self):
        self.seen = set()
        self.processed = []
        self.considered = set()

    def reset(self):
        found.seen = set()
        found.considered = set()
        for s in self.processed:
            span = document.querySelector("div#t{} span.seen".format(s.id))
            if span:
                span.text = ""

    def process(self):
        species = []
        for s in self.processed[:]:
            if s.id not in self.considered:
                self.considered.add(s.id)
                species.append(str(s.id))
                if len(species) == 30:
                    break
        if species:
            self.download(species)

    def download(self, species):
        user = document["edit_user"].value
        args = state.sl.args
        names, weeks, pictures = state.sl.result
       
        c = []
        # actually, seeing species in another place also counts!
        #c += ["place_id=" + args.places]
        c += ["taxon_id=" + (",".join(species))]
        c += ["rank=species,subspecies,variety,form,hybrid"]
        c += ["verifiable=true"]
        c += ["user_id=" + user]
        c += ["per_page=200"]
        url = "https://api.inaturalist.org/v1/observations?" + ("&".join(c))
        Downloader().download_pages(url, ignore_cache=False, on_success=self.done)

    def done(self, results):
        found_seen = {}
        for result in results:
            inatid = result["taxon"]["id"]
            if result["taxon"]["rank"] in ["subspecies","variety","form"]:
                inatid = result["taxon"]["ancestor_ids"][-2]
            day = result["observed_on"]
            if inatid in found_seen and found_seen[inatid] < day:
                continue
            span = document.querySelector("div#t{} span.seen".format(inatid))
            if span:
                span.text = day
                found_seen[inatid] = day
                self.seen.add(inatid)
                document["seen"].text = "Seen {} out of {}!".format(len(self.seen), len(self.considered))
            #print(result["taxon"]["id"], result["observed_on"], result["place_guess"])

        document["seen"].text = "Seen {} out of {}!".format(len(self.seen), len(self.considered))
        if len(self.considered) < len(self.processed):
            timer.set_timeout(found.process, 0)

found = Found()

class Downloader(wildflower.Downloader):
    def cache_transform(self, text):
        j = json.loads(text)
        results2 = []
        for result in j["results"]:
            t = result["observed_on"]
            p = result["place_guess"]
            taxon_id = result["taxon"]["id"]
            rank = result["taxon"]["rank"]
            ancestors = result["taxon"]["ancestor_ids"]
            results2.append({"observed_on" : t,
                "place_guess" : p,
                "taxon" : { "id" : taxon_id, "rank" : rank, "ancestor_ids": ancestors }})
        j["results"] = results2
        return json.dumps(j)

def button_submit(ev):
    found.reset()
    timer.set_timeout(found.process, 0)

def main():
    document["button_submit"].bind("click", button_submit)

    p = Parameters()
    state.last_clicked = None
    state.sl = SpeciesList()
    state.sl.from_saved(saved.saved)
    state.picture_click = picture_click
    html5_plot.state = state
    state.sl.args.columns = 1
    state.sl.args.inat_links = True
    state.sl.args.first_header_only = True
    state.sl.args.check_rare = "1"
    p.fix_arguments(state.sl.args)

    document["seen"].text = "Seen 0 out of {}!".format(len(state.sl.species))

    document["around"].innerHTML = ""

    timer.set_timeout(lambda: part(1), 0)

def part(page):
    more, added = html5_plot.plot_list(page)
    found.processed += added
    timer.set_timeout(found.process, 0)
    if more:
        timer.set_timeout(lambda: part(1 + page), 0)
