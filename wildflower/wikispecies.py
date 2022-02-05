import sys
import helpers
import bs4

def retrieve_distribution_states(taxon, ignore_cache=False):
    states = set()
    content = helpers.get3("https://species.wikimedia.org/wiki/", taxon,
        ignore_cache=ignore_cache)
    soup = bs4.BeautifulSoup(content, features="lxml")
    for table in soup.find_all("table"):
          if not table.th: continue
          if not table.th.span: continue
          if table.th.span.text != "Native distribution areas:": continue
          for li in table.td.find_all("li"):
                if li.ul:
                    if li.text.startswith("Introduced into:"):
                        break
                    continue
                # exclude text inside of <span> (sometimes used to gray out invasives)
                for text in li.find_all(text=True, recursive=False):
                    for state in text.split(","):
                        if state.strip():
                            states.add(state.strip())
    return states

class Args:
  quiet=False
  offline=False

def main():
    helpers.args = Args()
    taxons = sys.argv[1:]
    for taxon in taxons:
        states = retrieve_distribution_states(taxon)
        print(states)

if __name__ == "__main__":
    main()
