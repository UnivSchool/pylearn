""" myconfs.py - (c)2023 UnivSchool
Extension for pyang configurations
	https://github.com/UnivSchool/pylearn/
"""

import os.path

DEBUG = 0

DEF_CONFIG_BASE = "pyangconfig.csv"

DEF_PATHS = {
    "basedir": [],
    "paths": [],
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

    def load_config(self, d_or_fname:str):
        """ Load configuration """
        fname = d_or_fname if os.path.isfile(d_or_fname) else os.path.join(d_or_fname, DEF_CONFIG_BASE)
        self.confs, msg = self._reload_config(fname)
        if DEBUG > 0:
            print("Loaded configuration:", fname, "; basedir():", self.basedir())
            print(self.confs, end="\n\n")
            print("Msg", ":" if msg else ": OK", msg)
        return True

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
