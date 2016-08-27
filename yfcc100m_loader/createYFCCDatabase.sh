#!/bin/sh

JARVIS_DATABASE=yfcc100m_jarvis

rm -r $JARVIS_DATABASE

src/yfcc --locationTree data/geolite2/cities.csv $JARVIS_DATABASE
src/yfcc --cities data/geolite2/latlongcities.csv $JARVIS_DATABASE
src/yfcc --synonyms data/dictionary-seed/db/wordnet_generics.tsv $JARVIS_DATABASE
src/yfcc --media data/yfcc100m/yfcc100m_dataset_short $JARVIS_DATABASE
