""" mysources.py - (c)2023 UnivSchool
Extension for pyang configurations
	https://github.com/UnivSchool/pylearn/
"""

import os.path

#SAMPLE_OC_DIR = "../anaceo/openconfig_public/release/models"
SAMPLE_OC_DIR = "openconfig/public/release/models"

HTML_YANG_SKEL = """<!DOCTYPE html>
<html>
<body>
<title>{}</title>
{}
</body>
</html>
"""

KEY_REDDING = {
    "uses": "USE",
    "list": "CONT",
    "container": "CONT*",
    "type": "TYPE",
}

def main_test():
    sources = YSources()
    file_list = [
        "system/openconfig-alarms.yang",
        "optical-transport/openconfig-channel-monitor.yang",
    ]
    is_ok = sources.set_sample_config(file_list, SAMPLE_OC_DIR)
    print("set_sample_config():", is_ok)
    sources.show()
    for name in file_list:
        filename = SAMPLE_OC_DIR + "/" + name
        with open(filename, "r", encoding="utf-8") as fdin:
            text = fdin.read()
        rev = None
        sources.add_module(filename, text, "yang", name, rev)
    sources.populate_html()


class YBaseSource:
    """ Abstract class """
    def __init__(self, conf=None, name="?"):
        self.name = name

class YSources(YBaseSource):
    """ Yang source locations, including HTML siblings """
    def __init__(self, conf=None, name="sources"):
        super().__init__(name)
        self.conf = {} if conf is None else conf
        self.flist, self.pnames = [], []
        self.nmap = {
            "nick2pname": {},
            "pname2html": {},
            "html-base": "",
            "html2path": {},
        }  # Names map
        self._mod_html = {
            "path": {},
        }

    def show(self):
        mymap = self.nmap
        print("Configuration:", self.conf.confs)
        print("File listing:")
        print('\n'.join(self.flist) + '\n', end="<<<<\n")
        print(f'self.nmap["html-base"] = {self.nmap["html-base"]}')
        for key, s_val in mymap["pname2html"].items():
            print(f'nmap["pname2html"]["{key}"] = {s_val}')
        print("HTML PATHS:")
        for key, s_val in mymap["html2path"].items():
            print(f'nmap["html2path"]["{key}"] = {s_val}')
        return True

    def set_sample_config(self, file_list, adir:str="", html_bdir=None):
        """ Basic openconfig sampler, to ease this class testing. """
        assert isinstance(adir, str), "Type?"
        h_bdir = "cache_meta/html" if html_bdir is None else html_bdir
        assert isinstance(h_bdir, str)
        conf = YBaseSource()
        conf.confs = {
            "meta_html_bdir": [h_bdir],
        }
        pre = adir + "/" if adir else ""
        path_list = [pre + name for name in file_list]
        res = self.set_config(conf, file_list, path_list)
        return res

    def set_config(self, conf, file_list=None, path_list=None):
        is_ok = True
        self.conf = conf
        if "meta_html_bdir" in conf.confs:
            a_dir = conf.confs["meta_html_bdir"][0]
            self.nmap["html-base"] = a_dir
        if file_list is None:
            assert path_list is None, self.name
            args, filenames = [], []
        else:
            args, filenames = file_list, path_list
        self.flist, self.pnames = args, filenames
        self.nmap["nick2pname"] = dict(zip(args, filenames))
        self.flist = args
        self.pnames = filenames
        for pname in filenames:
            if not os.path.isfile(pname):
                is_ok = False
            bname = os.path.basename(pname)
            name, fext = os.path.splitext(bname)
            #print("BNAME:", pname, "IS:", bname, "; name:", name, "; extension:", fext)
            if fext not in (".yang",):
                continue
            html_name = name + ".html"
            self.nmap["pname2html"][pname] = html_name
            self.nmap["html2path"][html_name] = path_joiner(self.nmap["html-base"], html_name)
        return is_ok

    def add_module(self, filename, text, in_format, name, rev):
        assert isinstance(name, str), filename
        assert name, filename
        if in_format != "yang":
            return False
        assert rev is None, filename
        if filename not in self.nmap["pname2html"]:
            return False
        h_short_name = self.nmap["pname2html"][filename]
        h_full_name = self.nmap["html2path"][h_short_name]
        tup = (
            name, h_full_name,
            in_format == "yang",
            [line.rstrip() for line in text.splitlines()],
        )
        print("DEBUG: YSources add_module():", tup)
        self._mod_html["path"][filename] = tup
        return True

    def populate_html(self):
        """ Write HTML files """
        for y_file, tup in self._mod_html["path"].items():
            name, h_full_name, _, lines = tup
            assert name, h_full_name
            print("DEBUG: Write:", name, "; full-name:", h_full_name)
            self._populate_one(h_full_name, (name,), lines)
        return True

    def _populate_one(self, outname:str, tup:tuple, lines:list):
        """ Write HTML file """
        name = tup[0]
        resume = {}
        astr, idxes = "", ""
        for idx, line in enumerate(lines, 1):
            s_num = f"{idx:>5}".replace(" ", "&nbsp;")
            s_line = f"<td><a id=line{idx}>{s_num}</a></td>"
            this = line.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
            astr += f"<tr>{s_line}<td><pre>{this}<pre></td></tr>\n"
            this = line.replace("\t", " ").split(" ")
            this = [item for item in this if len(item) >= 4]
            if this:
                if len(this) >= 2 and this[0] in KEY_REDDING:
                        s_line = f"{this[0]} <b><font color=red>{this[1]}</font></b>"
                elif len(this) >= 2 and this[0] in ("config",):
                    continue
                else:
                    s_line = this[0]
                if s_line:
                    resume[idx] = s_line
        for idx, line in enumerate(lines, 1):
            if not line:
                continue
            this = line.strip().split("//", maxsplit=1)
            if not this[0].strip():
                continue
            if idx not in resume:
                continue
            s_line = "<tr><td><a href='#line{}'>Line {}</a></td><td>{}</td</tr>".\
                format(idx, idx, resume[idx])
            idxes += s_line + "\n"
        s_content = """
<table border=0>
<tr><td>&nbsp;</td><td bgcolor=lightgreen>{}</td></tr>
<!-- remaining Yang -->
{}
</table>
<table border=1>
{}
</table>
""".format(name, astr, idxes)
        astr = HTML_YANG_SKEL.format(name, s_content)
        with open(outname, "w", encoding="ascii") as fdout:
            fdout.write(astr)
        return True

def path_joiner(dname:str, bname:str) -> str:
    """ Joins dirname and basename """
    res = os.path.join(dname, bname)
    if "/" in dname:
        res = res.replace("\\", "/")
    return res


if __name__ == "__main__":
    main_test()
