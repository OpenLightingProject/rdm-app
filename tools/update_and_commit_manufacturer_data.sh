#!/bin/bash
# Autoupdate data/manufacturer_data.py

(
UPSTREAM=$1
UPSTREAM_BRANCH=$2
ORIGIN=$3
ORIGIN_BRANCH=$4

if [ $# -ne 4 ]
then
echo "Usage:"
echo "$0 upstream master origin manufacturer-updates"
exit
fi

cd "${BASH_SOURCE%/*}" || exit # cd into the bundle and use relative paths
ls

echo "Pulling from $ORIGIN $ORIGIN_BRANCH"
git pull $ORIGIN $ORIGIN_BRANCH || exit

echo "Pulling from $UPSTREAM $UPSTREAM_BRANCH"
git pull $UPSTREAM $UPSTREAM_BRANCH || exit

./make_manufacturer_data.sh > ../data/manufacturer_data.py

git diff --exit-code ../data/manufacturer_data.py

if [ $? -eq 0 ]
then
echo "No changes"
exit
fi

echo "Committing"
git commit -m "`printf "Autoupdated manufacturer data\nPlease check this manually before merging"`" ../data/manufacturer_data.py

echo "Pushing to $ORIGIN $ORIGIN_BRANCH"
git push $ORIGIN $ORIGIN_BRANCH || exit

echo "Done"
)