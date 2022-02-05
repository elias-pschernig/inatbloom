from matplotlib import pyplot
from shapely.geometry import LineString
from descartes import PolygonPatch
from matplotlib import image as mpli
import matplotlib.patheffects as patheffects
import matplotlib.transforms as transforms
import subprocess
import math
import copy

mercator_f0 = None
mercator_y0 = None
# Multiplies lon values to sort of keep aspect relative to lat...
# this mostly works but of course the returned longitude values make no
# more sense
def reset_mercator():
    global mercator_f0
    mercator_f0 = None

def get_radius(c):
    cx = 0
    cy = 0
    n = 0
    for x, y in c[0]:
        cx += x
        cy += y
        n += 1
    if n == 0:
        return 0
    cx /= n
    cy /= n
    maxd = 0
    for x, y in c[0]:
        d = ((x - cx) * (x - cx) + (y - cy) * (y - cy)) ** 0.5
        if d > maxd:
            maxd = d
    return maxd

def fix_gps(pos, center_lon):
    global mercator_f0, mercator_y0
    lon, lat = pos
    lat = float(lat)
    lon = float(lon)
    x = lon
    y = lat
    if x > 0 and center_lon < 0:
        x -= 360
    elif x < 0 and center_lon > 0:
        x += 360
    if mercator_f0 is None:
        mercator_f0 = math.cos(lat * math.pi / 180)
        mercator_y0 = y
    y = mercator_y0 + (y - mercator_y0) / mercator_f0
    return x, y

def fix_coordinates(c, center_lon):
    for i in range(len(c)):
        c[i] = [fix_gps(p, center_lon) for p in c[i]]
        
def update_bounds(c, bounds):
    for i in range(len(c)):
        for p in c[i]:
            if bounds[0] is None or p[0] < bounds[0]: bounds[0] = p[0]
            if bounds[1] is None or p[1] < bounds[1]: bounds[1] = p[1]
            if bounds[2] is None or p[0] > bounds[2]: bounds[2] = p[0]
            if bounds[3] is None or p[1] > bounds[3]: bounds[3] = p[1]

def get_extent(pic, geo):
    if geo["type"] == "MultiPolygon":
        xy = []
        for p in geo["coordinates"]:
            xy += p[0]
    else:
        xy = geo["coordinates"][0]
    bx1 = min([x[0] for x in xy])
    bx2 = max([x[0] for x in xy])
    by1 = min([x[1] for x in xy])
    by2 = max([x[1] for x in xy])
    w = pic.shape[1]
    h = pic.shape[0]
    bw = bx2 - bx1
    bh = by2 - by1
    cx = bx1 + bw / 2
    cy = by1 + bh / 2

    s = bw / w

    if h * s < bh:
        s = bh / h

    return cx - w * s / 2, cx + w * s / 2, cy - h * s / 2, cy + h * s / 2
    #return cx - w * s / 2, cx + w * s / 2, by2 - h * s, by2

def overlap(b1, b2):
    return b1[0] < b2[2] and b1[1] < b2[3] and b2[0] < b1[2] and b2[1] < b1[3]

