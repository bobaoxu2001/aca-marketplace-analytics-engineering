#!/bin/zsh
# Robust NYC 311 (erm2-nwe9) download for full-year 2024.
# Socrata caps a single CSV response (~230k rows) regardless of $limit, so we
# paginate: 50k-row pages, total order (created_date, unique_key) for exact,
# deterministic paging over immutable historical data. One file per month.
set -e
cd "$(dirname "$0")/monthly"
base="https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
page=50000
months=(01 02 03 04 05 06 07 08 09 10 11 12)
next=(02 03 04 05 06 07 08 09 10 11 12 13)

for i in {1..12}; do
  m=$months[$i]; nm=$next[$i]
  if [[ "$nm" == "13" ]]; then hi="2025-01-01T00:00:00"; else hi="2024-${nm}-01T00:00:00"; fi
  lo="2024-${m}-01T00:00:00"
  out="sr_2024_${m}.csv"
  tmp="${out}.part"
  : > "$tmp"
  offset=0
  pageno=0
  while true; do
    chunk="_chunk.csv"
    where="created_date%20%3E%3D%20'${lo}'%20AND%20created_date%20%3C%20'${hi}'"
    order="created_date,unique_key"
    curl -s --max-time 600 -o "$chunk" \
      "${base}?\$where=${where}&\$order=${order}&\$limit=${page}&\$offset=${offset}"
    lines=$(wc -l < "$chunk")
    data=$((lines - 1))
    if [[ $pageno -eq 0 ]]; then
      cat "$chunk" >> "$tmp"            # keep header on first page
    else
      tail -n +2 "$chunk" >> "$tmp"     # drop header on later pages
    fi
    echo "  ${out} page ${pageno} offset ${offset}: ${data} rows"
    if [[ $data -lt $page ]]; then break; fi
    offset=$((offset + page))
    pageno=$((pageno + 1))
  done
  rm -f _chunk.csv
  mv "$tmp" "$out"
  echo ">>> ${out} DONE: $(( $(wc -l < "$out") - 1 )) rows, $(du -h "$out" | cut -f1)"
done
echo "ALL MONTHS DONE"
