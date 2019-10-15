export PYTHON_VERSION="3.7.3"
export PIP_REQUIREMENTS="xonsh prompt_toolkit gnureadline Pygments"
export PYTHON_ENTRYPOINT='"-u" "-c" "from xonsh.main import main; main()"'
export LD_LIBRARY_PATH="AppDir/usr/python/lib/python3.7/site-packages/.libsgnureadline:${LD_LIBRARY_PATH}"
