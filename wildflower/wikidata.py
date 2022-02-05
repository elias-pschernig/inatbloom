import sys
from qwikidata.sparql import return_sparql_query_results

sparql = """
SELECT ?fna WHERE {
  VALUES ?taxons { %s }
  ?item wdt:P225 ?taxons.
  ?item p:P1727[ps:P1727 ?fna].
}
"""

def main():
    taxons = " ".join(f'"{x}"' for x in sys.argv[1:])
    print(sparql % taxons)
    res = return_sparql_query_results(sparql % taxons)
    for item in res["results"]["bindings"]:
        print(item["fna"]["value"])

if __name__ == "__main__":
    main()
