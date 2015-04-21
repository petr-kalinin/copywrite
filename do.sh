iconv -f cp1251 -t utf8 <resWork.gdf >resWork.utf8.gdf
grep -v -E ",(1|2)\$" <resWork.utf8.gdf > resWork.filt.gdf