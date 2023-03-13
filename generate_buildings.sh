#!/usr/bin/env bash

cat params.csv | parallel --timeout 60 --colsep ',' --jobs $(nproc) --joblog city3d.log ./Release/bin/CLI_IGN_LIDAR_Footprints {1} {2} {3}
