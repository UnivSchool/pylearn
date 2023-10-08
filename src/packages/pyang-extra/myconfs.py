""" myconfs.py - (c)2023 UnivSchool
Extension for pyang configurations
	https://github.com/UnivSchool/pylearn/
"""

from sys import stdout
import os.path

DEBUG = 0

DEF_CONFIG_BASE = "pyangconfig.csv"

DEF_PATHS = {
    "basedir": [],
    "paths": [],
}

BOOL_KEYS = {
    "TREE_META": (False, "Has extra meta HTML files"),
}

class OwnPaths:
    """ Own modeling paths class! """
    def __init__(self, dct=None, name="basic"):
        self.name = name
        self.confs = DEF_PATHS if dct is None else dct
        assert isinstance(self.confs, dict), name

    def basedir(self) -> str:
        bdirs = self.confs["basedir"]
        assert len(bdirs) <= 1, self.name
        return bdirs[0] if bdirs else ""

    def paths(self) -> list:
        return self.confs["paths"]

    def has_meta(self) -> bool:
        return self.confs["tree_meta"]

    def load_config(self, d_or_fname:str):
        """ Load configuration """
        fname = d_or_fname if os.path.isfile(d_or_fname) else os.path.join(d_or_fname, DEF_CONFIG_BASE)
        self.confs, msg = self._reload_config(fname)
        if DEBUG > 0:
            print("Loaded configuration:", fname, "; basedir():", self.basedir())
            print(self.confs, end="\n\n")
            print("Msg", ":" if msg else ": OK", msg)
        return True

    def from_args(self, args):
        """ Returns the same paths, or the complete path in case any of the paths is found in basedir().
        Example: release/models/system/openconfig-alarms.yang is expanded to <BASEDIR>/...
        """
        assert isinstance(args, list)
        res = []
        bdir = self.basedir()
        for path in args:
            new = path
            if bdir:
                fpath = os.path.join(bdir, path)
                if os.path.isfile(fpath):
                    new = fpath
                    if "/" in path:
                        new = new.replace("\\", "/")
            res.append(new)
        return res

    def _reload_config(self, fname) -> tuple:
        dct = {}
        with open(fname, "r", encoding="ascii") as fdin:
            lines = [line.strip() for line in fdin.readlines() if not line.startswith("#")]
        for line in lines:
            if not line:
                continue
            oper_eq = "S"  # Set
            if "+=" in line:
                lvar, rvar = line.split("+=", maxsplit=1)
                oper_eq = "P"
            elif "=" in line:
                lvar, rvar = line.split("=", maxsplit=1)
            else:
                return {}, f"Unsupported syntax: '{line}'"
            lvar = lvar.strip()
            rvar = rvar.strip()
            avar = lvar.lower()
            if not lvar:
                print("Ignored:", line)
            if oper_eq in ("S",):
                if lvar in BOOL_KEYS:
                    my_default, _ = BOOL_KEYS[lvar]
                    assert rvar in ("True", "False", "*"), lvar
                    if rvar == "*":
                        rvar = my_default
                    else:
                        rvar = rvar == "True"
                    dct[avar] = rvar
                else:
                    dct[avar] = [rvar]
            elif oper_eq in ("P",):  # Plus...
                #print("ADDED:", avar, "AS:", rvar)
                if avar in dct:
                    dct[avar].append(rvar)
                else:
                    dct[avar] = [rvar]
            else:
                return {}, "Invalid op"
        return dct, ""


class Writer(object):
    """ Multiple file writer. """
    def __init__(self, name="writer"):
        self.name = name
        self.dout = stdout
        self.alt = None
        self._lines = []

    def set_text_alt(self, fname:str, allow_overide=True):
        self.alt = None
        if not fname:
            return False
        assert isinstance(fname, str), "Should be string"
        if not allow_overide:
            if os.path.isfile(fname):
                return False
        self.alt = fname
        return True

    def write(self, astr):
        if self.dout is None:
            return -1
        res = self.dout.write(astr)
        if self.alt is None:
            return res
        self._lines.append(astr)
        return res

    def flush_all(self):
        if self.alt is None:
            return False
        astr = ''.join(self._lines)
        with open(self.alt, "wb") as fdout:
            fdout.write(astr.encode("utf-8"))
        return True

    def __del__(self):
       self.flush_all()

# Debug tree.py:
#   s = module ...
#   [(ala, getattr(s, ala)) for ala in dir(s) if ala[0].isalpha() and hasattr(s, ala)]
#   or ...
#   [(callable(getattr(s, ala)), ala, getattr(s, ala)) for ala in dir(s) if ala[0].isalpha() and hasattr(s, ala)]
# Distinguishing functions:
#   [(key, val, callable(val)) for key, val in statements.ModSubmodStatement.__dict__.items() if key == "prune"][0]
#   prune() is a function of a Module class.
