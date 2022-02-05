import json
from browser import document, ajax, html, window
from shared import Parameters
from shared import SpeciesList
import html5_plot
import wildflower
import saved
from datetime import date

state = wildflower.State()

def pic_hover_cb(idiv, tid, scientific, i, n):
    span_text = f"id={tid}<br/>{scientific}<br/>{i+1}/{n}"
    span = html.SPAN(Class = "info")
    span <= html.SPAN(span_text)
    button = html.BUTTON("submit")
    def picture_submit_click(ev):
        name = state.sl.species_by_id[tid].name
        document["edit_taxon"].value = f"{tid} ({name})"
        document["button_submit"].click()
    button.bind("click", picture_submit_click)
    span <= button
    idiv <= span

state.pic_hover_cb = pic_hover_cb

def picture_click(ev):
    taxon = str(ev.target.id)
    name = state.sl.species_by_id[taxon].name
    document["edit_taxon"].value = f"{taxon} ({name})"

class Args:
    pass

def button_submit(ev):
    taxon = document["edit_taxon"].value.split(None, maxsplit = 1)[0]
    place = document["edit_place"].value
    date = document["edit_date"].value
    document["button_submit"].value = "..."

    def _cb(r):
        if r.status == 200:
            document["button_submit"].value = "Submit"
            get_found()
        else:
            pass

    url = "https://elias.pschernig.com/wildflower/api/data"
    req = ajax.ajax()
    req.open("POST", url, True)
    req.bind("complete", _cb)
    req.send({"taxon": taxon, "place": place, "date": date})

def get_found():
    def _cb(r):
        print(r.status)
        if r.status == 200:
            state.sl.found = json.loads(r.responseText)
            show_dates()
            document["around"].innerHTML = ""
            html5_plot.plot_list()
        else:
            pass

    url = "https://elias.pschernig.com/wildflower/api"
    print("GET", url)
    req = ajax.ajax()
    req.open("GET", url, True)
    req.bind("complete", _cb)
    req.send()  

def show_dates():
    document["dates"].innerHTML = ""
    dates = {}
    places = {}
    for tid in state.sl.found:
        for date, place in state.sl.found[tid]:
            if date not in dates:
                dates[date] = set()
                places[date] = set()
            dates[date].add(tid)
            places[date].add(place)
    for date in sorted(dates.keys()):
        text = "<b>" + date[-2:] + "</b>" + "<br/>" + str(len(dates[date]))
        day = html.DIV(text, Class = "day")
        names = []
        for tid in dates[date]:
            try:
                names.append(state.sl.species_by_id[tid].name)
            except KeyError as e:
                print(e)
                names.append("error")
        date_places = sorted(list(places[date]))
        text = "/".join(date_places)
        text = "<b>" + text + "</b><br/>"
        columns = len(names) // 30
        col = 0
        for name in sorted(names):
            text += name.replace(" ", "&nbsp;")
            if col == columns:
                text += "<br/>"
                col = 0
            else:
                text += ", "
                col += 1
        day <= html.SPAN(text, Class = "info")
        document["dates"] <= day

def main():

    today = date.today().strftime("%Y/%m/%d")
    document["edit_date"].value = today

    document["button_submit"].bind("click", button_submit)
    
    p = Parameters()
    state.sl = SpeciesList()
    state.sl.from_saved(saved.saved)
    state.picture_click = picture_click
    html5_plot.state = state
    state.sl.args.columns = 1
    state.sl.args.columnsize = 250
    state.sl.args.inat_links = True
    p.fix_arguments(state.sl.args)

    get_found()
