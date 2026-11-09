# -*- coding: UTF-8 -*-
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import servUtils.htmx_tpl as hx
import dataUtils.dataService as datServ

HOST = "127.0.0.1"
PORT = 8080

class OpenManulHTTPRequestHandler(SimpleHTTPRequestHandler):
    """自定义请求处理器，添加 UTF-8 编码响应头与基础 MIME 类型支持"""
    def do_GET(self):
        # 拦截特定路由，返回对应的 HTML 片段
        split_path = self.path.split("/")
        if split_path[0] != "":
            super.do_GET()
            return
        if split_path[1] == "individuals":
            manuls = om_database.getIndividuals().values()
            manul_sections = []
            for manul in manuls:
                manul_section = hx.fmt_card(manul, "zh")
                manul_sections.append(manul_section)
            html_snippet = "".join(manul_sections)
        elif split_path[1] == "tree":
            html_snippet = "<p>This is family tree page</p>"
        elif split_path[1] == "map":
            html_snippet = "<p>This is map page</p>"
        elif split_path[1] == "timeline":
            html_snippet = "<p>This is timeline page</p>"
        elif split_path[1] == "contribute":
            html_snippet = "<p>This is contribute page</p>"
        elif split_path[1] == "zoos":
            super().do_GET()
            return
        elif split_path[1] == "individual":
            manul = om_database.getIndividualByID(split_path[2])
            zoos = om_database.getZoos()
            if manul:
                html_snippet = hx.fmt_info(manul, zoos, "zh")
            else:
                super().do_GET()
        elif split_path[1] == "nav":
            zoos = om_database.getZoos().values()
            html_snippet = hx.fmt_zoo_filter(zoos, "zh")
        elif split_path[1] == "image":
            '''image/manul/{imgID}'''
            pic_path = "/".join([om_data_dir, "data", "individuals", split_path[2], "image", split_path[3]])
            print(pic_path)
            if not os.path.exists(pic_path):
                pic_path = "/".join([om_serv_dir, "template", "resource", "profile.png"])
            print(pic_path)
            with open(pic_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        elif split_path[1] == "reference":
            '''reference/manul/{ID}/{ref_id}'''
            try:
                # split_path[2] == "manul"
                manul_id   = split_path[3]
                ref_id_str = split_path[4]
                indv = om_database.getIndividualByID(manul_id)
                ref_idx = int(ref_id_str) - 1
                redirection_url = indv["links"][ref_idx]["href"]
                print(redirection_url)
                self.send_response(302)
                self.send_header("Location", redirection_url)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            except:
                super().do_GET()
                return
        else:
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
