#!/bin/bash

#########################################################

APPCFG=appcfg.py
KINDS="AllowedRange Command ControllerTagRelationship ControllerTag Controller EnumValue LastUpdateTime Manufacturer Message MessageItem Pid ProductCategory ResponderPersonality ResponderSensor ResponderTagRelationship ResponderTag Responder SoftwareVersion"
EMAIL="simon@nomis52.net"
HOST="localhost:8080"
PASSWORD="czigyzwsgaxaifku"
#########################################################

set +x
if [ $# -ne 1 ]; then
  echo "Usage: `basename $0` <output_dir>"
  exit 65;
fi

dir=$1

if [ ! -d $dir ]; then
  echo "Usage: `basename $0` <output_dir>"
fi

if [ -z $PASSWORD ]; then
  echo "Enter password or enter to skip";
  read passwd;
else
  passwd=$PASSWORD;
fi

for kind in $KINDS; do
  input=$(echo $kind | tr '[A-Z]' '[a-z]');
  echo "INSERTING $kind";
  echo $passwd | $APPCFG upload_data \
    --url=http://$HOST/_ah/remote_api \
    --filename=$dir/output-$input \
    --kind=$kind \
    --email=$EMAIL \
    --passin \
    --config_file=bulkloader.yaml \
    --num_threads=5;
done
