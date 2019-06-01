#!/bin/bash

# Resolve symlinks within the image
nickname="{{PYTHON}}"
executable="${APPDIR}/usr/bin/${nickname}"
if [ -L "${executable}" ]; then
    nickname="$(basename $(readlink -f ${executable}))"
fi

for opt in "$@"
do
    [ "${opt:0:1}" != "-" ] && break
    if [[ "${opt}" =~ "I" ]] || [[ "${opt}" =~ "E" ]]; then
        # Environment variables are disabled ($PYTHONHOME). Let's run in a safe
        # mode from the raw Python binary inside the AppImage
        "$APPDIR/usr/bin/.${nickname}" "$@"
        exit "$?"
    fi
done

# But don't resolve symlinks from outside!
if [[ "${ARGV0}" =~ "/" ]]; then
    executable="$(cd $(dirname ${ARGV0}) && pwd)/$(basename ${ARGV0})"
else
    executable=$(which "${ARGV0}")
fi

# Wrap the call to Python in order to mimic a call from the source
# executable ($ARGV0), but potentially located outside of the Python
# install ($PYTHONHOME)
(PYTHONHOME="${APPDIR}/usr" exec -a "${executable}" "$APPDIR/usr/bin/.${nickname}" "$@")
exit "$?"
