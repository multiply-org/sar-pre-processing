#!/bin/bash
files=$1/*.nc
for f in $files
do ncap -h -O -s 'crs=-9999' $f $f
   echo $f 
   ncatted -h -O \
      -a spatial_ref,crs,c,c,'GEOGCS[\"GCS_WGS_1984\",DATUM[\"WGS_1984\",SPHEROID[\"WGS_84\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.017453292519943295]]' \
      -a grid_mapping_name,crs,c,c,'latitude_longitude' \
      -a longitude_of_prime_meridian,crs,c,d,0 \
      -a semi_major_axis,crs,c,d,6378137 \
      -a inverse_flattening,crs,c,d,298.257223563 \
      -a grid_mapping,theta,c,c,'crs' \
      -a grid_mapping,sigma0_vv_multi,c,c,'crs' \
      -a grid_mapping,sigma0_vh_multi,c,c,'crs' \
      -a grid_mapping,sigma0_vv_norm_multi,c,c,'crs' \
      -a grid_mapping,sigma0_vh_norm_multi,c,c,'crs' \
      -a grid_mapping,sigma0_vv_single,c,c,'crs' \
      -a grid_mapping,sigma0_vh_single,c,c,'crs' \
      -a grid_mapping,sigma0_vv_norm_single,c,c,'crs' \
      -a grid_mapping,sigma0_vh_norm_single,c,c,'crs' \
      $f
done