def do_plot(data, title, subtitle, name, want_names = False,
        want_labels = False, want_icon = False, args = {}):
    print("plotting", title, name, args["size"])
    background = args["background_color"]
    ignore_islands = float(args.get("ignore_islands", 0.01))
    thickness = float(args["thickness"])
    font_size_title = 40
    font_size_subtitle = 15
    font_size_label = 5
    dpi = 240

    data_bounds = [None, None, None, None]

    w_, h_ = args["size"].split("x")

    if want_icon:
        thickness = 0.1
        w_, h_ = args["outline_size"].split("x")
    w_pixel = int(w_)
    h_pixel = int(h_)
    w_inch = w_pixel / dpi
    h_inch = h_pixel / dpi
    fig = pyplot.figure(None, figsize=(w_inch, h_inch), dpi = dpi, facecolor = background)
    fig.clf()
    if want_icon > 0:
        pyplot.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0)
    else:
        b = font_size_subtitle / 72
        b_top = b + (font_size_subtitle + font_size_title) / 72
        pyplot.subplots_adjust(top = (h_inch - b_top) / h_inch, bottom = b / h_inch,
            right = (w_inch - b) / w_inch, left = b / w_inch)
    #ax = fig.add_axes([0.15, 0.01, 0.7, 0.98])
    #pyplot.margins(0, 0)
    ax = fig.gca()
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    #pyplot.xticks([])
    #pyplot.yticks([])
    ax.axis('off')
    ax.set(facecolor = background)

    reset_mercator()
    labels = []

    i = 0
    for region, species, count in data:
        place = region.place["results"][0]
        geo = copy.deepcopy(place['geometry_geojson'])

        y, x = place["location"].split(",")
        center = float(x)
        x, y = fix_gps((x, y), center)

        if geo["type"] == "MultiPolygon":
            ok = []
            not_ok = []
            for poly in geo["coordinates"]:
                fix_coordinates(poly, center)
                r = get_radius(poly)
                if r > ignore_islands:
                    ok.append(poly)
                    update_bounds(poly, data_bounds)
                else:
                    not_ok.append((r, poly))
            if not ok:
                biggest = max(not_ok)
                ok = [biggest[1]]
            geo["coordinates"] = ok
        else:
            fix_coordinates(geo["coordinates"], center)
            update_bounds(geo["coordinates"], data_bounds)

        pp = PolygonPatch(geo, fill = False, ec = args["foreground_color"],
            alpha=1.0, zorder=1, linewidth = thickness)
        ax.add_patch(pp)

        pic = mpli.imread(species.pic)

        #print(region.name)
        #print(geo)
        ax.imshow(pic, extent = get_extent(pic, geo)).set_clip_path(pp)

        i += 1

        if want_labels and not want_icon:
            species_name = species.name
            if species.translated:
                species_name = species.translated
            text = place["name"] + "\n" + get_name(species_name)
            labels.append((x, y, text))

    #ax.set_aspect(1)
    #ax.autoscale(tight = False) wrongly uses clipped pictures
    ax.set_xlim((data_bounds[0], data_bounds[2]))
    ax.set_ylim((data_bounds[1], data_bounds[3]))

    already = []
    for x, y, text in labels:
        trans = ax.transData + transforms.ScaledTranslation(0, font_size_label / 72, fig.dpi_scale_trans)
        x2, y2 = ax.transData.inverted().transform(trans.transform((x, y)))
        bs = (y2 - y) * 0.75
        bb = (x - bs * 3, y - bs, x + bs * 3, y + bs, text)
        updown = 1
        amount = 1
        for t in range(5):
            collided = False
            for a in already:
                if overlap(a, bb):
                    collided = True
                    break
            if not collided:
                break
            y += bs * updown * amount
            updown = -updown
            amount += 1
            bb = (x - bs * 3, y - bs, x + bs * 3, y + bs, text)
        already.append(bb)
        #x3, y3 = fig.dpi_scale_trans.inverted().transform((x2, y2))
        #print(x, y, x2, y2, x3, y3)
        txt = ax.text(x, y, text, ha = "center", va = "center", color = "#ffffff", alpha = 0.5, size = font_size_label,
            transform = ax.transData)
        txt.set_path_effects([patheffects.withStroke(linewidth = 2, foreground='#000000')])

    if not want_icon:
        trans = ax.transAxes + transforms.ScaledTranslation(0, font_size_subtitle / 72, fig.dpi_scale_trans)
        ax.text(0, 1, title, va = "bottom", size = font_size_title, transform = trans)
        ax.text(0, 1, subtitle, va = "bottom", size = font_size_subtitle, transform = ax.transAxes, style = "italic")
        ax.text(1, 0, "single pictures are all www.iNaturalist.org species default icons with their respective copyrights",
            ha = "right", va = "top", size = 8, transform = ax.transAxes, style = "italic")

    if want_names and not want_icon:
        i = 0
        y = 1
        x = -0.01
        ha = "right"
        names = sorted(list(set([get_name(x[1].name) for x in data])))
        for fname in names:
            if i == 44:
                ha = "left"
                y = 1
                x = 1.01

            y -= 0.022
            i += 1
            ax.text(x, y, fname, size = "medium", transform = ax.transAxes, ha = ha)

    if not want_icon:
        fig.savefig(name, pad_inches = 0)
        subprocess.run(("convert", name, "-trim", "-bordercolor", background, "-border", "10", name[:-4] + ".jpg"))
    else:
        fig.savefig(name, pad_inches = 0, transparent = True)
    
    pyplot.close()

def get_name(s):
    x = s.lower()

    for i in range(len(x)):
        if i == 0 or x[i - 1] == " ":
            x = x[:i] + x[i].upper() + x[i + 1:]
    return x
