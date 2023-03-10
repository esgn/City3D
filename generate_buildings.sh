#!/usr/bin/env bash

cat params.csv | parallel --timeout 60 --colsep ',' -j $(nproc) ./Release/bin/CLI_IGN_LIDAR_Footprints {1} {2} {3}
