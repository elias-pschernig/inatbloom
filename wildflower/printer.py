import json
from browser import document, ajax, html, window
from shared import Parameters
from shared import SpeciesList
import html5_plot
import wildflower

state = wildflower.State()

class Downloader(wildflower.Downloader):
    def progress(self, done, p):
        print("progress", done, p)
        if done:
            document["around"].innerHTML = ""
            state.picture_click = None
            html5_plot.state = state
            state.sl.args.first_header_only = True
            state.sl.args.check_rare = "1"
            html5_plot.plot_list()
        else:
            document["around"].innerHTML = "%.0f%%" % (p * 100)

def main():
    p = Parameters()
    p.from_query(document)

    p.downloader = Downloader()
    state.sl = SpeciesList()
    state.sl.from_parameters(p)
