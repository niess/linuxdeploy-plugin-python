#! /bin/bash

# Upload the AppImage
ls -lh appimage/*.AppImage
wget -c https://github.com/probonopd/uploadtool/raw/master/upload.sh
source upload.sh appimage/*.AppImage


# Upload the Docker container
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push $DOCKER_USERNAME/linuxdeploy-plugin-python:${ARCH}
