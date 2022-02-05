import urllib.parse
import json
try:
    import odnr_rare
except ModuleNotFoundError:
    from . import odnr_rare

def first_week_for_month(m):
    # month 0 and week 0 are both invalid
    return [0, 1, 5, 9, 14, 18, 23, 27, 31, 36, 40, 44, 49, 53][m]

def read_months(args):
    months = [int(x) for x in args.months.split(",")]
    args.m0 = min(months)
    args.mn = max(months) - args.m0 + 2
    if args.m0 + args.mn > 13:
        args.mn = 13 - args.m0
    args.w0 = first_week_for_month(args.m0)
    args.wn = first_week_for_month(args.m0 + args.mn - 1) - args.w0 + 2
    if args.w0 + args.wn > 53:
        args.wn = 53 - args.w0
    print(f"months: {args.m0}+{args.mn} weeks: {args.w0}+{args.wn}")

include_taxons = {
    47125, # Angiospermae (flowering plants)
    }
# these can also be parent taxons
exclude_taxons = {
    # not flowers (trees, sedges, ...)
    53350, # Aesculus (buckeye)
    47733, # Oleaceae (ash)
    47194, # Cornaceae (dogwood)
    48801, # Cercis (redbud)
    47853, # Fagales (beech)
    47375, # Pinales (pine)
    50899, # Annonaceae (pawpaw)
    49664, # Platanus (sycamore)
    47727, # Acer (maple)
    53581, # Magnoliaceae (magnolia)
    53548, # Ulmaceae (elm)
    48874, # Anacardiaceae (sumac)
    52469, # Hydrangeaceae (hydrangea)
    47162, # Poales (grass)
    781703, # Viburnaceae (viburnum)
    47567, # Salicaceae (willow)
    117430, # Cladrastis-kentukea (yellow-wood)
    532720, # Nyssaceae (black gum)
    919966, # Oxydendreae (sourwood)
    48808, # Laurales (sassafras)
    61874, # Styracaceae (silverbells)
    132768, # Chamaedaphne (leatherleaf)
    49398, # Kalmia (lorel)
    53855, # Aquifoliaceae (holly)
    47544, # Rubus (blackberry)
    47131, # Grossulariaceae (currant)
    49487, # rhododendron
    50314, # leatherwood
    60747, # greenbrier
    71280, # Crossosomatales (bladdernut)
    746912, # Robinieae (black locust)
    56091, # Morus (mulberry)
    64539, # Celastrus (bittersweet)
    117432, # Euonymus-atropurpureus
    51971, # hamamelis
    48498, # Gleditsia
    71434, # Altingiaceae (sweetgum tree)
    54858, # Celtis
    54812, # Rhamnus (buckthorn)
    54837, # Zanthoxylum (prickly ash)
    910649, # Catalpeae (catalpa)
    71506, # Ebenaceae (persimmon)
    502646, # Lemnoideae (duckweed)
    50624, # Ptelea (hoptree)
    52728, # Cephalanthus (buttonbush)
    48211, # Clethra (shrubs)
    924978, # Tilioideae (linden tree)
    82813, # Aralia-spinosa (devil's walking stick, a tree)
    47351, # Prunus (cherry)
    71291, # Vitales (grapes)
    723302, # Maleae (apple)
    }

