#* @apiTitle Sentence Splitter API

#* Split a sentence into words
#* @param sentence The sentence to split
#* @get /split
function(sentence = "") {
    words <- strsplit(sentence, " ")[[1]]
    return(list(words = words))
}
