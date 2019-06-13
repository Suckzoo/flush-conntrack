#!/bin/sh

if [ -z $TARGET_IP ];
then
    echo "Error: TARGET_IP is unset. Please provide TARGET_IP via environment variable."
    exit 1
fi

if [ -z $TARGET_PORT ];
then
    echo "Error: TARGET_PORT is unset. Please provide TARGET_PORT via environment variable."
    exit 1
fi

echo "$TARGET_IP:$TARGET_PORT"
curl "http://flush-conntrack.$TARGET_NAMESPACE/flush?ip=$TARGET_IP&port=$TARGET_PORT"