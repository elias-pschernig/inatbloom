# create flower list using matplotlib - will not work under brython
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import image as mpli
import plot_matplotlib
import math
from matplotlib.transforms import Bbox
from matplotlib.backends.backend_pdf import PdfPages
import numpy
import calendar
import wildflower.shared as shared

def month_color(m):
    m = (m + 11) % 12
    return [
        "#ffffff", "#e0e0ff", "#b0ffb0", "#d0d0a0", "#ffb090", "#ff0000",
        "#bf2fbf", "#bfbf00", "#e0d0c0", "#b0a080", "#a0a0a0", "#e0e0ff"][m]

def week_color(i, args):
    p = (i - args.w0) / args.wn
    h = 0.5 - p
    if h < 0: h += 1
    r, g, b = mcolors.hsv_to_rgb((h, 0.75, 0.75))
    return (r, g, b)

def plot(names, weeks, pictures, args, months=None):
    no_pictures = False

    n = len(names)
    per_page = args.columnsize * args.columns
    pages = int(math.ceil(n / per_page))

    if not args.output:
        return

    if args.want_pictures != 1:
        no_pictures = True

    class Plotter: pass
    plotter = Plotter()
    plotter.month = 0
    plotter.n = len(names)
    plotter.i = 0

    if pages > 1 and args.output.endswith(".pdf"):
        with PdfPages(args.output) as pdf:
            pagenum = 0
            while plotter.i < plotter.n:
                print(f"page {1+pagenum}")
                plot_page(plotter, names, weeks, pictures, args, pagenum, months=months, want_pictures=not no_pictures)
                pdf.savefig()
                pagenum += 1
                if args.only1:
                    break
    elif no_pictures:
        fig = plot_page(plotter, names, weeks, pictures, args, None, months=months, want_pictures=False)
        fig.savefig(args.output)
    else:
        fig = plot_page(plotter, names, weeks, pictures, args, None, months=months)
        #plt.show()
        fig.savefig(args.output)
        #fig.savefig("ohio-spring-bloom.jpg", pad_inches = 0)

