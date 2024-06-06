# Turn Meddra import into percolator, one query per LLM

library(dplyr)
library(jsonlite)
library(purrr)
library(elastic)


            
  
  llt_perc <- mdhier %>%
  filter(primary_soc_fg == "Y") %>%
  left_join(llt %>% filter(current == "Y")) %>%
  mutate(query = map(llt_name, ~ I(paste0('{"constant_score":{"filter":{"match_phrase":{"',
                                        .x,
                                        '"}}}})'))))

llt_perc_index <- llt_perc %>%
                  rowwise() %>%
                  mutate(perc_doc = toJSON(across(c(soc_name,
                                              soc_code,
                                              hlgt_name,
                                              hlgt_code,
                                              hlt_name,
                                              hlt_code,
                                              pt_name,
                                              pt_code,
                                              query)),
                                     auto_unbox = TRUE, 
                                     pretty = TRUE))

llt_perc_index_list <- llt_perc %>%
                       select(soc_name,
                                                           soc_code,
                                                           hlgt_name,
                                                           hlgt_code,
                                                           hlt_name,
                                                           hlt_code,
                                                           pt_name,
                                                           pt_code,
                                                           query) %>%
                       mutate_if(is.numeric, as.character)



library(elastic)
es <- connect(host = "elastic-gate.hc.local",
               port = 80,
               transport_schema = "http")

 docs_bulk(es, "llt_perc.json", index= "meddra_perc_test2")
                   
                   
test <- list(constant_score = list(filter = list(match_phrase = list(text_input = "Anaemia folate deficiency"))) )

PUT /meddra_perc_test2
{
  "mappings": {
    "properties": {
      "text_input": {
        "type": "text"
      },
      "query": {
        "type": "percolator"
      },
      "soc_name": {
        "type": "keyword"
      },
      "soc_code": {
        "type": "keyword"
      },
      "hlgt_name": {
        "type": "keyword"
      },
      "hlgt_code": {
        "type": "keyword"
      },
      "hlt_name": {
        "type": "keyword"
      },
      "hlt_code": {
        "type": "keyword"
      },
      "pt_name": {
        "type": "keyword"
      },
      "pt_code": {
        "type": "keyword"
      }
    }
  }
            }  
  
            
{
  "constant_score": {
    "filter": {
      "match_phrase": {
        "text_input": "ASC 09F"
      }
    }
  }
}


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


library(yyjsonr)

writeLines(llt_perc$perc_doc, "llt_perc.json")

library(readr)
groundtruth <- read_csv("~/llmtaskforce-standardizedner/data/groundtruth_extracted.csv")
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


ground_truth_perc$perc_resp$hits$hits
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
  select(-perc_resp)
