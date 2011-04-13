from glob import glob;
from collections import defaultdict;
from nltk.probability import FreqDist;
from string import rstrip;
from os import remove, access, F_OK;

def parse_de_news_gs(glob_expression, lang="english", doc_limit= -1, max_df_percentage = 1.0, min_df_percentage = 0.0):
    docs = parse_de_news(glob_expression, lang, doc_limit, max_df_percentage, min_df_percentage);
    return docs

def parse_de_news_vi(glob_expression, lang="english", doc_limit= -1, max_df_percentage = 1.0, min_df_percentage = 0.0):
    docs = parse_de_news(glob_expression, lang, doc_limit, max_df_percentage, min_df_percentage);
    return parse_data(docs)

# compute the df counts of the given corpus
# max_df_percentage: a value between 0 to 1, upper cutoff for df is computed as document number times max_df_percentage
# min_df_percentage: a value between 0 to 1, lower cutoff for df is computed as document number times min_df_percentage
def cutoff_df_de_news(glob_expression, doc_limit= -1, max_df_percentage = 1.0, min_df_percentage = 0.0):
    from nltk.tokenize.treebank import TreebankWordTokenizer
    tokenizer = TreebankWordTokenizer()

    from string import ascii_lowercase
    files = glob(glob_expression)
    print("Found %i files" % len(files))
    
    df = FreqDist()
    doc_count = 0
    
    for ii in files:
        text = open(ii).read().lower()
        
        sections = text.split("<doc")
        
        for section in sections:
            if section != None and len(section) != 0:
                index_content = section.split(">\n<h1>\n")
                title_content = index_content[1].split("</h1>")
                # not x in stop: to remove the stopwords
                # min(y in ascii_lowercase for y in x) : to remove punctuation or any expression with punctuation and special symbols
                words = [x for x in tokenizer.tokenize(title_content[1]) if min(y in ascii_lowercase for y in x)]
    
                words = set(words)
                for word in words:
                    df.inc(word, 1)
                    
                doc_count += 1
                    
        if doc_limit > 0 and doc_count>doc_limit:
            print("Passed doc limit %i" % doc_count)
            break
    
    max_df = (doc_count*max_df_percentage)
    min_df = (doc_count*min_df_percentage)
    filtered_words = [word for word in df.keys() if df[word]>max_df or df[word]<min_df]
    print("document count %i,\tupper df cutoff %f,\tlower df cutoff %f" % (doc_count, max_df, min_df))
    print "filtered words: ", filtered_words

    return filtered_words

# this method reads in the data from wikipedia dataset/corpus
# output a dict data type, indexed by the document id, value is a list of the words in that document, not necessarily unique
# this format is generally used for gibbs sampling
def parse_wikipedia(glob_expression, lang="english", doc_limit= -1, max_df_percentage = 1.0, min_df_percentage = 0.0):
    include_id_url = False
    include_path = False
    
    from nltk.tokenize.treebank import TreebankWordTokenizer
    tokenizer = TreebankWordTokenizer()

    from nltk.corpus import stopwords
    stop = stopwords.words('english')
    if lang.lower() == "english":
        stop = stopwords.words('english')
    elif lang.lower() == "german":
        stop = stopwords.words('german')
    else:
        print "language option unspecified, default to english..."

    #filtered_words = cutoff_df_de_news(glob_expression, doc_limit, max_df_percentage, min_df_percentage)

    from string import ascii_lowercase
    docs = {}
    
    dirs = glob(glob_expression)
    for jj in dirs:
        files = glob(jj + "/*")
        print("Found %i files in directory %s" % (len(files), jj))
        
        for ii in files:
            text = open(ii).read().lower()
            sections = text.split("\n</doc>\n")
            
            for section in sections:
                if section != None and len(section) != 0:
                    tokens = section.split("\n")
                    title = rstrip(tokens[1], ".")
                    contents = " ".join(tokens[2 :])
                                        
                    # not x in stop: to remove the stopwords
                    # min(y in ascii_lowercase for y in x) : to remove punctuation or any expression with punctuation and special symbols
                    #words = [x for x in tokenizer.tokenize(contents) if (not x in stop) and (min(y in ascii_lowercase for y in x)) and (not x in filtered_words)]
                    words = [x for x in tokenizer.tokenize(contents) if (not x in stop) and (min(y in ascii_lowercase for y in x))]

                    if include_id_url:
                        docs["%s\t%s" % (tokens[0].strip(), title.strip())] = words
                    else:
                        docs["%s" % (title.strip())] = words
                
                if doc_limit > 0 and len(docs) > doc_limit:
                    print("Passed doc limit %i" % len(docs))
                    break
                
            if doc_limit > 0 and len(docs) > doc_limit:
                print("Passed doc limit %i" % len(docs))
                break
            
        if doc_limit > 0 and len(docs) > doc_limit:
            print("Passed doc limit %i" % len(docs))
            break
    
    return docs

