#Meddra distribution import

library(data.table)

pt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/pt.asc", 
            sep = "$", 
            select = c(1, 2, 4),
            col.names = c("pt_code", "pt_name", "soc_code"))

pt_fr <- fread("~/meddra/meddra_26_1/meddra_26_1_fr/ascii-261/pt.asc", 
            sep = "$", 
            select = c(1, 2, 4),
            encoding = "Latin-1",
            col.names = c("pt_code", "pt_term_fr", "soc_code"))

hlt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/hlt.asc", 
          sep = "$", 
          select = c(1, 2),
          col.names = c("hlt_code", "hlt_name"))

hlgt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/hlgt.asc", 
             sep = "$", 
             select = c(1, 2),
             col.names = c("hlgt_code", "hlgt_name"))

hlt_pt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/hlt_pt.asc", 
            sep = "$", 
            select = c(1, 2),
            col.names = c("hlt_code", "pt_code"))

hlgt_hlt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/hlgt_hlt.asc", 
                sep = "$", 
                select = c(1, 2),
                col.names = c("hlgt_code", "hlt_code"))

soc <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/soc.asc", 
            sep = "$", 
            select = c(1, 2, 3),
            col.names = c("soc_code", "soc_name", "soc_abbrev"))

soc_fr <- fread("~/meddra/meddra_26_1/meddra_26_1_fr/ascii-261/soc.asc", 
             sep = "$", 
             select = c(1, 2, 3),
             encoding = "Latin-1",
             col.names = c("soc_code", "soc_name_fr", "soc_abbrev_fr"))


soc_hlgt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/soc_hlgt.asc", 
                  sep = "$", 
                  select = c(1, 2),
                  col.names = c("soc_code", "hlgt_code"))

mdhier <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/mdhier.asc",
                sep = "$",
                drop = c(10, 13),
                col.names = c("pt_code",
                              "hlt_code",
                              "hlgt_code",
                              "soc_code",
                              "pt_name",
                              "hlt_name",
                              "hlgt_name",
                              "soc_name",
                              "soc_abbrev",
                              "pt_soc_code",
                              "primary_soc_fg"))

llt <- fread("~/meddra/meddra_26_1/meddra_26_1_en/MedAscii/llt.asc", 
            sep = "$", 
            select = c(1, 2, 3, 10),
            col.names = c("llt_code", "llt_name", "pt_code", "current"),
            quote = "")

llt_fr <- fread("~/meddra/meddra_26_1/meddra_26_1_fr/ascii-261/llt.asc", 
               sep = "$", 
               select = c(1, 2, 3, 10),
               encoding = "Latin-1",
               col.names = c("llt_code", "llt_term_fr", "pt_code", "current"))
