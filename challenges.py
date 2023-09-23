import base64
import abc
import os
import re
from typing import List

from util import bash, cat


class Challenge(abc.ABC):
    @abc.abstractmethod
    def run(self):
        pass

    @property
    def intermediate_files(self) -> List[str]:
        return []

    def __del__(self):
        for f in self.intermediate_files:
            os.remove(f)


class ObedientCat(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["flag"]

    def run(self):
        bash(
            "wget https://mercury.picoctf.net/static/0e428b2db9788d31189329bed089ce98/flag"
        )
        cat("flag")


class Mod26(Challenge):
    def run(self):
        # TODO: copy from pc
        pass


class WaveAFlag(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["warm"]

    def run(self):
        bash(
            "wget https://mercury.picoctf.net/static/f95b1ee9f29d631d99073e34703a2826/warm"
        )
        bash("chmod +x warm")
        bash("./warm -h")


class Information(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["cat.jpg"]

    def run(self):
        # original bash command that works
        # $ exiftool cat.jpg | grep -E License | sed -E 's/License\s+: //g' | base64 -d
        bash(
            "wget https://mercury.picoctf.net/static/e5825f58ef798fdd1af3f6013592a971/cat.jpg"
        )
        out = bash("exiftool cat.jpg", get_stdout=True)
        m = re.search(r"License\s+:\s(.*)", out).group(1)
        print(base64.decodebytes(bytes(m, encoding="utf-8")).decode("utf-8"))


class NiceNetCat(Challenge):
    def run(self):
        print("you need to press enter to break communication on netcat")
        out = bash("nc mercury.picoctf.net 21135", get_stdout=True)
        chars = [int(o) for o in out.split("\n") if o not in (" ", "\n", "")]
        print("".join(chr(c) for c in chars))
