#!/bin/sh

JARVIS_DATABASE=yfcc100m_jarvis

rm -r $JARVIS_DATABASE

src/yfcc 2 data/geolite2/cities.csv $JARVIS_DATABASE
src/yfcc 3 data/geolite2/latlongcities.csv $JARVIS_DATABASE
src/yfcc 4 data/dictionary-seed/db/wordnet_generics.tsv $JARVIS_DATABASE
src/yfcc 1 data/yfcc100m/yfcc100m_dataset_short $JARVIS_DATABASE