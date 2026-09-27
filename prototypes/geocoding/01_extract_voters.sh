#!/usr/bin/env bash
# Convert the NCSBE snapshot (UTF-16 LE, tab-delimited; see layout_VR_Snapshot.txt) to a
# UTF-8 TSV holding only the columns this study needs. Names, phone and mailing address
# are dropped here and never reach later steps. Records end in CRLF; a few fields hold a
# bare LF, which becomes a space.
#   columns: 1 snapshot_dt 2 county_id 3 county_desc 4 voter_reg_num 5 ncid 6 status_cd
#   8 reason_cd 16-26 residential address, 36 race_code 38 ethnic_code 40 party_cd 44 age
#   46 registr_dt 47 precinct_abbrv 49 municipality_abbrv 85 confidential_ind
#   86 cancellation_dt 87 vtd_abbrv
set -euo pipefail
DATA=${DATA:-$HOME/Programming/nc-voter-data}
iconv -f UTF-16 -t UTF-8 "$DATA/VR_Snapshot_20241105.txt" \
  | perl -e '$/ = "\r\n"; while (<>) { chomp; s/[\r\n]/ /g; print "$_\n" }' \
  | cut -f1-6,8,16-26,36,38,40,44,46,47,49,85,86,87 \
  > "$DATA/snapshot_cols.tsv"
wc -l "$DATA/snapshot_cols.tsv"
