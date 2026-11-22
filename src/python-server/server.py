# -*- coding: UTF-8 -*-
import os
import sys
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import servUtils.htmx_tpl as hx
import dataUtils.dataService as datServ


HOST = "127.0.0.1"
PORT = 8080

class OpenManulHTTPRequestHandler(SimpleHTTPRequestHandler):
    """自定义请求处理器，添加 UTF-8 编码响应头与基础 MIME 类型支持"""
    def do_GET(self):
        req = urlparse(self.path)
        _path = req.path.lstrip("/")
        _fragment = req.fragment
        _querys = parse_qs(req.query)
        _is_htmx = self.headers.get('Hx-Request') == 'true'
        _split_path = _path.split("/")
        print(_split_path)
        if _split_path[0] == "":
            _split_path[0] = "list"
        
        if _split_path[0] == "image":
            '''image/manul/{imgID}'''
            pic_path = "/".join([om_data_dir, "data", "individuals", _split_path[1], "image", _split_path[2]])
            if not os.path.exists(pic_path):
                pic_path = "/".join([om_serv_dir, "template", "resource", "profile.png"])
            print("image", pic_path)
            with open(pic_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        elif _split_path[0] == "reference":
            '''reference/manul/{ID}/{ref_id}'''
            try:
                # _split_path[1] == "manul"
                manul_id   = _split_path[2]
                ref_id_str = _split_path[3]
                indv = om_database.getIndividualByID(manul_id)
                ref_idx = int(ref_id_str) - 1
                redirection_url = indv["links"][ref_idx]["href"]
                print("reference", redirection_url)
                self.send_response(302)
                self.send_header("Location", redirection_url)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            except:
                self.send_error(404, "Reference not found")
                return
        elif _split_path[0] == "individuals":
            '''/individuals'''
            related_to = _querys.get("related_to", [None])[0]
            if related_to:
                print("individuals", related_to)
                manuls = om_database.getIndividualsRelatedTo(related_to).values()
            else:
                print("individuals", "-all")
                manuls = om_database.getIndividuals().values()
            manul_sections = []
            for manul in manuls:
                manul_section = hx.fmt_card(manul, "zh")
                manul_sections.append(manul_section)
            html_snippet = "".join(manul_sections)
        elif _split_path[0] == "individual":
            manul = om_database.getIndividualByID(_split_path[1])
            zoos = om_database.getZoos()
            if manul:
                print("individual", manul["ID"])
                html_snippet = hx.fmt_info(manul, zoos, "zh")
            else:
                print("individual", "ID not found")
                super().do_GET()
                return
        elif _split_path[0] == "nav":
            nav_title = _split_path[1] if len(_split_path)>1 else "zoo"
            if nav_title == "manul":
                print("nav", "manul")
                manuls = om_database.getIndividuals().values()
                html_snippet = hx.fmt_indiv_nav(manuls, "zh")
            else:
                # /nav/zoo
                print("nav", "zoo")
                zoos = om_database.getZoos().values()
                html_snippet = hx.fmt_zoo_filter(zoos, "zh")
        elif _split_path[0] in ('list', 'view', 'tree', 'map', 'timeline'):
            if _is_htmx:
                print(_split_path[0], "htmx")
                super().do_GET()
                return
            else:
                print(_split_path[0], "page")
                tab = _split_path[0]
                param = _split_path[1] if len(_split_path)>1 else None
                if tab == "view":
                    html_snippet = om_page_template
                    html_snippet = html_snippet.replace("[[tab_title]]", "View")
                    html_snippet = html_snippet.replace("[[aside_htmx_url]]", "/nav/manul")
                    if param:
                        html_snippet = html_snippet.replace("[[article_htmx_url]]", f"/individual/{param}")
                    else:
                        html_snippet = html_snippet.replace("[[article_htmx_url]]", "/individuals")
                elif tab in ('tree', 'map', 'timeline'):
                    html_snippet = f"<p>This is {tab} page</p>"
                else:
                    #list
                    html_snippet = om_page_template
                    html_snippet = html_snippet.replace("[[tab_title]]", "List")
                    html_snippet = html_snippet.replace("[[aside_htmx_url]]", "/nav")
                    html_snippet = html_snippet.replace("[[article_htmx_url]]", "/individuals")
        else:
            if _is_htmx:
                print("otherwise", "htmx")
                html_snippet = ""
                self.send_response(404)
            else:
                print("otherwise", "page")
                if re.search("\.html?$", _split_path[-1].lower()):
                    self.path = "/individuals.html"
                super().do_GET()
                return
        content = html_snippet.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        
    def end_headers(self):
        # 强制针对 HTML、JSON、YAML 等文本资源添加 UTF-8 字符集，防止前端乱码
        if self.path.endswith((".html", ".json", ".yaml", ".yml", ".js", ".css")):
            self.send_header("Content-Type", f"{self.guess_type(self.path)}; charset=utf-8")
        # 允许跨域请求（方便后续前端跨域测试 API 或拉取 openManul 数据）
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def run_server():
    # 确保运行工作目录为当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir+"/../../template")

    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, OpenManulHTTPRequestHandler)
    
        
    global om_serv_dir
    om_serv_dir = os.path.abspath(os.path.join(base_dir, "../.."))
    global om_data_dir
    om_data_dir = os.path.abspath(os.path.join(base_dir, "../../../openManul"))
    
    global om_database
    om_database = datServ.OpenManulDataService(om_data_dir)
    
    global om_page_template
    tpl_path = "/".join([om_serv_dir, "template", "template.html"])
    with open(tpl_path, "r", encoding="utf8") as f:
        om_page_template = f.read()
    
    print(f"om_serv_dir: {om_serv_dir}")
    print(f"om_data_dir: {om_data_dir}")
        
    print(f" site: http://{HOST}:{PORT}")
    print(f" path: {base_dir}")
    print("press Ctrl+C to stop server...\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nserver shutdown...")
        httpd.server_close()
        sys.exit(0)


if __name__ == "__main__":
    run_server()