# these have to be species level and are filtered out at the end
default_remove = {
    # mostly these are mistakenly considered native in Ohio by inaturalist
    # unfortunately it's a long list and not sure how to automate, e.g.
    # if using this for another state
    57969, # Acton Brittlebush
    54531, # Cuckooflower
    122866, # domesticated winter squash
    76541, # Cucurbita-pepo (cultivated winter sqash)
    164369, # Krigia-cespitosa
    125103, # Houstonia micrantha
    67379, # Lupinus-latifolius
    77264, # Geranium-viscosissimum
    57793, # Gilia-capitata
    81320, # Ranunculus aquatilis
    57457, # Stachys-palustris
    163779, # Hieracium-fendleri
    78090, # Mollugo verticillata
    165891, # Opuntia-macrorhiza
    122587, # Monarda-citriodora
    79492, # Verbena-pulchella
    68218, # Saxifraga-mertensiana
    57983, # Helianthus-annuus
    79078, # Sida-spinosa
    163763, # Hibiscus-coccineus
    131581, # Strophostyles-umbellata
    127941, # Callirhoe-involucrata
    51813, # Oenothera-elata
    77398, # Heterotheca subaxillaris
    60983, # Arabis-blepharophylla (endemic to california)
    48384, # Heuchera-sanguinea (not native to Ohio)
    51266, # Wisteria frutescens
    59936, # Nemophila-maculata (endemic to California)
    62218, # Camassia leichtlinii
    123634, # Trillium cuneatum
    50648, # Nemophila menziesii
    78414, # Penstemon procerus
    160370, # Chaerophyllum tainturieri
    50876, # Layia platyglossa
    163181, # Galium lanceolatum
    132602, # Penstemon albidus (not in ohio)
    55410, # wild radish
    59549, # Large-leaved Lupine
    128717, # Coral Bean
    75605, # madwort (native to Europe)
    58331, # Datura wrightii (not native in ohio)
    48625, # Oenothera-speciosa (not native in ohio)
    57481, # Calystegia sepium (bindweed, not in ohio)
    55854, # Datura stramonium (jimsonwood, not in ohio)
    76765, # Eclipta prostrata  (false daisy, not in ohio)
    77495, # Ipomoea-hederacea
    52344, # Ipomoea-purpurea
    51884, # Urtica-dioica
    57858, # Veronica-anagallis-aquatica
    50316, # Allegheny spurge
    }

default_add = {
    238944, # Trollius-laxus-laxus, sub-species not set to native even though species is native (inat bug?)
    241025, # Heuchera-parviflora-parviflora, same ^
    55925, # Geranium-robertianum (mistakenly introduced for Ohio on inaturalist)
}

class Parameters:
    keys = ["species", "exclude", "include", "remove", "places",
        "columns", "columnsize", "pictures", "months", "title",
        "footers", "nocachefor", "rename", "extra", "nocache",
        "inatquery", "check_rare", "check_native", "check_wikispecies",
        "maybe_introduced",
        "min_count", "remove_file"]

    pics = """76005=https://inaturalist-open-data.s3.amazonaws.com/photos/68298883/large.jpeg?1587691263
170114=https://inaturalist-open-data.s3.amazonaws.com/photos/9633323/large.jpg?1502243473"""
    defaults = ["47125",
        ",".join(sorted([str(x) for x in exclude_taxons])),
        ",".join(sorted([str(x) for x in default_add])),
        ",".join(sorted([str(x) for x in default_remove])), "31",
        "3", "32", pics, "1,2,3,4,5,6,7,8,9,10,11,12", "Native Wildflowers of Ohio",
        "⚘||$potentially^P$ $threatened^T$ $endangered^E$||" +\
        "data/pictures from https://iNaturalist.org", "", "", "term_id=12&term_value_id=13",
        "",
        "", "", "", "",
        "",
        "0", ""]

    def __init__(self):
        self.inat_links = False
        self.first_header_only = False

    @staticmethod
    def default_for(x):
        for i in range(len(Parameters.keys)):
            if Parameters.keys[i] == x:
                return Parameters.defaults[i]
        return None

    def from_query(self, document):
        for i in range(len(Parameters.keys)):
            key = Parameters.keys[i]
            d = Parameters.defaults[i]
            setattr(self, key, document.query.getfirst(key, d))

    def fix_arguments(self, args):
        for i in range(len(Parameters.keys)):
            key = Parameters.keys[i]
            d = Parameters.defaults[i]
            v = vars(args).get(key)
            if v is None:
                setattr(args, key, d)
        args.columns = int(args.columns)
        args.columnsize = int(args.columnsize)
        args.check_rare = args.check_rare == "1"
        args.check_native = args.check_native == "1"
        args.maybe_introduced = args.maybe_introduced == "1"
        args.check_wikispecies = args.check_wikispecies == "1"

    def from_input(self, document):
        for key in Parameters.keys:
            try:
                setattr(self, key, document["edit_" + key].value)
            except KeyError:
                setattr(self, key, Parameters.default_for(key))

    def to_input(p, document):
        for key in Parameters.keys:
            try:
                document["edit_" + key].value = getattr(p, key)
            except KeyError:
                pass

    def get_query_string(self):
        c = []
        upq = urllib.parse.quote
        for key in Parameters.keys:
            c.append(key + "=" + upq(getattr(self, key)))
        return "&".join(c)

