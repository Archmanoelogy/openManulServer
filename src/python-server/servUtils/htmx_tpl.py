# -*- coding: UTF-8 -*-

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

def fmt_card(indv, lang):
    if "name" not in indv: raise Exception(f"""manul ID: {indv["ID"]} has no name.""")
    htmx = f"""
    <section class="card">
		<a class="bm" name="{indv["ID"]}" hx-get="/individual/{indv["ID"]}" hx-target="article" hx-swap="innerHTML" hx-trigger="click[!event.target.closest('omr')]">
			<div class="card-inner">
				<div class="card-face card-front">
					<img class="card-image" src="image/manul/{indv.get("ImgID","")}.png" alt="">
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
            links_ul.append(f"""<li href=`{lnk.get("href",".")}`>{lnk.get("title","[ref]")}</li>""")
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
            <img src="image/manul/{indv.get("ImgID","")}.png" alt="">
            <span>图源：</span><a href=""\\`{indv.get("ImgLink","")}`>{indv.get("ImgAuthor","")}</a>
        </div>
        <div class="info-detail">{__auto_lang(indv.get("info",{"_":""}), lang)}</div>
        {residents_div}
        <div class="info-relats" hx-get="/individuals?related_to={indv["ID"]}" hx-trigger="load" hx-target="this">
        </div>
        <div class="info-gallery" hx-get="/gallery?id={indv["ID"]}" hx-trigger="load" hx-target="this">
        </div>
        {links_div}
    </section>
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
            <ul>
                {li_list_dom}
            </ul>
        </div>
    </details>
    """
    return(htmx)
