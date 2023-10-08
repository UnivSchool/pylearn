""" mysources.py - (c)2023 UnivSchool
Extension for pyang configurations
	https://github.com/UnivSchool/pylearn/
"""

import os.path

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

    def show(self):
        mymap = self.nmap
        print("Configuration:", self.conf)
        print("File listing:")
        print('\n'.join(self.flist) + '\n', end="<<<<\n")
        for key, s_val in mymap["pname2html"].items():
            print(f'nmap["pname2html"]["{key}"] = {s_val}')
        print("HTML PATHS:")
        for key, s_val in mymap["html2path"].items():
            print(f'nmap["html2path"]["{key}"] = {s_val}')
        return True

    def set_sample_config(self, file_list, html_bdir=None):
        """ Basic openconfig sampler, to ease this class testing. """
        h_bdir = "cache_meta/html" if html_bdir is None else html_bdir
        assert isinstance(h_bdir, str)
        conf = YBaseSource()
        conf.confs = {
            "meta_html_bdir": h_bdir,
        }
        path_list = ["openconfig_public/" + name for name in file_list]
        res = self.set_config(conf, file_list, path_list)
        return res

    def set_config(self, conf, file_list=None, path_list=None):
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
                return False
            bname = os.path.basename(pname)
            name, fext = os.path.splitext(bname)
            #print("BNAME:", pname, "IS:", bname, "; name:", name, "; extension:", fext)
            if fext not in (".yang",):
                continue
            html_name = bname + ".html"
            self.nmap["pname2html"][pname] = html_name
            self.nmap["html2path"][html_name] = path_joiner(self.nmap["html-base"], html_name)
        return True

    def add_module(self, filename, text, in_format, name, rev):
        return True

def path_joiner(dname:str, bname:str) -> str:
    """ Joins dirname and basename """
    res = os.path.join(dname, bname)
    if "/" in dname:
        res = res.replace("\\", "/")
    return res
