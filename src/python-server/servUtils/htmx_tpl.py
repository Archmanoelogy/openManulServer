# -*- coding: UTF-8 -*-
from html import escape

def __auto_lang(desc, lang):
    if type(desc)==str:
        return(desc)
    elif type(desc)==dict:
        if lang in desc:
            return(desc[lang])
        else:
            return(list(desc.values())[0])
    else:
        raise Exception(f"language format error: dict or str expected but {type(desc)} found")
        
def __lifetime(desc):
    if 'year_1' in desc:
        if 'year_2' in desc:
            return(f"{desc['year_1']} - {desc['year_2']}")
        else:
            return(f"{desc['year_1']} - ")
    else:
        if 'year_2' in desc:
            return(f"? - {desc['year_2']}")
        else:
            return(f"")

def fmt_card(indv, tab, lang):
    if "name" not in indv: raise Exception(f"""manul ID: {indv["ID"]} has no name.""")
    htmx = f"""
    <section class="card">
        <a class="bm" name="{indv["ID"]}" href="/{tab}/{indv["ID"]}">
            <div class="card-inner">
                <div class="card-face card-front">
                    <img class="card-image" src="/image/manul/{indv.get("ImgID","")}.png" alt="">
                    <div class="card-overlay">
                        <h2 class="card-title">{__auto_lang(indv["name"], lang)}</h2>
                        <p class="card-description">{__lifetime(indv)}</p>
                    </div>
                </div>
                <div class="card-face card-back">
                    <h2 class="card-title">{__auto_lang(indv["name"], lang)}</h2>
                    <p class="card-description">{__auto_lang(indv.get("info",{"_":""}), lang)}</p>
                </div>
            </div>
        </a>
    </section>
    """
    return(htmx)

def fmt_gallery(img, lang):
    htmx = f"""
    <section class="card">
        <a class="bm" name="{img["ImgID"]}" href="{img["link"]}">
            <div class="card-inner">
                <div class="card-face card-front">
                    <img class="card-image" src="/image/manul/{img["ImgID"]}.png" alt="">
                    <div class="card-overlay">
                        <h2 class="card-title"></h2>
                        <p class="card-description"></p>
                    </div>
                </div>
                <div class="card-face card-back">
                    <h2 class="card-title">{img.get("author", "")}</h2>
                    <p class="card-description">{img.get("date", "")}</p>
                </div>
            </div>
        </a>
    </section>
    """
    return(htmx)



def fmt_info(indv, zoos, lang):
    if "name" not in indv: raise Exception(f"""manul ID: {indv["ID"]} has no name.""")
    alias = indv.get("alias")
    if type(alias) == dict:
        alias_items = []
        for k in alias:
            alias_items += alias[k]
        alias_ul = [u"<li>%s</li>"%(item,) for item in alias_items]
        alias_div = f"""
        <div class="info-alias">
            <span>昵称：</span>
            <ul>{u"".join(alias_ul)}</ul>
        </div>
        """
    else:
        alias_div = u""
    
    residents = indv.get("residents")
    if type(residents) == list:
        residents_ul = []
        for place in residents:
            if "nature" in place:
                residents_ul.append(f"""<li><a class="info-nature"><span>{__auto_lang(place["nature"], lang)}</span><span>{place["time"]}</span></a></li>""")
            elif "zoo" in place:
                zooID = place["zoo"]
                if zooID not in zoos:
                    raise Exception(u"Zoo ID Not Found.")
                zoo_name = __auto_lang(zoos[zooID]["name"], lang)
                residents_ul.append(f"""<li><a class="info-zoo"><span>{zoo_name}</span><span>{place["time"]}</span></a></li>""") #zoos[zooID] needed
            else:
                pass
        residents_div = f"""
        <div class="info-residents">
            <span>旅居：</span>
            <ul>{u"".join(residents_ul)}</ul>
        </div>
        """
    else:
        residents_div = u""
    
    links = indv.get("links")
    if type(links) == list:
        links_ul = []
        for lnk in links:
            links_ul.append(f"""<li><a  href="{escape(lnk.get("href","."))}">{lnk.get("title","[ref]")}</a></li>""")
        links_div = f"""
        <div class="info-links">
            <span>链接：</span>
            <ul>{u"".join(links_ul)}</ul>
        </div>
        """
    else:
        links_div = u""
        
    htmx = f"""
    <section class="info">
        <h2 class="info-title">{__auto_lang(indv["name"], lang)}</h2>
        <p class="info-year">{__lifetime(indv)}</p>
        {alias_div}
        <div class="info-image">
            <img src="/image/manul/{indv.get("ImgID","")}.png" alt="">
            <span>图源：</span><a href="{escape(indv.get("ImgLink",""))}">{indv.get("ImgAuthor","")}</a>
        </div>
		<a class="bm" name="{indv["ID"]}">
        <div class="info-detail">{__auto_lang(indv.get("info",{"_":""}), lang)}</div>
		</a>
        {residents_div}
        <div class="info-relats" hx-get="/tree/{indv["ID"]}" hx-trigger="load" hx-target="this">
        </div>
        <div class="info-gallery" hx-get="/gallery?id={indv["ID"]}" hx-trigger="load" hx-target="this">
        </div>
        {links_div}
    </section>
    """
    return(htmx)

