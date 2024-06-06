The files in this folder were used to implement an elasticsearch percolate filter for MedDRA Low Level Terms (LLTs).

https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-percolate-query.html

https://spinscale.de/posts/2021-09-15-understanding-elasticsearch-percolate-query.html

This results in extremely efficient dictionary labelling for arbitrary text passages.

Setting up a percolate index on elasticsearch for meddra is done with the meddra_perc_mapping.json file

The meddra_import_asc.R script will read meddra ASCII distribution files

