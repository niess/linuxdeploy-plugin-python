import json
import os
import shutil
import subprocess
import unittest
import sys


TAGS = ("python2", "python3")

TESTDIR = "/tmp/test-linuxdeploy-plugin-python"
ROOTDIR = os.path.realpath(os.path.dirname(__file__) + "/..").strip()

_is_python2 = sys.version_info[0] == 2


def get_version(recipe):
    path = os.path.join(ROOTDIR, "appimage", "recipes", recipe + ".sh")
    with open(path) as f:
        for line in f:
            if line.startswith("export PYTHON_VERSION="):
                version = line.split("=")[-1]
                return version.strip().replace('"', "").replace("'", "")
        else:
            raise ValueError("version not found")


def system(command, env=None):
    """Wrap system calls
    """
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, env=env)
    out, _ = p.communicate()
    if not _is_python2:
        out = out.decode()
    if p.returncode != 0:
        raise RuntimeError(os.linesep.join(
            ("", "COMMAND:", command, "OUTPUT:", out)))
    return out


class PluginTest(unittest.TestCase):
    """Unit tests for the python plugin
    """

    def __init__(self, *args, **kwargs):
        if _is_python2:
            super(PluginTest, self).__init__(*args, **kwargs)
        else:
            super().__init__(*args, **kwargs)

        # Configure the test environment
        if not "ARCH" in os.environ:
            os.environ["ARCH"] = system("arch").strip()

        user = os.getenv("USER")
        if (user is None) or (user == "root"):
            user = "beta"
            home = "/tmp/home/" + user
            os.environ["USER"] = user
            os.environ["HOME"] = home
            if not os.path.exists(home):
                for tag in TAGS:
                    version = get_version(tag)
                    os.makedirs(os.path.join(home, ".local", "lib",
                        "python" + version[:3], "site-packages"))
            bindir = os.path.join(home, ".local", "bin")
            os.environ["PATH"] = ":".join((bindir, os.environ["PATH"]))

        if not os.path.exists(TESTDIR):
            os.makedirs(TESTDIR)
        os.chdir(TESTDIR)

        for tag in TAGS:
            appimage = "{:}-{:}.AppImage".format(tag, os.environ["ARCH"])
            shutil.copy(
                os.path.join(ROOTDIR, "appimage", appimage),
                os.path.join(TESTDIR, appimage))


    def test_python3_base(self):
        """Test the base functionalities of a Python 3 AppImage
        """
        self.check_base("python3")

    def test_python3_modules(self):
        """Test the modules availability of a Python 3 AppImage
        """
        self.check_modules("python3")


    def test_python3_venv(self):
        """Test venv from a Python 3 AppImage
        """
        self.check_venv("python3")


    def test_python2_base(self):
        """Test the base functionalities of a Python 2 AppImage
        """
        self.check_base("python2")


    def check_base(self, tag):
        """Check the base functionalities of a Python AppImage
        """
        version = get_version(tag)
        appimage = "python{:}-{:}.AppImage".format(
            version[0], os.getenv("ARCH"))

        # Check the Python system configuration
        python = os.path.join(TESTDIR, appimage)
        cfg = self.get_python_config(python)

        v = [int(vi) for vi in version.split(".")]
        self.assertEqual(cfg["version"][:3], v)
        self.assertEqual(cfg["executable"], python)
        self.assertEqual(cfg["prefix"], os.path.join(cfg["appdir"], "usr"))
        site_packages = os.path.join("lib",
            "python{:}.{:}".format(*cfg["version"][:2]), "site-packages")
        self.assertEqual(cfg["path"][-1], os.path.join(cfg["appdir"],
            "usr", site_packages))
        user_packages = os.path.join(cfg["home"], ".local", site_packages)
        self.assertTrue(user_packages in cfg["path"])

        # Check pip install
        system("./{:} -m pip uninstall test-pip-install -y || exit 0".format(
            appimage))
        r = system("./{:} -m pip install --user test-pip-install".format(
            appimage))
        r = system("test-pip-install").strip()
        self.assertEqual(r, "running Python {:} from {:}".format(
                            version, os.path.join(TESTDIR, appimage)))


    def check_venv(self, tag):
        """Check venv from a Python AppImage
        """
        version = get_version(tag)
        appimage = "python{:}-{:}.AppImage".format(
            version[0], os.getenv("ARCH"))

        # Generate a virtual environment
        if os.path.exists("ENV"):
            shutil.rmtree("ENV")

        system("./{:} -m venv ENV".format(appimage))
        envdir = TESTDIR + "/ENV"
        python = envdir + "/bin/python"
        self.assertTrue(os.path.exists(python))

        # Bootstrap pip
        def bash(cmd):
            return system("/bin/bash -c '. ENV/bin/activate; {:}'".format(cmd))

        bash("python -m ensurepip")
        pip = "pip" + version[0]
        self.assertTrue(os.path.exists("ENV/bin/" + pip))

        # Check the Python system configuration
        cfg = self.get_python_config("python", setup="ENV/bin/activate")

        v = [int(vi) for vi in version.split(".")]
        self.assertEqual(cfg["version"][:3], v)
        self.assertEqual(cfg["executable"], str(python))
        self.assertEqual(cfg["prefix"], str(envdir))
        site_packages = os.path.join("lib",
            "python{:}.{:}".format(*cfg["version"][:2]), "site-packages")
        self.assertEqual(cfg["path"][-1], str(os.path.join(envdir,
                                              site_packages)))
        self.assertTrue(os.path.join(cfg["home"], ".local",
            site_packages) not in cfg["path"])

        # Check pip install
        system("{:} uninstall test-pip-install -y || exit 0".format(pip))
        bash("{:} uninstall test-pip-install -y".format(pip))
        bash("{:} install test-pip-install".format(pip))
        r = bash("test-pip-install").strip()
        bash("{:} uninstall test-pip-install -y".format(pip))
        self.assertEqual(r, "running Python {:} from {:}".format(
                            version, str(python)))


    def check_modules(self, tag):
        """Check the modules availability of a Python AppImage
        """
        version = get_version(tag)
        appimage = "python{:}-{:}.AppImage".format(
            version[0], os.getenv("ARCH"))

        def import_(module):
            system("./{:} -c 'import {:}'".format(appimage, module))

        modules = {
            "a": ["abc", "aifc", "argparse", "array", "ast", "asynchat",
                  "asyncio", "asyncore", "atexit", "audioop"],
            "b": ["base64", "bdb", "binascii", "binhex", "bisect", "builtins",
                  "bz2"],
            "c": ["calendar", "cgi", "cgitb", "chunk", "cmath", "cmd", "code",
                  "codecs", "codeop", "collections", "colorsys", "compileall",
                  "concurrent", "configparser", "contextlib", "contextvars",
                  "copy", "copyreg", "cProfile", "crypt", "csv", "ctypes",
                  "curses"],
            "d": ["dataclasses", "datetime", "dbm", "decimal", "difflib",
                  "dis", "distutils", "doctest"],
            "e": ["email", "encodings", "ensurepip", "enum", "errno"],
            "f": ["faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch",
                  "fractions", "ftplib", "functools"],
            "g": ["gc", "getopt", "getpass", "gettext", "glob", "grp", "gzip"],
            "h": ["hashlib", "heapq", "hmac", "html", "http"],
            "i": ["imaplib", "imghdr", "importlib", "inspect", "io",
                  "ipaddress", "itertools"],
            "j": ["json"],
            "k": ["keyword"],
            "l": ["lib2to3", "linecache", "locale", "logging", "lzma"],
            "m": ["mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap",
                  "modulefinder", "multiprocessing"],
            "n": ["netrc", "nis", "nntplib", "numbers"],
            "t": ["tkinter"]
        }

        for sublist in modules.values():
            for module in sublist:
                import_(module)


    def get_python_config(self, python, setup=None):
        """Get the config loaded by the given Python instance
        """

        cfg_file = "cfg.json"
        if os.path.exists(cfg_file):
            os.remove(cfg_file)

        script = """\
import json
import os
import sys

with open("{:}", "w+") as f:
    json.dump({{"path": sys.path, "executable": sys.executable,
               "prefix": sys.prefix, "user": os.getenv("USER"),
               "home": os.getenv("HOME"), "version": tuple(sys.version_info),
               "appdir": os.getenv("APPDIR")}}, f)
        """.format(cfg_file)

        script_file = "script.py"
        with open(script_file, "w") as f:
            f.write(script)

        if setup:
            system("/bin/bash -c '. {:}; {:} {:}'".format(
                   setup, python, script_file))
        else:
            system("{:} {:}".format(python, script_file))

        with open(cfg_file) as f:
            return json.load(f)


if __name__ == "__main__":
    unittest.main(failfast=True)