def fmt_tree(nodes, links, manuls, lang):
    ncol = max([x[1] for x in nodes]) + 1
    nrow = max([x[2] for x in nodes]) + 1
    
    sections = []
    for node in nodes:
        manul_id = node[0]
        x = node[1]
        y = node[2]
        indv = manuls[manul_id]
        section = fmt_card(indv, "tree", lang)
        section = section.replace("""<section class="card">""", f"""<section class="card" style="--x:{x};--y:{y};">""")
        sections.append(section)
    
    paths = []
    for link in links:
        rr = 0.075
        x0, y0 = link[0:2]
        x1, y1 = link[2:4]
        yh = max(y0, y1) - 0.5
        xd = 1 if x1>x0 else -1 if x1<x0 else 0
        yd = 1 if y1>y0 else -1 if y1<y0 else 0
        path = f"""<path d="M{x0},{y0} L{x0},{yh-yd*rr} Q{x0},{yh},{x0+xd*rr},{yh} L{x1-xd*rr},{yh} Q{x1},{yh},{x1},{yh+yd*rr} L{x1},{y1}"></path>"""
        paths.append(path)
    
    htmx = f"""
    <div class="treeview" style="--ncol:{ncol};--nrow:{nrow};">
    {"\n".join(sections)}
    <svg viewbox="-0.5 -0.5 {ncol} {nrow}">
    {"\n".join(paths)}
    </svg>
    </div>
    """
    return(htmx)

def fmt_zoo_filter(zoos, lang):
    li_list = []
    for zoo in zoos:
        li_list.append(f"""
                    <li><a href="javascript:void(0)" name="{zoo["ID"]}" onclick="nav_toggle(this)">{__auto_lang(zoo["name"], lang)}</a></li>
        """)
    li_list_dom = "".join(li_list)
    title = u"动物园列表"
    htmx = f"""
    <details class="nav-group" open>
        <summary>
            <h2>{title}</h2>
            <span class="summary-actions">
                <button type="button" class="summary-btn" title="Select all" onclick="nav_selectAll(this, event)"><i class="fa fa-check-square-o"></i></button>
                <button type="button" class="summary-btn" title="Deselect all" onclick="nav_deselectAll(this, event)"><i class="fa fa-square-o"></i></button>
                <i class="fa fa-chevron-down toggle-icon"></i>
            </span>
        </summary>
        <div class="collapsible-wrapper">
            <ul class="zoo-filter">
                {li_list_dom}
            </ul>
        </div>
    </details>
    """
    return(htmx)
    
def fmt_indiv_nav(manuls, tab, lang):
    li_group = {}
    li_list = []
    manul_ids = list(manuls)
    manul_ids.sort(key=lambda x:x.get("ID",""))
    for manul in manul_ids:
        group_title = manul["ID"][0]
        year_1 = manul.get("year_1", None)
        year_sub = ", "+year_1[:4] if year_1 else ""
        li_dom = f"""
                    <li><a href="/{tab}/{manul["ID"]}" name="{manul["ID"]}">{__auto_lang(manul["name"], lang)+year_sub}</a></li>
        """
        li_group[group_title] = li_group.get(group_title, []) + [li_dom]
    li_group_doms = []
    sorted_title = list(li_group.keys())
    sorted_title.sort()
    for group_title in sorted_title:
        li_list_dom = "\n".join(li_group[group_title])
        li_group_doms.append(f"""
        <details class="nav-group" open>
            <summary>
                <h2>{group_title}</h2>
            </summary>
            <div class="collapsible-wrapper">
                <ul class="manul">
                    {li_list_dom}
                </ul>
            </div>
        </details>
        """)
    return("\n".join(li_group_doms))
