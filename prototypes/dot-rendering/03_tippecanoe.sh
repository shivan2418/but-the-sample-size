#!/bin/sh
# Vector dot tiles with tippecanoe (felt/tippecanoe 2.82.0), built in Docker. Run in $DATA/dot-rendering.
set -e
[ -d tippecanoe ] || git clone --depth 1 https://github.com/felt/tippecanoe.git
cat > Dockerfile.tc <<'DF'
FROM ubuntu:24.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential libsqlite3-dev zlib1g-dev
COPY tippecanoe /src
WORKDIR /src
RUN make -j8 && make install
WORKDIR /data
DF
docker build -q -f Dockerfile.tc -t tc-local .
R="docker run --rm -v $PWD:/data tc-local"   # rootless Docker: run as container root
$R tippecanoe -q -f -o clt_full.pmtiles -l dots -Z8 -z14 -B14 --no-feature-limit --no-tile-size-limit clt.csv
$R tippecanoe -q -f -o nc_drop.pmtiles  -l dots -Z5 -z14 --drop-densest-as-needed nc.csv
$R tippecanoe -q -f -o nc_full12.pmtiles -l dots -Z12 -z14 -B12 --no-feature-limit --no-tile-size-limit nc.csv
$R tippecanoe -q -f -e nc_dir -l dots -Z12 -z14 -B12 --no-feature-limit --no-tile-size-limit --no-tile-compression nc.csv
