parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_0/data_0/images/" < yfcc100m_0_0 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_0/data_1/images/" < yfcc100m_0_1 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_0/data_2/images/" < yfcc100m_0_2 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_0/data_3/images/" < yfcc100m_0_3 &

parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_1/data_0/images/" < yfcc100m_1_0 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_1/data_1/images/" < yfcc100m_1_1 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_1/data_2/images/" < yfcc100m_1_2 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_1/data_3/images/" < yfcc100m_1_3 &

parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_2/data_0/images/" < yfcc100m_2_0 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_2/data_1/images/" < yfcc100m_2_1 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_2/data_2/images/" < yfcc100m_2_2 &
parallel --gnu -j 64 "wget -q -x -nH --directory-prefix=/yfcc100m/set_2/data_3/images/" < yfcc100m_2_3 &
