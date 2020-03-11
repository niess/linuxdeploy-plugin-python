#!/bin/bash

SCRIPT=`readlink -f -- $0`
SCRIPTPATH=`dirname $SCRIPT`
APPDIR="${APPDIR:-$SCRIPTPATH}"

${APPDIR}/usr/bin/{{exe}} {{entrypoint}} "$@"
