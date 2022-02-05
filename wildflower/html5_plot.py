import calendar
import colorsys
from browser import document, ajax, html, window
import math
import shared

row_size = 1.5 # em
debug_grid = False
notew = 8
textw = 16
picw = 4.5
colgap = 1

def week_color(i, args):
    p = (i - args.w0) / args.wn
    h = 0.6 - 0.7 * p
    if h < 0: h += 1
    v = min(1, 0.5 + 0.7 * p)
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, 1, v)]
    return "#%02x%02x%02x" % (r, g, b)

def create_histogram(weeks):
    sl = state.sl
    args = sl.args

    div = html.DIV(Class = "histogram")

    for week in range(args.w0, args.w0 + args.wn):
        week = 1 + (week - 1) % 53
        v = weeks[week] / 9
        
        bar = html.DIV(Class = "bar")
        bar.style["border-left-color"] = week_color(week, args)
        bar.style["height"] = f"{v}em"
        div <= bar

    return div

def draw_months():
    sl = state.sl
    args = sl.args

    d = html.DIV(Class = "months")
    histw = args.wn / 2

    for mi in range(args.mn):
        m = 1 + ((args.m0 - 1) + mi) % 12
        mname = calendar.month_name[m]
        mspan = html.SPAN(Class = "month")
        mspan <= html.SMALL(mname)
        mspan.style["left"] = f"{mi * histw / args.mn}em"
        d <= mspan

    return d

def header_row(num):
    sl = state.sl
    args = sl.args

    row = html.DIV(Class = "header")
    row <= html.SPAN(args.title if num == 0 else "&nbsp;", Class = "title");
    row <= draw_months()
    return row

def footer_row(plotter, num):
    sl = state.sl
    args = sl.args

    row = html.DIV(Class = "footer")
    row <= draw_months()

    def parameterize(text):
        text = text.replace("⚘", f"⚘{plotter.n}")
        text = text.replace("$", "")
        text = text.replace("^P", "<sup>P</sup>")
        text = text.replace("^T", "<sup>T</sup>")
        text = text.replace("^E", "<sup>E</sup>")
        return text

    notes = [x.replace("|", "\n") + "\n" for x in args.footers.split("||")]
    nc = len(notes)
    span = html.SPAN(Class = "footer");
    span <= html.SMALL(parameterize(notes[num % nc]))
    row <= span
    
    return row

def vlines(page):
    sl = state.sl
    args = sl.args
    n = int(args.columnsize)
    histw = args.wn / 2
    for mi in range(0, args.mn + 1):
        div = html.DIV(Class = "vline")
        div.style["left"] = f"{mi * histw / args.mn}em"
        div.style["height"] = f"{n * row_size}em"
        page <= div

def plot_list(to_i = None): # -> bool
    around = document["around"]
    
    sl = state.sl
    args = sl.args
    names, weeks, pictures = sl.result

    class Plotter: pass
    plotter = Plotter()
    plotter.n = len(names)

    n = len(names)
    nc = int(args.columnsize)
    columns = int(args.columns)
    ps = nc * columns

    pages = int(math.ceil(n / ps))

    # border + padding + ... + border
    histw = args.wn / 2
    colw = 0.125 + 0.25 + histw + notew + textw + picw * 3 + 0.125

    start = 0
    added = []
    if to_i is not None:
        start = to_i - 1
    if start == 0:
        around.text = ""
    i = start * columns
    for pi in range(start, pages):
        page = html.DIV(Class = "page")
        page.style["width"] = f"{(colw + colgap) * columns}em"
        around <= page
        for ci in range(columns):
            column = html.DIV(Class = "column")
            
            column.style["width"] = f"{colw}em"
            page <= column
            added += plot_column(plotter, column, i * nc, i * nc + nc, i)
            last = i * nc + nc
            
            i += 1

        if pi + 1 == to_i:
            if pi + 1 < pages: return True, added
    return False, added

def plot_column(plotter, column, a, b, num):
    sl = state.sl
    args = sl.args
    names, weeks, pictures = sl.result
    n = len(names)

    if debug_grid:
        pad = 0.25
        x = pad
        histw = args.wn / 2
        for pos in [0, histw, 0.5, notew - 1, 0.5, textw, picw, picw, picw]:
            x += pos
            div = html.DIV(Class = "debugvline")
            div.style["left"] = f"{x}em"
            column <= div

    if num == 0 or not args.first_header_only:
        column <= header_row(num)

    d = html.DIV(Class = "rows")
    column <= d
    vlines(d)

    added = []
    counter = 0
    for i in range(a, b):
        s = None
        if i < n:
            name = names[i]
            tid = sl.ids[i]
            pic = pictures[i]
            s = sl.species_by_id[tid]
            tid = s.id
            added.append(s)
            scientific = s.scientific
        else:
            name = ""
            pic = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWP4////fwAJ+wP9CNHoHgAAAABJRU5ErkJggg=="
            tid = 0
            scientific = ""
        row = html.DIV(Class = "row", id="t" + str(tid))
        d.attach(row)

        hist = create_histogram(weeks[i] if i < n else [0] * 54)
        row <= hist

        seen = html.SPAN(Class = "seen")
        if tid in sl.found:
            seen <= str(len(sl.found[tid]))
            text = ""
            for date, place in sl.found[tid]:
                rowtext = date + " " + place
                text += rowtext.replace(" ", "&nbsp;") + "<br/>"
            seen <= html.SPAN(text, Class = "info")
        row <= seen

        name2 = sl.capitalize(name)

        if args.check_rare:
            sp = s
            if sp and sp.rare:
                if sp.rare == "P" or sp.rare == "T" or sp.rare == "E" or sp.rare == "U":
                    name2 += "<sup>" + sp.rare + "</sup>"

        if args.inat_links:
            inat = f"https://www.inaturalist.org/observations?verifiable=true&taxon_id={tid}&place_id=31"
            row <= html.A(f"{name2}", href = inat, Class = "name")
        else:
            row <= html.SPAN(f"{name2}", Class = "name")

        c = "col" + str(counter % 3)
        idiv = html.DIV(Class = "pic " + c)
        img = html.IMG(src = pic, Class = "pic", id = tid)
        idiv <= img
        
        if state.pic_hover_cb:
            state.pic_hover_cb(idiv, tid, scientific, i, n)
        else:
            span_text = f"{scientific}<br/>inat id={tid}"
            idiv <= html.SPAN(span_text, Class = "info")
        row <= idiv
        if state.picture_click:
            img.bind("click", state.picture_click)
        counter += 1

    d <= footer_row(plotter, num)
    return added
