#!/bin/bash

#########################################################
APPCFG=appcfg.py
BASE_KINDS="Manufacturer"
PID_KINDS="${BASE_KINDS} AllowedRange Command EnumValue Message MessageItem Pid"
CONTROLLER_KINDS="ControllerTagRelationship ControllerTag Controller"
RESPONDER_KINDS="ProductCategory ResponderPersonality ResponderSensor ResponderTagRelationship ResponderTag Responder SoftwareVersion"
ALL_KINDS="${PID_KINDS} ${CONTROLLER_KINDS} ${RESPONDER_KINDS} ${BASE_KINDS} LastUpdateTime"
HOST="localhost:8080"
#########################################################

set +x

usage() {
cat << EOF
usage: $0 options

Insert the backup into a data store.

OPTIONS:
   -d <path>      Directory to read data from
   -e <email>     Email address to login with
   -h             Show this message
   -H <hostname>  Hostname to upload to
   -m             Insert messages (PIDs) only
   -p <password>  password
EOF
}

email=
dir=
# default to everything
kinds=$ALL_KINDS;

while getopts “d:e:hH:mp:” option
do
  case $option in
    d)
      dir=$OPTARG
      ;;
    e)
      email=$OPTARG
      ;;
    h)
      usage;
      exit 1
      ;;
    H)
      HOST=$OPTARG
      ;;
    m)
      kinds=$PID_KINDS
      ;;
    p)
      password=$OPTARG
      ;;
    ?)
      usage
      exit 1
      ;;
  esac
done


if [ -z "$email" ]; then
  usage
  exit 65;
fi

if [ ! -d $dir ]; then
  echo "Usage: `basename $0` <output_dir>"
fi

if [ -z $PASSWORD ]; then
  echo "Enter password or enter to skip";
  read passwd;
else
  passwd=$PASSWORD;
fi

for kind in $kinds; do
  input=$(echo $kind | tr '[A-Z]' '[a-z]');
  echo "INSERTING $kind";
  echo $passwd | $APPCFG upload_data \
    --url=http://$HOST/_ah/remote_api \
    --filename=$dir/output-$input \
    --kind=$kind \
    --email=$email \
    --passin \
    --config_file=bulkloader.yaml \
    --num_threads=1;
  if [ $? -ne 0 ]; then
    exit $?;
  fi;
  # We need to sleep between kinds because the bulkloader uses the timestamp as
  # as part of the progress database. Talk about dumb.
  sleep 1
done