def plot_page(plotter, names, weeks, pictures, args, page_number=0,
        want_pictures=True, months=None, start_month=0):

    pages = args.columns
    triple_pictures = False
    debug_grid = False

    text_width = 162
    if args.want_seen == 1:
        notes_width = 100
        header = 1
    else:
        notes_width = 0
        header = 1
    footer = 1
    cell_height = 22
    if args.want_histogram:
        histogram_width = cell_height * args.mn
        header += 1
        footer += 1
    else:
        histogram_width = 0
    if want_pictures:
        if triple_pictures:
            picture_width = cell_height * 9
        else:
            picture_width = cell_height
    else:
        picture_width = 0
    cell_width = text_width + notes_width + histogram_width + picture_width

    leftmargin = 20
    rightmargin = 20
    topmargin = 22
    page_x = leftmargin
    column_gap = 10
    bottommargin = 22

    n_page = args.columnsize
    nrows = n_page + header + footer
    skip_ni = 0

    def add_header():
        if args.want_histogram:
            for i in range(2):
                if i == 0:
                    y = topmargin + cell_height * 1.5
                else:
                    y = height - bottommargin - cell_height * 2
                for mi in range(args.mn):
                    mname = calendar.month_name[1 + (args.m0 + mi - 1) % 12]
                    hx = page_x + picture_width + text_width + notes_width
                    hx += mi / args.mn * histogram_width
                    ax.text(hx, y + cell_height, mname, fontsize = 10, rotation = 45)
                    c = month_color(args.m0 + mi)
                    if mi > 0 and i == 0:
                        ax.add_line(Line2D([hx, hx], [topmargin + cell_height, height - bottommargin - cell_height], color = c, zorder = -2))
                        #plt.axvline(x, color = c, zorder = -2)

        if args.want_seen == 1:
            hx = page_x + text_width + picture_width
            ax.text(hx + notes_width / 4, topmargin, "\nWhere", fontsize = 10, ha="center", va="top", color="#8080ff")
            ax.text(hx + notes_width * 3 / 4, topmargin, "\nWhen", fontsize = 10, ha="center", va="top", color="#8080ff")

    page_width = cell_width
    page_height = cell_height * nrows
    width = page_width * pages + leftmargin + rightmargin + (pages - 1) * column_gap
    height = page_height + topmargin + bottommargin
    dpi = 72

    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi * 2)
    #fig.subplots_adjust(margin/width, margin/height,
    #                    (width-margin)/width, (height-topmargin+bottommargin)/height)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, width) # - margin * 2)
    ax.set_ylim(height, 0) #cell_height * (nrows-0.5), -cell_height/2.)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_axis_off()
    #ax.set_title(args.title, fontsize=12, loc="left", pad=10)
    ax.text(leftmargin, topmargin, args.title, fontsize=12,
                    ha='left',
                    va='top', weight="bold")

    if debug_grid:
        ax.add_patch(Rectangle(xy=(0, 0), width=dpi, height=dpi, fill=False, color="#ff0000"))
        ax.add_patch(Rectangle(xy=(width-dpi, height-dpi), width=dpi, height=dpi, fill=False, color="#ff0000"))
        ax.add_patch(Rectangle(xy=(0, height-dpi), width=dpi, height=dpi, fill=False, color="#ff0000"))
        ax.add_patch(Rectangle(xy=(width-dpi, 0), width=dpi, height=dpi, fill=False, color="#ff0000"))
        
        ax.add_patch(Rectangle(xy=(0, 0), width=leftmargin, height=topmargin, fill=False, color="#00ff00"))
        ax.add_patch(Rectangle(xy=(0, height - bottommargin), width=leftmargin, height=bottommargin, fill=False, color="#00ff00"))
        ax.add_patch(Rectangle(xy=(width - rightmargin, 0), width=rightmargin, height=topmargin, fill=False, color="#00ff00"))
        ax.add_patch(Rectangle(xy=(width - rightmargin, height - bottommargin), width=rightmargin, height=bottommargin, fill=False, color="#00ff00"))
        for i in range(1, args.columns):
            ax.add_patch(Rectangle(xy=(leftmargin + i * (page_width + column_gap) - column_gap, topmargin),
                width=column_gap, height=page_height, fill=False, color="#808000"))

        ax.text(width - rightmargin, height - bottommargin, "x", fontsize=8, ha="right", va="bottom", color="#ff0000")
        
        ax.add_patch(Rectangle(xy=(page_x, 0), width=text_width, height=cell_height, fill=False, color="#0000ff"))

    #fig.savefig("bloom.jpg", pad_inches = 0) # to setup the renderer for text measurement o_O

    month1 = plotter.month
    column = 0

    def print_month_footer(x):
        if args.month_headers:
            if month1 == plotter.month:
                monthtext = calendar.month_name[month1]
            else:
                monthtext = calendar.month_name[month1] + "-" + calendar.month_name[plotter.month]
            ax.text(x, height - bottommargin, monthtext + "\n", fontsize=8, ha="left", va="bottom")
            if column > 1:
                ax.text(x, topmargin, monthtext, fontsize=8, ha="left", va="top")

    def print_page_header():
        ax.text(width - rightmargin, topmargin, "{}".format(1 + page_number),
            fontsize=8, ha="right", va="top")

    print_page_header()

    add_header()

    column_cut_off = n_page
    y = topmargin + header * cell_height
    page_ni = 0
    while plotter.i < len(names):
        ni = plotter.i
        name = names[ni]

        print_month = None
        if args.month_headers and months:
            if months[ni] > plotter.month:
                print_month = (months[ni] - 1) % 12 + 1
                if month1 == 0: month1 = months[ni]
                plotter.month = months[ni]

        new_page = False
        if page_ni >= column_cut_off: new_page = True
        # don't print month in last line with nothing to follow
        if print_month and page_ni >= column_cut_off - 1: new_page = True
        if new_page:
            column += 1
            print(f"column {column}/{args.columns}")
            if column >= args.columns:
                break

            print_month_footer(page_x)
            month1 = plotter.month

            page_x += page_width + column_gap
            y = topmargin + header * cell_height
            add_header()
            page_ni = 0
            skip_ni = 0
            line = Line2D([page_x - column_gap / 2, page_x - column_gap / 2],
                [topmargin + cell_height * header, topmargin + cell_height * (header + n_page)], color = "#808080")
            line.set_clip_on(False)
            ax.add_line(line)

        x = page_x

        if print_month is not None:
            ax.text(x, y + cell_height / 2, calendar.month_name[print_month], fontsize=12,
                    horizontalalignment='left',
                    verticalalignment='center', weight="bold")
            y += cell_height
            page_ni += 1
            skip_ni += 1

        if want_pictures:
            #pic = mpli.imread(f"pics_alternate/{name}.jpg")
            pic = mpli.imread(pictures[ni])
            pic_border_color = "#ffffff40"
        #else:
        #    pic = numpy.array([[(0, 0, 0, 0)]])
        #    pic_border_color = "#00000000"
            pw = pic.shape[1]
            ph = pic.shape[0]
            if triple_pictures:
                offset = (page_ni - skip_ni) % 3
                cs = cell_height * 3
            else:
                offset = 0
                cs = cell_height

            px = x + offset * cs + cs / 2
            py = y + cell_height / 2
            sx = 1
            sy = 1
            if pw > ph:
                sx = pw / ph
            else:
                sy = ph / pw
            if triple_pictures:
                cs -= 5 # gap between pictures
            pw = cs * sx
            ph = cs * sy

            pp = Rectangle((px - cs / 2, py - cs / 2), cs, cs, fill = False, color = pic_border_color)
            ax.add_patch(pp)

            im = ax.imshow(pic, extent = (
                px - pw / 2, px + pw / 2,
                py + ph / 2, py - ph / 2))
            im.set_clip_path(pp)

            x += cs

        note = ""
        scientific = ""
        if args.check_rare:
            sp = state.sl.species_by_name.get(name)
            if sp and sp.rare:
                if sp.rare == "P" or sp.rare == "T" or sp.rare == "E" or sp.rare == "U":
                    note = "$^" + sp.rare + "$"
        tx = x
        if want_pictures: tx += 4
        ax.text(tx, y + cell_height / 2, plot_matplotlib.get_name(name) + note, fontsize=10,
                horizontalalignment='left',
                verticalalignment='bottom')
        if args.scientific:
            sp = state.sl.species_by_name.get(name)
            scientific = " ".join(("$" + x + "$") for x in sp.scientific.split())
            ax.text(tx, y + cell_height, "  " + scientific, fontsize=10,
                horizontalalignment='left',
                verticalalignment='bottom', color="#808080")

        x += text_width

        if args.want_seen == 1:
            b = cell_height / 8
            ax.add_patch(
                Rectangle(xy=(x, y),
                    width = notes_width / 2 - b, height = cell_height - 2,
                    fill = False, color = "#8080ff")
                )
            ax.add_patch(
                Rectangle(xy=(x + notes_width / 2, y),
                    width = notes_width / 2 - b, height = cell_height - 2,
                    fill = False, color = "#8080ff")
                )
            x += notes_width

        if args.want_histogram:
            hh = cell_height - 4
            for week in range(args.w0, args.w0 + args.wn):
                v = weeks[ni][week] / 9
                if v > 0:
                    ax.add_patch(
                        Rectangle(xy=(x + histogram_width * (week - args.w0) / args.wn, y + cell_height - v * hh),
                            width=histogram_width / args.wn, height = hh * v, color = week_color(week, args))
                    )
            ax.add_line(Line2D([x, x + histogram_width], [y + cell_height, y + cell_height], color = "#c0c0c0", zorder = -1))
            x += histogram_width

        y += cell_height
        page_ni += 1
        plotter.i += 1

    if plotter.i == len(names):
        column += 1
        print(f"column {column}/{args.columns}")

    def print_footer():
        def parameterize(text):
            return text.replace("⚘", f"⚘{plotter.n}")

        notes = [x.replace("|", "\n") for x in parameterize(args.footers).split("||")]

        nn = len(notes)
        if pages == 1:
            ax.text(page_width, height - bottommargin, notes[page_number % nn], fontsize = 8, ha = "right", va = "bottom")
        else:
            for c in range(args.columns):
                ax.text(leftmargin + page_width * (1 + c) + column_gap * c, height - bottommargin, notes[c % nn], fontsize=8, ha="right", va="bottom")

        print_month_footer(page_x)

    print_footer()
    return fig


