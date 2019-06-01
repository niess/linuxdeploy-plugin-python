#! /bin/bash

ls -lh appimage/*.AppImage
wget -c https://github.com/probonopd/uploadtool/raw/master/upload.sh
source upload.sh appimage/*.AppImage
