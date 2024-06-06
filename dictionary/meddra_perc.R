# Turn Meddra import into percolator, one query per LLM
library(dplyr)
library(jsonlite)
library(purrr)
library(elastic)
library(readr)

# Prepare percolate queries for each LLT and prep bulk file for loading
# Adjust index name as required
# Ensure mapping applied before bulk loading

llt_perc <- mdhier %>%
  filter(primary_soc_fg == "Y") %>%
  left_join(llt %>% filter(current == "Y")) %>%
  mutate(perc_doc = sprintf('{"index":{"_index":"meddra_perc_test2"}}
                            {"soc_name": "%s","soc_code": "%s","hlgt_name": "%s","hlgt_code": "%s","hlt_name": "%s","hlt_code": "%s","pt_name": "%s","pt_code": "%s","query": {"constant_score": {"filter": {"match_phrase": {"text_input": "%s"}}}}}', soc_name, 
                            soc_code,
                            hlgt_name,
                            hlgt_code,
                            hlt_name,
                            hlt_code,
                            pt_name,
                            pt_code,
                            llt_name))
writeLines(llt_perc$perc_doc, "llt_perc.json")

# Connection details to elasticsearch, replace as required
es <- connect(host = "elastic-gate.hc.local",
               port = 80,
               transport_schema = "http")

docs_bulk(es, "llt_perc.json", index= "meddra_perc_test2")
                   
# Load test documents                   
groundtruth <- read_csv("~/llmtaskforce-standardizedner/data/groundtruth_extracted.csv")

# Prepare queries for each text input, perform percolate queries and put response objects into perc_resp
ground_truth_perc <- groundtruth %>%
                    mutate(body = sprintf('{
  "query": {
    "percolate": {
      "field": "query",
      "document": {
        "text_input": "%s"
      }
    }
  }
}', text),
perc_resp = map(body, ~Search(es, index = "meddra_perc_test2", body = .x))
)

# Parse response objects
gt <- ground_truth_perc %>% 
  mutate(meddra_pts = map(perc_resp, "hits") %>% 
           map("hits") %>%
           map_depth(2, "_source") %>%
           map_depth(2, "pt_name") %>%
           map_chr(str_flatten, collapse = ", "),
         meddra_llts = map(perc_resp, "hits") %>%
           map("hits") %>%
           map_depth(2, "_source") %>%
           map_depth(2, "query") %>%
           map_depth(2, "constant_score") %>%
           map_depth(2, "filter") %>%
           map_depth(2, "match_phrase") %>%
           map_depth(2, "text_input") %>%
           map_chr(str_flatten, collapse = ", ")) %>%
  select(-perc_resp, -body)
