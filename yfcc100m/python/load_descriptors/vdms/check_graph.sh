/home/luisremi/vcs/pmgd/tools/dumpgraph db/graph > dump.graph
echo "Number of Images:"
cat dump.graph | grep "#VD:IMG" | wc -l
echo "Number of autotags:"
cat dump.graph | grep "#autotags" | wc -l
echo "Number of connections:"
cat dump.graph | grep "#tag:" | wc -l
echo "Number of Descriptors Set:"
cat dump.graph | grep "VD:DESCSET" | wc -l
echo "Number of Descriptors:"
cat dump.graph | grep "VD:DESC" | wc -l
