#!/bin/bash

#########################################################
APPCFG=appcfg.py
BASE_KINDS="Manufacturer"
PID_KINDS="${BASE_KINDS} Command Pid"
CONTROLLER_KINDS="ControllerTagRelationship ControllerTag Controller"
RESPONDER_KINDS="ProductCategory ResponderPersonality ResponderSensor ResponderTagRelationship ResponderTag Responder SoftwareVersion"
ALL_KINDS="${PID_KINDS} ${CONTROLLER_KINDS} ${RESPONDER_KINDS} ${BASE_KINDS} LastUpdateTime"
HOST="localhost:8080"
#########################################################

set +x

usage() {
cat << EOF
usage: $0 options

Dump the data store out to files.

OPTIONS:
   -d <path>      Output directory
   -e <email>     Email address to login with
   -h             Show this message
   -H <hostname>  Hostname to fetch from
   -m             Backup messages (PIDs) only
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


if [ -z "$dir" ]; then
  usage
  exit 65;
fi

if [ -z "$email" ]; then
  usage
  exit 65;
fi

if [ ! -d $dir ]; then
  if [ -e $dir ]; then
    echo "$dir already exists and is not a directory"
    exit 1;
  fi;
  mkdir -p $dir;
fi

if [ -z $password ]; then
  echo "Enter password or enter to skip";
  read password;
fi

for kind in $(echo $kinds | tr " " "\n" | sort | uniq | xargs); do
  output=$(echo $kind | tr '[A-Z]' '[a-z]');
  echo $password | $APPCFG download_data \
    --url=http://$HOST/_ah/remote_api \
    --filename=$dir/output-$output \
    --kind=$kind \
    --email=$email \
    --passin \
    --num_threads=1 \
    --config_file=bulkloader.yaml;
  if [ $? -ne 0 ]; then
    exit $?;
  fi;
done
