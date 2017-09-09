#!/bin/sh

JARVIS_DB=yfcc100m_jarvis

rm -r $JARVIS_DB

./yfcc --locationTree data/extras/geolite2/cities.csv $JARVIS_DB
./yfcc --cities data/extras/geolite2/latlongcities.csv $JARVIS_DB
./yfcc --synonyms data/extras/dictionary-seed/db/wordnet_generics.tsv $JARVIS_DB
./yfcc --media data/yfcc100m/yfcc100m_dataset_short $JARVIS_DB
