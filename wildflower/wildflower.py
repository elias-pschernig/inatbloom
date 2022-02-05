import json
from browser import document, ajax, html, window
import shared
import html5_plot
from browser.local_storage import storage
from browser import timer
from shared import Parameters
from shared import SpeciesList
import shared
import time

class State:
    def __init__(self):
        self.info_cb = None
        self.pic_hover_cb = None

state = State()

def picture_click(ev):
    taxon = str(ev.target.id)
    url = ev.target.src
    document["edit_pictures"].value += f"{taxon}={url}\n"

class Downloader(shared.Downloader):
    def __init__(self):
        self.wait = 0

    def cache_transform(self, text):
        return text

    def download(self, url, ignore_cache, on_success):
        timer.set_timeout(lambda: self.download_real(url, ignore_cache, on_success), self.wait)

    def download_real(self, url, ignore_cache, on_success):
        if not ignore_cache and url in storage:
            print("(cache)", url)
            text = storage[url]
            try:
                j = json.loads(text)
                timer.set_timeout(lambda: on_success(j), 0)
            except Exception as e:
                del storage[url]
                self.wait += 2000
                timer.set_timeout(lambda: self.download(url, ignore_cache, on_success), 2000)
            return
        def _cb(r):
            if r.status == 200:
                if self.wait > 0:
                    self.wait -= 250
                storage[url] = self.cache_transform(r.responseText)
                j = json.loads(storage[url])
                on_success(j)
            else:
                self.wait += 2000
                timer.set_timeout(lambda: self.download(url, ignore_cache, on_success), 2000)

        print("(get)", url)
        req = ajax.ajax()
        req.open("GET", url, True)
        req.bind("complete", _cb)
        req.send()

    def progress(self, done, p):
        if done:
            document["button_fetch"].innerHTML = "Submit"
            state.picture_click = picture_click
            html5_plot.state = state
            document["info"].text = f"{len(state.sl.result[0])} flowers included"
            html5_plot.plot_list()
            j = state.sl.to_saved()
            print(json.dumps(j, indent=1))
        else:
            document["button_fetch"].innerHTML = "%.0f%%" % (p * 100)

def button_fetch(ev):
    around = document["around"]
    if len(around.children) > 0:
        around.removeChild(around.children[0])
    p = Parameters()
    p.from_input(document)
    url = document.documentURI.split("?")[0]
    document["edit_link"].value = url + "?" + p.get_query_string()

    p.downloader = Downloader()
    state.sl = SpeciesList()
    state.sl.from_parameters(p)
    
def button_print(ev):
    p = Parameters()
    p.from_input(document)
    window.open("printer.html?" + p.get_query_string())

def main():
    p = Parameters()
    p.from_query(document)
    p.to_input(document)

    document["button_fetch"].bind("click", button_fetch)
    document["button_print"].bind("click", button_print)
    
    around = document["around"]

