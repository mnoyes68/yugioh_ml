#!/bin/bash

COUNT=50
HOST_PREFIX=https://m2k8n9f7.ssl.hwcdn.net/images/

downloadImages() {
    for i in $(seq 1 $COUNT); do
        printf -v NUMBER_FORMATTED "%03d" $i
        FILENAME=$3-$NUMBER_FORMATTED.jpg

        SOURCE=${HOST_PREFIX}$2/$FILENAME
        TARGET=$1/$FILENAME

        curl $SOURCE > $TARGET
    done
}

downloadImages client/src/assets/images/yugi sdy SDY
downloadImages client/src/assets/images/kaiba sdk SDK
downloadImages client/src/assets/images/joey sdj SDJ
downloadImages client/src/assets/images/pegasus sdp SDP