class Downloader:
    def download_pages(self, url, ignore_cache, on_success):
        self.page = 1
        self.results = []
        def on_page(j):
            self.results.extend(j["results"])
            if len(j["results"]) > 0 and len(self.results) < j["total_results"]:
                self.page += 1
                self.download(url + f"&page={self.page}", ignore_cache,
                    on_page)
                return
            on_success(self.results)
        self.download(url, ignore_cache, on_page)

class Species:
    def __init__(self):
        self.id = None
        self.name = None
            
class SpeciesList:
    species_counts = "https://api.inaturalist.org/v1/observations/species_counts"
    histogram = "https://api.inaturalist.org/v1/observations/histogram"

    def __init__(self):
        self.species_by_id = {}
        self.species_by_name = {}
        self.found = {}
        self.renamed = {}
    
    def from_parameters(self, args):
        self.args = args
        read_months(args)

        self.ic = args.nocache or args.nocachefor
        #print(self.ic)

        c = []
        c += ["place_id=" + args.places]
        c += ["month=" + args.months]
        c += ["taxon_id=" + args.species]
        c += [args.extra]

        # if we limit to species it ignores and subspecies etc.
        c += ["rank=species,subspecies,variety,form,hybrid"]
        
        c += ["verifiable=true"]
        exclude = args.exclude
        # filter them out later instead, so the query isn't so long (?)
        #if args.remove:
        #    exclude += "," + args.remove
        c += ["without_taxon_id=" + exclude]

        self.url = self.species_counts + "?" + ("&".join(c))
        self.url += args.inatquery

        self.rare = {}
        if args.check_rare:
            self.rare = odnr_rare.rare

        if args.check_native or args.maybe_introduced:
            args.downloader.download_pages(self.url, self.ic, self.on_success1)
        else:
            args.downloader.download_pages(self.url + "&native=true", self.ic, self.on_success4)

    def from_saved(self, saved):
        self.result = saved["names"], saved["weeks"], saved["pictures"]
        self.bloom_start = saved["bloom_start"]
        self.args = Parameters()
        for k, v in saved["args"].items():
            setattr(self.args, k, v)
        read_months(self.args)

        self.species_by_name = {}
        self.species_by_id = {}
        self.species = []
        self.ids = saved["ids"]
        i = 0
        for name in saved["names"]:
            s = Species()
            s.id = saved["ids"][i]
            s.name = name
            s.scientific = saved["scientific"][i]
            s.rare = saved["rare"][i]
            if name in self.species_by_name:
                print("{} ({}) is duplicate".format(name, s.id))
            self.species_by_name[name] = s
            if s.id in self.species_by_id:
                print("{} ({}) is duplicate".format(s.id, name))
            self.species_by_id[s.id] = s
            self.species.append(s)
            i += 1

    def to_saved(self):
        argsd = {}
        for k in Parameters.keys:
            argsd[k] = getattr(self.args, k)
        names, weeks, pictures = self.result
        ids = []
        scientific = []
        rare = []
        for tid in self.ids:
            s = self.species_by_id[tid]
            name = s.name
            ids.append(s.id)
            scientific.append(s.scientific)
            rare.append(s.rare)
        j = {"names": names, "weeks": weeks, "pictures": pictures, "args": argsd,
            "ids": ids, "scientific": scientific, "rare": rare, "bloom_start": self.bloom_start}
        return j

    def on_success1(self, results):
        self.all_results = results
        self.args.downloader.download_pages(self.url + "&native=true", self.ic, self.on_success2)

    def on_success2(self, results):
        self.native_results = results
        self.args.downloader.download_pages(self.url + "&introduced=true", self.ic, self.on_success3)

    def on_success3(self, results):
        self.introduced_results = results
        self.on_success_()

    def on_success4(self, results):
        self.all_results = self.native_results = results
        self.introduced_results = []
        self.on_success_()

    def on_success_(self):
        if self.args.include:
            self.args.downloader.download(self.species_counts + "?taxon_id=" + self.args.include,
                self.ic, lambda j2:
                    self.on_have_species(j2["results"]))
        else:
            self.on_have_species([])

    def on_have_species(self, add_results):
        args = self.args
        args.min_count = int(args.min_count)

        print(f"found {len(self.all_results)} species, {len(self.native_results)} are native " +
            f"and {len(self.introduced_results)} are introduced")

        debugnc = args.nocachefor.split(",")

        native_set = {str(r["taxon"]["id"]) for r in self.native_results}
        introduced_set = {str(r["taxon"]["id"]) for r in self.introduced_results}
        remove_set = set(args.remove.split(","))

        filter_out = set()
        if args.remove_file:
            filter_out = set(open(args.remove_file).read().splitlines())

        introduced_taxa = []
        results = []
        for r in self.all_results:
            taxon = str(r["taxon"]["id"])
            scientific = r["taxon"]["name"]
            if taxon in remove_set:
                continue
            if scientific in filter_out:
                print("filtered out", scientific)
                continue
            if args.maybe_introduced:
                if taxon in native_set or taxon in introduced_set:
                    continue
                results.append(r)
                introduced_taxa.append(r)
                continue
            if taxon in introduced_set:
                continue
            if taxon not in native_set or args.check_wikispecies:
                native = False
                name = r["taxon"].get("preferred_common_name", scientific)
                if args.places == "31":
                    states = wikispecies.retrieve_distribution_states(scientific)
                    if "Ohio" in states:
                        native = True
                        print(f"{name} ({scientific}, {taxon}) has unknown establishment, KEEPING")
                if not native:
                    introduced_taxa.append(r)
                    if taxon not in native_set:
                        if taxon in debugnc:
                            print(f"{name} ({scientific}, {taxon}) has unknown establishment, removing")
                        continue
                    else:
                        print(f"{name} ({scientific}, {taxon}) does not pass wikispecies test")
            results.append(r)

        if introduced_taxa:
            inat_ids = []
            introduced = open("introduced.txt", "w")
            for r in introduced_taxa:
                scientific = r["taxon"]["name"]
                inat_ids.append(str(r["taxon"]["id"]))
                introduced.write(f"{scientific}\n")
            introduced.write(",".join(inat_ids))
            introduced.write("\n")
            introduced.close()

        results.extend(add_results)

        self.species = []
        print(len(results), "flowers found")
        if debugnc[0] != "":
            print(f"no cache for {debugnc}")
        for result in results:
            taxon = result["taxon"]
            name = taxon.get("preferred_common_name", taxon["name"])

            s = Species()
            s.name = name
            s.id = str(taxon["id"])
            s.scientific = taxon["name"]
            s.count = int(result["count"])
            if args.min_count:
                if s.count < args.min_count:
                    print(f"count {s.count} < {args.min_count}, skipping")
                    continue

            if s.id in debugnc:
                print("Found", s.id)
                debugnc.remove(s.id)

            if s.id not in self.species_by_id:
                self.species_by_id[s.id] = s
                self.species_by_name[s.name] = s
                self.species.append(s)
            else:
                print(f"{s.name} ({s.id}) was duplicate")
            s.taxon = taxon

            s.histogram_flowering = None

        for d in debugnc:
            if d:
                print(f"{d} was not included")

        self.workers = self.species[:]
        if args.extra == "":
            for s in self.workers:
                s.flowers_per_week = {}
                s.in_season = True
            self.have_histograms()
        else:
            self.work()

    def work(self):
        args = self.args
        if not self.workers:
            self.have_histograms()
            return
        s = self.workers.pop()

        args.downloader.progress(False, (len(self.species) - len(self.workers)) / len(self.species))

        ic = args.nocache or s.id in args.nocachefor.split(",")

        # note: we do not apply args.extra here, as that normally
        # already has the term_id=12&term_value_id=13 which we always
        # need here
        args.downloader.download(self.histogram + "?" +
            f"place_id={args.places}&"
            f"taxon_id={s.id}&"
            f"term_id=12&"
            f"term_value_id=13&"
            f"date_field=observed&"
            f"interval=week_of_year", ic, lambda j: self.worker_done(s, j))

    def worker_done(self, s, j):
        s.flowers_per_week = {int(k):v for k, v in j["results"]["week_of_year"].items()}
        self.mark_season_flower(s)
        self.work()

    def mark_season_flower(self, s):
        args = self.args
        s.in_season_count = 0
        s.out_season_count = 0
        for week in range(53):
            v = s.flowers_per_week.get(week, 0)
            if week >= args.w0 and week < args.w0 + args.wn - 1:
                s.in_season_count += v
            else:
                s.out_season_count += v
        s.in_season = s.in_season_count >= s.out_season_count

    def have_histograms(self):
        args = self.args
        def flowers_per_week(s):
            h = []
            for week in range(54):
                v = s.flowers_per_week.get(week, 0)
                if v > 9: v = 9
                h.append(v)
            return h

        alternate = {}
        for row in args.pictures.splitlines():
            k, v = row.split("=", maxsplit = 1)
            alternate[str(k)] = v

        for name in args.rename.splitlines():
            if not name: continue
            sid, name2 = name.split("=")
            name = self.species_by_id[sid].name
            self.renamed[name] = name2

        ns = 0
        ids = []
        names = []
        weeks = []
        pictures = []
        bloom_start = []

        def weighted_bloom_time(x):
            fpw = flowers_per_week(x)
            m = max(fpw)
            for i in range(len(fpw)):
                if fpw[i] == 0: continue
                if fpw[i] < m // 2: continue
                return i
            if args.extra != "":
                print(f"no bloom time for {x.id}")
            return 0

        for s in self.species:
            s.weighted_bloom_time = weighted_bloom_time(s)
            s.rare = ""
            if s.scientific in self.rare:
                s.rare = self.rare[s.scientific]
        
        for s in sorted(self.species, key = lambda x: x.weighted_bloom_time):
            if not s.in_season:
                ns += 1
                print(f"Skipping {s.name} {s.in_season_count} < {s.out_season_count}")
                continue
            if s.id in args.nocachefor.split(","):
                print(f"Keeping {s.name} {s.in_season_count} >= {s.out_season_count}")
            names.append(s.name)
            ids.append(s.id)
            h = flowers_per_week(s)
            weeks.append(h)
            url = None
            photo = s.taxon["default_photo"]
            if photo:
                url = photo.get("medium_url", None)
            if s.id in alternate:
                url = alternate[s.id]
            pictures.append(url)
            bloom_start.append(s.weighted_bloom_time)

        nr = len(args.remove.split(","))
        na = len(args.include.split(","))
        print(f"Using {len(names)} flowers for list ({ns} skipped, {nr} removed, {na} added).")

        self.result = names, weeks, pictures
        self.ids = ids
        self.bloom_start = bloom_start
        
        args.downloader.progress(True, 1)

        #list_plot.plot(names, weeks, pictures, args)

    def capitalize(self, s):
        if s in self.renamed:
            s = self.renamed[s]

        x = s.lower()

        for i in range(len(x)):
            if i == 0 or x[i - 1] == " ":
                x = x[:i] + x[i].upper() + x[i + 1:]
        return x
 
