import html

def create(filename, states, columns):
    out = open(filename, "w")
    h = html.Html(lambda x: out.write(x + "\n"))
    h.tag2("!DOCTYPE", html = "")
    h.tag2("meta", charset = "utf8")
    with h.tag("html"):
        with h.tag("head"):
            with h.tag("title"):
                h.content(f"Spring Wildflowers")
            with h.tag("style"):
                h.style("h1", color = "black")
                h.style("td", width = "9%", background = "cornflowerblue")
                h.style("img", **{"max-width": "100%"})
                h.style("a", display = "list-item", color = "#008000", **{
                    "text-decoration": "none",
                    "font-family": "sans-serif",
                    "white-space": "nowrap"
                    })
                h.style("span", **{
                    "white-space": "nowrap",
                    "font-family": "sans-serif"
                    })
                h.style(".container", position = "relative")
                h.style(".dropdown:hover .menu", display = "block")
                h.style(".menu", display = "none",
                    position = "absolute", left = "0px", top = "0px",
                    background = "#c0ff80c0",
                    padding = "0.5em 0.5em 0.5em 1.5em",
                    **{"border-radius": "0.25em",
                        "z-index": "1"})
                h.style("table", **{"border-spacing": "0px"})
        with h.tag("body"):
            with h.tag("h1"):
                h.content("Spring Wildflowers")
            with h.tag("table"):
                for i in range(0, len(states), columns):
                    with h.tag("tr"):
                        for j in range(columns):
                            if j + i < len(states) and states[j + i] != "none":
                                with h.tag("td.dropdown"):
                                    draw_state(h, j + i, states)
                            else:
                                with h.tag("td.dropdown"):
                                    pass
                                
    out.close()

def draw_state(h, i, states):
    
    state = states[i]
    name = state
    title = state

    with h.tag("span"):
        h.content(f"{title}")
    with h.tag("div.container"):
        h.tag2("img", src = f"{name}_out2.png")
        with h.tag("div.menu"):
            with h.tag("a", href = f"{name}2.jpg"):
                h.content("unique flowers")
            with h.tag("a", href = f"{name}_lab2.jpg"):
                h.content("unique with labels")
            with h.tag("a", href = f"{name}1.jpg"):
                h.content("most flowers")
            with h.tag("a", href = f"{name}_lab1.jpg"):
                h.content("most with labels")

    
