import json
import os
import shutil
import subprocess
import unittest
import sys


PYTHON2_VERSION = "2.7.16"
PYTHON3_VERSION = "3.7.3"

LINUX_DEPLOY = "linuxdeploy-x86_64.AppImage"
URL = "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous"
PLUGIN = "linuxdeploy-plugin-python-x86_64.AppImage"

TESTDIR = "/tmp/test-linuxdeploy-plugin-python"
ROOTDIR = os.path.realpath(os.path.dirname(__file__) + "/..").strip()


_is_python2 = sys.version_info[0] == 2


def system(command, env=None):
    """Wrap system calls
    """
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, env=env)
    out, _ = p.communicate()
    if not _is_python2:
        out = out.decode()
    if p.returncode != 0:
        raise RuntimeError(out)
    return out


def python_url(version):
    """Download URL for specific Python version
    """
    base = "https://www.python.org/ftp/python"
    return "{0:}/{1:}/Python-{1:}.tgz".format(base, version)


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
                os.makedirs(os.path.join(home, ".local", "lib",
                            "python" + PYTHON2_VERSION[:3], "site-packages"))
                os.makedirs(os.path.join(home, ".local", "lib",
                            "python" + PYTHON3_VERSION[:3], "site-packages"))
            bindir = os.path.join(home, ".local", "bin")
            os.environ["PATH"] = ":".join((bindir, os.environ["PATH"]))

        system(ROOTDIR + "/appimage/build-appimage.sh")

        try:
            os.makedirs(TESTDIR)
        except:
            pass
        os.chdir(TESTDIR)
        system("wget --no-check-certificate -c {:}/{:}".format(
            URL, LINUX_DEPLOY))
        system("chmod u+x {:}".format(LINUX_DEPLOY))
        shutil.copy(ROOTDIR + "/appimage/" + PLUGIN, TESTDIR)


    def test_python3_base(self):
        """Test the base functionalities of a Python 3 AppImage
        """
        appimage, version = "python3-x86_64.AppImage", PYTHON3_VERSION
        if not os.path.exists(os.path.join(TESTDIR, appimage)):
            self.build_python_appimage(PYTHON3_VERSION)
        self.check_base(appimage, version)


    def test_python3_venv(self):
        """Test venv from a Python 3 AppImage
        """
        appimage, version = "python3-x86_64.AppImage", PYTHON3_VERSION
        self.check_venv(appimage, version)


    def test_python2_base(self):
        """Test the base functionalities of a Python 2 AppImage
        """
        appimage, version = "python2-x86_64.AppImage", PYTHON2_VERSION
        if not os.path.exists(os.path.join(TESTDIR, appimage)):
            self.build_python_appimage(
                PYTHON2_VERSION, PYTHON_SOURCE=python_url(version))
        self.check_base(appimage, version)


    def check_base(self, appimage, version):
        """Check the base functionalities of a Python AppImage
        """

        # Check the Python system configuration
        python = os.path.realpath(appimage)
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


    def check_venv(self, appimage, version):
        """Check venv from a Python AppImage
        """

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


    def build_python_appimage(self, version, **kwargs):
        """Build a Python AppImage using linux-deploy-python
        """
        nickname = "python" + version[0]
        exe = ".python" + version[:3]

        appdir = TESTDIR +  "/AppDir"
        if os.path.exists(appdir):
            shutil.rmtree(appdir)
        resdir = TESTDIR + "/resources"
        if os.path.exists(resdir):
            shutil.rmtree(resdir)
        os.makedirs(resdir)

        # Create generic resources for the application deployement
        src = ROOTDIR + "/appimage/resources/linuxdeploy-plugin-python.png"
        icon = os.path.join(resdir, nickname + ".png")
        shutil.copy(src, icon)

        desktop = os.path.join(resdir, nickname + ".desktop")
        with open(desktop, "w") as f:
            f.write("""\
[Desktop Entry]
Categories=Development;
Type=Application
Icon={0:}
Exec={1:}
Name={0:}
Terminal=true
""".format(nickname, exe))

        for index in range(2):
            command = ["./" + LINUX_DEPLOY,
                "--appdir", appdir,
                "-i", icon,
                "-d", desktop]
            if index == 0:
                command += [
                    "--plugin", "python"]
            else:
                command += [
                    "-e", os.path.join(appdir, "usr", "bin", exe),
                    "--custom-apprun", os.path.join(appdir, "usr", "bin",
                                                    nickname),
                    "--output", "appimage"]

            env = os.environ.copy()
            env.update(kwargs)
            system(" ".join(command), env=env)

        shutil.copy(
            TESTDIR + "/{:}-{:}.AppImage".format(nickname, os.environ["ARCH"]),
            ROOTDIR + "/appimage")


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