# this method reads in the data from wikipedia dataset/corpus
# output a dict data type, indexed by the document id, value is a list of the words in that document, not necessarily unique
# this format is generally used for gibbs sampling
def output_wikipedia(glob_expression, output_path, lang="english", doc_limit= -1, max_df_percentage = 1.0, min_df_percentage = 0.0):
    include_id_url = False
    include_path = False
    
    from nltk.tokenize.treebank import TreebankWordTokenizer
    tokenizer = TreebankWordTokenizer()

    from nltk.corpus import stopwords
    stop = stopwords.words('english')
    if lang.lower() == "english":
        stop = stopwords.words('english')
    elif lang.lower() == "german":
        stop = stopwords.words('german')
    else:
        print "language option unspecified, default to english..."

    #filtered_words = cutoff_df_de_news(glob_expression, doc_limit, max_df_percentage, min_df_percentage)

    if access(output_path, F_OK):
        remove(output_path);

    from string import ascii_lowercase
    docs = {}

    parsed_docs = 0    
    dirs = glob(glob_expression)
    for jj in dirs:
        files = glob(jj + "/*")
        print("Found %i files in directory %s" % (len(files), jj))
        
        for ii in files:
            text = open(ii).read().lower()
            sections = text.split("\n</doc>\n")
            
            for section in sections:
                if section != None and len(section) != 0:
                    tokens = section.split("\n")
                    title = rstrip(tokens[1], ".")
                    contents = " ".join(tokens[2 :])
                                        
                    # not x in stop: to remove the stopwords
                    # min(y in ascii_lowercase for y in x) : to remove punctuation or any expression with punctuation and special symbols
                    #words = [x for x in tokenizer.tokenize(contents) if (not x in stop) and (min(y in ascii_lowercase for y in x)) and (not x in filtered_words)]
                    words = [x for x in tokenizer.tokenize(contents) if (not x in stop) and (min(y in ascii_lowercase for y in x))]

                    if include_id_url:
                        docs["%s\t%s" % (tokens[0].strip(), title.strip())] = words
                    else:
                        docs["%s" % (title.strip())] = words
                        
                    parsed_docs = parsed_docs+1

                if doc_limit > 0 and parsed_docs > doc_limit:
                    print("Passed doc limit %i" % len(docs))
                    break
                
            append(docs, output_path)
            docs.clear()
                 
            if doc_limit > 0 and parsed_docs > doc_limit:
                #print("Passed doc limit %i" % len(docs))
                break
            
        if doc_limit > 0 and parsed_docs > doc_limit:
            #print("Passed doc limit %i" % len(docs))
            break
        
    return parsed_docs
    
def append(docs, file):
    f = open(file, "a")
    
    for doc in docs.keys():
        f.write(doc)
        f.write("\t" + " ".join(docs[doc]))
        f.write("\n")

# this method convert a corpus into proper format for training lda model for variational inference
# output a defaultdict(dict) data type, first indexed by the document id, then indexed by the unique tokens
# corpus: a dict data type, indexed by document id, corresponding value is a list of words (not necessarily unique from each other)
def parse_data(corpus):
    docs = defaultdict(dict)
    
    for doc in corpus.keys():
        content = {}
        for term in corpus[doc]:
            if term in content.keys():
                content[term] = content[term] + 1
            else:
                content[term] = 1
        docs[doc] = content
    
    return docs

if __name__ == "__main__":
    parsed_docs = output_wikipedia("/windows/d/Data/dewiki/*", "/windows/d/Data/dewiki.txt", "german",
                  -1, 0.4, 0.0001)
    print "parsed ", parsed_docs, " german documents in total..."
    
    parsed_docs = output_wikipedia("/windows/d/Data/enwiki/*", "/windows/d/Data/enwiki.txt", "english",
                  -1, 0.4, 0.0001)
    print "parsed ", parsed_docs, " english documents in total..."
    
#    data_en = parse_data(data_en)
#    data_de = parse_wikipedia("/windows/d/Data/de-news/txt/*.de.txt", "german",
#                  1, 0.4, 0.0001)
#    data_de = parse_data(data_de)
#    print len(data_en), "\t", len(data_de)
#    
#    [data_en, data_de] = map_corpus(data_en, data_de)
#    print len(data_en), "\t", len(data_de)
    
#lda.initialize(d)

#lda.sample(100)
#lda.print_topics()