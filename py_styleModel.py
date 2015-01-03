import sqlite3
import nltk
from nltk import FreqDist
import math
import time
import datetime
from scipy import stats
import numpy as np
from numpy import matrix
from matplotlib.mlab import PCA
import random
import re

db = sqlite3.connect('py_style.db')

class Corpus(object):
    def __init__(self, corpus_id):
        self.corpus_vars = {"corpus_title": None, "corpus_member_ids": [], "corpus_member_titles": []}
        self.corpus_id = corpus_id
        self.get_title()
        self.get_members()
    
    def timestamp(self):
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_')
    
    def bootstrapped_docs_finder(self):
        cursor = db.cursor()
        self.bootstrapped_ids = []
        for i in self.corpus_vars["corpus_member_ids"]:
            c = cursor.execute('SELECT doc_id, bootstrap FROM metadata WHERE doc_id = (?)', (i,))
            for j in c:
                if j[1] == 1:
                    self.bootstrapped_ids.append(i)
        
    def get_title(self):
        #make a query based upon corpus_id
        cursor = db.cursor()
        c = cursor.execute('SELECT corpus_title FROM corpus WHERE corpus_id = (?)', (self.corpus_id,))
        # set as self.corpus_title
        for i in c:
            self.corpus_vars["corpus_title"] = i[0]
    def get_members(self):
        #make a query based upon corpus_id
        cursor = db.cursor()
        c = cursor.execute('SELECT corpus_doc.corpus_id, corpus.corpus_title, corpus_doc.doc_id, metadata.doc_title FROM corpus_doc LEFT JOIN corpus ON corpus.corpus_id = corpus_doc.corpus_id LEFT JOIN metadata ON metadata.doc_id = corpus_doc.doc_id WHERE corpus.corpus_id = (?) ORDER BY corpus.corpus_id', (self.corpus_id, ))
        #set as self.corpus_member_ids
        for i in c:
            self.corpus_vars["corpus_member_ids"].append(i[2])
            self.corpus_vars["corpus_member_titles"].append(str(i[3]))
    def values_getter(self, test_type):
        #build up a tuple of doc_id, doc_title, author_surname, author_first_middle, value
        test_values = []
        cursor = db.cursor()
            #add this tuple to a list of all tuples
        if test_type == "Type-Token Ratio":
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    doc_values = (i[0], i[1], i[2], i[3], i[4])
                    test_values.append(doc_values)
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", test_type]
        elif test_type == "Hapax Dislegomena":
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    doc_values = (i[0], i[1], i[2], i[3], i[5])
                    test_values.append(doc_values)
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", test_type]
        elif test_type == "Honore's R":
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    doc_values = (i[0], i[1], i[2], i[3], i[6])
                    test_values.append(doc_values)
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", test_type]
        elif test_type == "Yule's K":
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    doc_values = (i[0], i[1], i[2], i[3], i[7])
                    test_values.append(doc_values)
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", test_type]
        elif test_type == "T, H, R, and K":
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    doc_values = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                    test_values.append(doc_values)
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", "T", "H", "R", "K"]
        elif test_type == "Lexical Richness PCA":
            metadata_values = []
            pca_values = []
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    metadata = [i[0], i[1], i[2], i[3]]
                    doc_values = [i[4], i[5], i[6], i[7]]
                    pca_values.append(doc_values)
                    metadata_values.append(metadata)
                    self.metadata_values = metadata_values
            pca_results = self.run_pca(pca_values)
            test_values = self.pca_results_getter(pca_results)
            pca_variances_covered = pca_results.fracs.tolist()
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", "PC1: " + str(int(pca_variances_covered[0]*100)) + "%", "PC2: " + str(int(pca_variances_covered[1]*100)) + "%"]
        elif test_type == "Lexical Richness PCA with Bootstrap":
            metadata_values = []
            pca_values = []
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle, t, h, r, k FROM metadata LEFT JOIN thrk ON metadata.doc_id = thrk.doc_id WHERE metadata.doc_id = (?)', (i,))
                for i in c:
                    doc_values = [i[4], i[5], i[6], i[7]]
                    pca_values.append(doc_values)
                    if i[0] == self.corpus_vars["corpus_member_ids"][0]:
                        metadata = [i[1], i[2]]
                        metadata_values.append(metadata)
            len1 = len(self.set1) + 1
            len2 = len(self.set2) + 1
            self.set1 = pca_values[1:len1]
            self.set2 = pca_values[len1:len1+len2]
            bootstrap_output1 = self.bootstrap(self.set1, self.number_of_samples1, self.sample_size1)
            bootstrap_output2 = self.bootstrap(self.set2, self.number_of_samples2, self.sample_size2)
            count = 1
            while count<=len(bootstrap_output1):
                metadata = [self.set1_name + "_" + str(count), self.set1_name]
                metadata_values.append(metadata)
                count += 1
            count = 1
            while count<=len(bootstrap_output2):
                metadata = [self.set2_name + "_" + str(count), self.set2_name]
                metadata_values.append(metadata)
                count += 1
            self.metadata_values = metadata_values
            pca_values = [pca_values[0]]
            pca_values.extend(bootstrap_output1)
            pca_values.extend(bootstrap_output2)
            pca_results = self.run_pca(pca_values)
            test_values = self.pca_results_getter(pca_results)
            test_values_with_thrk = []
            for i, k in enumerate(test_values):
                test_list = list(test_values[i])
                pca_list = list(pca_values[i])
                test_list.extend(pca_list)
                test_tuple = tuple(test_list)
                test_values_with_thrk.append(test_tuple)
            test_values = test_values_with_thrk
            pca_variances_covered = pca_results.fracs.tolist()
            test_header = ["Title", "Author/Identifier", "PC1: " + str(int(pca_variances_covered[0]*100)) + "%", "PC2: " + str(int(pca_variances_covered[1]*100)) + "%", "T", "H", "R", "K"]
        elif test_type == "Function Word PCA":
            metadata_values = []
            for i in self.corpus_vars["corpus_member_ids"]:
                c = cursor.execute('SELECT metadata.doc_id, doc_title, author_lastname, author_first_middle FROM metadata WHERE doc_id = (?)', (i,))
                for i in c:
                    metadata = [i[0], i[1], i[2], i[3]]
                    metadata_values.append(metadata)
                    self.metadata_values = metadata_values
            pca_values = self.doc_freq_for_words(50, test_type)
            pca_results = self.run_pca(pca_values)
            test_values = self.pca_results_getter(pca_results)
            pca_variances_covered = pca_results.fracs.tolist()
            test_header = ["Doc ID", "Title", "Author Last Name", "FM", "PC1: " + str(int(pca_variances_covered[0]*100)) + "%", "PC2: " + str(int(pca_variances_covered[1]*100)) + "%"]
        elif test_type == "Burrows's Delta":
            disp_id = self.corpus_vars["corpus_member_ids"][0]
            c = cursor.execute('SELECT doc_title FROM metadata WHERE doc_id = (?)', (disp_id,))
            for i in c:
                disp_title = i[0]
            freq_tuples = self.doc_freq_for_words(30, test_type)
            delta_tuples = self.delta_tuples_getter(freq_tuples)
            delta1, delta2 = self.delta_calculator(delta_tuples)
            test_values = [(disp_title, delta1, delta2)]
            test_header = ["Disputed Text", self.set1_name + " Delta", self.set2_name + " Delta"]
            #function that makes new list of tuples, should be len3 with each item len30
        return test_values, test_header
    def send_set_data(self, set1_length, set2_length, set1_name, set2_name):
        self.set1_length = set1_length
        self.set2_length = set2_length
        self.set1_name = set1_name
        self.set2_name = set2_name
  
    def send_bootstrap_data(self, set1, set2, set1_name, set2_name, number_of_samples1, sample_size1, number_of_samples2, sample_size2):
        self.set1 = set1
        self.set2 = set2
        self.set1_name = set1_name
        self.set2_name = set2_name
        self.number_of_samples1 = number_of_samples1
        self.sample_size1 = sample_size1
        self.number_of_samples2 = number_of_samples2
        self.sample_size2 = sample_size2
    def delta_calculator(self, delta_values):
        set1_abs_diffs = []
        set2_abs_diffs = []
        for i, k in enumerate(delta_values[0]):
            abs_diff1 = abs(delta_values[1][i]-k)
            abs_diff2 = abs(delta_values[2][i]-k)
            set1_abs_diffs.append(abs_diff1)
            set2_abs_diffs.append(abs_diff2)
        set1_delta = sum(set1_abs_diffs) / len(set1_abs_diffs)
        set2_delta = sum(set2_abs_diffs) / len(set2_abs_diffs)
        return set1_delta, set2_delta
    def run_pca(self, list_of_tuples):
        ztest_values = self.zscore_calculator(list_of_tuples)
        ztest_list = []
        for i in range(0, len(list_of_tuples)):
            ztest_list.append([])
        for i, k in ztest_values.iteritems():
            for n, x in enumerate(k):
                ztest_list[n].append(x)
        ztest_values_matrix = matrix(ztest_list)
        pca_results = PCA(ztest_values_matrix)
        return pca_results
    def delta_tuples_getter(self, list_of_tuples):
        zfreqs = self.zscore_calculator(list_of_tuples)
        disputed_zfreqs = []
        set1_zfreqs = []
        set2_zfreqs = []
        for i in zfreqs:
            disputed_zfreqs.append(zfreqs[i][0])
            set1_zfreqs_avg = sum(zfreqs[i][1:self.set1_length+1]) / self.set1_length
            set1_zfreqs.append(set1_zfreqs_avg)
            set2_zfreqs_avg = sum(zfreqs[i][self.set1_length + 1: len(zfreqs[i])]) / self.set2_length
            set2_zfreqs.append(set2_zfreqs_avg)
        delta_values = [tuple(disputed_zfreqs), tuple(set1_zfreqs), tuple(set2_zfreqs)]
        return delta_values
    def zscore_calculator(self, list_of_tuples):
        data = {}
        zdata = {}
        for j, k in enumerate(list_of_tuples[0]):
            data[j] = []
        for i in list_of_tuples:
            for j, k in enumerate(i):
                data[j].append(k)
        for i in data:
            i_matrix = matrix(data[i])
            zi_matrix = stats.zscore(i_matrix, axis=1, ddof=1)
            zi = zi_matrix.tolist()[0]
            zdata[i]=zi
        return zdata
    def pca_results_getter(self, pca_results):
        formatted_pcas = []
        pca_remappings = pca_results.Y.tolist()
        pca_x = []
        pca_y = []
        for i in pca_remappings:
            pca_x.append(i[0])
            pca_y.append(i[1])
        for i, k in enumerate(self.metadata_values):
            formatted_pcas.append(k)
            formatted_pcas[i].append(pca_x[i])
            formatted_pcas[i].append(pca_y[i])
        return formatted_pcas
    def freq_for_sets(self, list_of_tuples):
        pass
        #need to know which docs associated with set 1 & set 2
    def doc_freq_for_words(self, num_words, test_name):
        top_words = self.top_words_from_corpus(num_words, test_name)
        list_of_freq_tuples = []
        for i in self.corpus_vars["corpus_member_ids"]:
            title = 'document_' + str(i)
            doc_freqs = []
            doc_fdist = Library.document_instances[title].fdist
            for i in top_words:
                doc_freqs.append(doc_fdist.freq(i))
            doc_values = tuple(doc_freqs)
            list_of_freq_tuples.append(doc_values)
        return list_of_freq_tuples
    
    def top_words_from_corpus(self, num_words, test_name):
        corpus_tokens = []
        for i in self.corpus_vars["corpus_member_ids"]:
            title = 'document_' + str(i)
            doc_tokens = Library.document_instances[title].metadata["tokenized_doc"]
            corpus_tokens += doc_tokens
        top_words = []
        fdist_corpus = FreqDist(corpus_tokens)
        fdist_list = fdist_corpus.items()
        if test_name == "Function Word PCA":
            function_pos = ['IN', 'TO', 'CC', 'DT', 'PDT', 'WDT']
            for i in fdist_list:
                top_words.append(i[0])
                if len(top_words) == num_words:
                    tagged_top = nltk.pos_tag(top_words)
                    for j,k in tagged_top:
                        if k not in function_pos:
                            top_words.remove(j)
                    if len(top_words) == num_words:
                        break
        elif test_name == "Burrows's Delta":
            for i in fdist_list:
                top_words.append(i[0])
                if len(top_words) == num_words:
                    break
        return top_words
    
    def bootstrap(self, list_of_tuples, number_of_samples, sample_size):
        bootstrapped_output = []
        length = int(.01 * sample_size * len(list_of_tuples))
        """for y in range(number_of_samples):
            random_values = []
            for x in range(0, length):
                inner_random_values = []
                for i, k in enumerate(list_of_tuples[0]):
                    random_number = random.randint(1,len(list_of_tuples)) - 1
                    inner_random_values.append(list_of_tuples[random_number][i])
                random_values.append(inner_random_values)
                """
        for y in range(number_of_samples):
            random_means = []
            for i, k in enumerate(list_of_tuples[0]):
                random_values = []
                for x in range(0, length):
                    random_number = random.randint(1,len(list_of_tuples)) - 1
                    random_values.append(list_of_tuples[random_number][i])
                random_values_sum = sum(random_values)/length
                random_means.append(random_values_sum)
            random_means = tuple(random_means)
            bootstrapped_output.append(random_means)      
        return bootstrapped_output
    
    def chunking_doc_factory(self, chunk_size, chunk_title, token_set):
        #loop through token set, create chunks of the appropriate size until our of tokens
        #each chunk becomes a new document and a tokenization
        """ Yield successive n-sized chunks from l."""
        output = []
        for i in xrange(0, len(token_set), chunk_size):
                output.append(token_set[i:i+chunk_size])
        new_doc_ids = []
        # loop through bootstrapped output. For each, add a doc to the library, and a tokenization
        for i,k in enumerate(output):
            doc_title = chunk_title+"chunk_"+str(i+1)
            #call constructor to create in db and return its doc_id
            doc_id = self.doc_constructor(doc_title, k)
            #add it to a list of doc_ids
            new_doc_ids.append(doc_id)
        
        #pass document_ids and a generated corpus title to corpus creator, create new corpus in db, returns corpus_id
        corpus_title = "chunked_corpus_"+chunk_title
        db.commit()
        #returns list and string
        return new_doc_ids, corpus_title
        #return 
    
    def bootstrap_doc_factory(self, number_of_samples, sample_size, bootstrap_title):
        #convert document_list to token_set
        token_set = []
        new_doc_ids = []
        for i in self.corpus_vars["corpus_member_ids"]:
            title = 'document_' + str(i)
            doc_tokens = Library.document_instances[title].metadata["tokenized_doc"]
            token_set += doc_tokens
        bootstrapped_output = self.bootstrap(token_set, number_of_samples, sample_size)      
        # loop through bootstrapped output. For each, add a doc to the library, and a tokenization
        for i,k in enumerate(bootstrapped_output):
            doc_title = bootstrap_title+"_"+str(i+1)
            #call constructor to create in db and return its doc_id
            doc_id = self.doc_constructor(doc_title, k)
            #add it to a list of doc_ids
            new_doc_ids.append(doc_id)
        #pass document_ids and a generated corpus title to corpus creator, create new corpus in db, returns corpus_id
        corpus_title = bootstrap_title
        db.commit()
        #returns list and string
        return new_doc_ids, corpus_title
    
    
    #removes unicode punctuation
    def remove_punctuation(self, text):
        return re.sub(ur"\p{P}+", "", text)
    
    #strips apostrophes
    def apostrophe_strip(self, input):
        try:
            input = input.replace("'","")
            input = input.replace(",","")
            input = input.replace(".","")
            input = input.replace(";","")
            input = input.replace("[","")
            input = input.replace("]","")
            return input
        except:
            pass
        
    #removes punctuation tokens
    def tokenize_prep(self, token):
        for i in token:
            if i.isalpha()==False:
                token.remove(i)
        return token
    
    def text_file_to_tokens(self, user_file):    
        with open (user_file, "r") as my_file:
            text=my_file.read()
        
        if not text:
            print "User selected text file must contain at least one word"
            processed_tokens = False
            return processed_tokens
        
        #windows_codes = {"'":"\xe2\x80\x98", "'":"\xe2\x80\x99", """: "\xe2\x80\x9c", """:"\xe2\x80\x9d", "-":"\xe2\x80\x93", "--":"\xe2\x80\x94", "...":"\xe2\x80\xa6"}
        text = text.replace("\\xe2\\x80\\x94", " ")
        text = text.replace("\\xe2\\x80\\xa6", "...")
        text = text.replace("\\xe2\\x80\\x93", "-")
        
        text = self.remove_punctuation(text)
        
        #text = remove_non_ascii_1(text)
        text = text.decode('unicode_escape').encode('ascii','ignore')
        #text = text.decode('unicode_escape').encode('utf-8','ignore')
        
        #redefine text with apostrophes removed via function and all letters lowercased
        text = self.apostrophe_strip(text).lower()
        
        #tokenize the words in the function, making a list of the words
        token = nltk.word_tokenize(text)
        
        #for loop that will remove non-alphabetical values
        token = self.tokenize_prep(token)
        processed_tokens = token
        
        return processed_tokens
    
    def doc_constructor(self, doc_title, tokenized_text, last_name=None, first_middle=None):
        #Takes document title and text as input and returns an automatically generated document ID
        if not last_name:
            last_name = "None"
        if not first_middle:
            first_middle = "None"
        if not doc_title:
            current_time = str(self.timestamp())
            doc_title = "user_added_document_" + current_time
        cursor = db.cursor()
        cursor.execute('INSERT INTO metadata (doc_id, doc_title, author_lastname, author_first_middle) values (?, ?, ?, ?)', (None, doc_title, last_name, first_middle))
        c = cursor.execute('SELECT doc_id, doc_title FROM metadata WHERE doc_id = (SELECT MAX(doc_id) FROM metadata) LIMIT 1')
        for i in c:
            doc_id = i[0]
        title = "document_" + str(doc_id)
        #create table for new document tokens
        cursor.execute('CREATE TABLE {}(token text not null)'.format(title))
        
        for i in tokenized_text:
            statement = 'INSERT INTO ' + title + ' (token) values (?)'
            cursor.execute(statement, (i,))
        
        db.commit()
        return doc_id
#Class for document ... holds metadata, tokenized text, methods for all document level tests, variables that store test results, initializes by running methods to set all variables
class Document(object):
    def __init__(self, doc_id):
        #rename metadata something more general?
        self.metadata = { "doc_title": None, "author_lastname": None, "author_first_middle": None, "year_written": None, "year_published": None,
                "pub_title": None, "pub_type": None, "Type-Token Ratio": None, "Hapax Dislegomena": None, "Honore's R": None, "Yule's K": None, "tokenized_doc": []}
        self.doc_id = doc_id
        self.fdist = None
        self.frequencies = []
        self.metadata_getter()
        self.tokenized_doc_getter() 
        self.thrk_getter()
        self.frequency_dist_getter()
        #method?
        #self.timestamp()
    
    def timestamp(self):
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_')
        
    def metadata_getter(self):
        # move to object?
        cursor = db.cursor()
        c = cursor.execute('SELECT author_lastname, author_first_middle, doc_title, original_publication_title, original_publication_type, year_written, year_published FROM metadata WHERE doc_id = (?)', (self.doc_id,))
        for row in c:
            self.metadata["author_lastname"] = row[0]
            self.metadata["author_first_middle"] = row[1]
            self.metadata["doc_title"] = row[2]
            self.metadata["pub_title"] = row[3]
            self.metadata["pub_type"] = row[4]
            self.metadata["year_written"] = row[5]
            self.metadata["year_published"] = row[6]
        #print "Metadata Found for Doc ", (self.doc_id)
        
    def tokenized_doc_getter(self):
        #assumes we're connected to db
        doc_name = 'document_' + str(self.doc_id) 
        cursor = db.execute('SELECT * FROM {}'.format(doc_name,))
        text = []
        for i in cursor:
            text.append(str(i[0]))
            self.metadata["tokenized_doc"] = text
        #print "Tokenized Document ", (self.doc_id)
    
    def type_token_ratio(self):
        self.metadata["Type-Token Ratio"] = float(self.V / self.N)
        
    def hap_dis_ratio(self):
        self.metadata["Hapax Dislegomena"] = float(self.hapaxes[2] / self.V)
        #assignments can go in methods
    
    def honore_r(self):
        if self.hapaxes[1] != 0:
            self.metadata["Honore's R"] = float((100*math.log(self.N, 10)) / (1 - (self.hapaxes[1] / self.V)))
        else:
            self.metadata["Honore's R"] = 'NA'

    def yule_k(self):
        #we find the value of the greatest number of times any word appears
        summation = []
        for i in self.hapaxes:
            summation.append(float(i**2 * self.hapaxes[i]))
        #with the summation, find K
        self.metadata["Yule's K"] = float((10**4 * (sum(summation) - self.N)) / (self.N**2))

    def frequency_dist(self):
        self.fdist = FreqDist(self.metadata["tokenized_doc"])
    
    def frequency_dist_getter(self):
        if self.fdist == None:
            self.frequency_dist()
        self.frequencies = self.fdist.items()
                
    def hapaxes_summation(self):
        self.frequency_dist()
        max = self.fdist[self.fdist.max()]
        # hapaxes method (only gets called if you hit else here)
        hapaxes = {}
        for n in range(1, max+1):
            hapaxes[n] = 0
        for i in self.fdist:
            hapaxes[self.fdist[i]] += 1
        self.hapaxes = hapaxes
    
    def thrk_getter(self):
        cursor = db.cursor()
        c = cursor.execute('SELECT doc_id, t, h, r, k FROM thrk WHERE doc_id = (?)', (self.doc_id,))
        count = 0
        for i in c:
            count +=1
        if count > 0:
            c = cursor.execute('SELECT doc_id, t, h, r, k FROM thrk WHERE doc_id = (?)', (self.doc_id,))
            for i in c:
                self.metadata["Type-Token Ratio"] = i[1]
                self.metadata["Hapax Dislegomena"] = i[2]
                self.metadata["Honore's R"] = i[3]
                self.metadata["Yule's K"] = i[4]
        else:
            self.hapaxes_summation()    
            # make these instance variables
            self.N = float(self.fdist.N())
            self.V = float(len(self.fdist))
            
            #Just call these
            self.type_token_ratio()
            self.hap_dis_ratio()
            self.honore_r()
            self.yule_k()
            cursor.execute('INSERT INTO thrk (doc_id, t, h, r, k) VALUES (?, ?, ?, ?, ?)', (self.doc_id, self.metadata["Type-Token Ratio"], self.metadata["Hapax Dislegomena"], self.metadata["Honore's R"], self.metadata["Yule's K"]))
            db.commit()

"""
BEGIN LIBRARY OBJECT CLASSES
"""

class Library(object):
    document_instances = {}
    corpus_instances = {}
    bootstrap_instances = {}
    
    def __init__(self):
        # instantiate all documents
        self.docs_from_db()
        # instantiate all corpora
        self.corpora_from_db()
        # self.bootstraps_from_db()
    
    def timestamp(self):
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_') 
    
    def docs_from_db(self):
        #code to initialize objects for all documents in DB
        cursor = db.cursor()
        c = cursor.execute('SELECT doc_id FROM metadata')
            #removed WHERE bootstrap=0 from query
        for i in c:
            name = "document_"+str(i[0])
            self.document_instances[name] = Document(i[0])
            
    def bootstraps_from_db(self):
        #code to initialize objects for all documents in DB
        cursor = db.cursor()
        c = cursor.execute('SELECT doc_id FROM metadata WHERE bootstrap=1')
        for i in c:
            name = "document_"+str(i[0])
            self.bootstrap_instances[name] = Document(i[0])
    
    def corpora_from_db(self):
        #code to initialize objects for all corpora in DB
        cursor = db.cursor()
        c = cursor.execute('SELECT corpus_id FROM corpus')
        for i in c:
            name = "corpus_"+str(i[0])
            self.corpus_instances[name] = Corpus(i[0])
    
    def doc_fetcher(self):
        #loop through instances
        output_list = []
        for i, k in self.document_instances.iteritems():
            data_list = [self.document_instances[i].doc_id, self.document_instances[i].metadata["author_lastname"], self.document_instances[i].metadata["author_first_middle"], self.document_instances[i].metadata["doc_title"]]
            output_list.append(data_list)
        return output_list

    def corpora_fetcher(self):
        #loop through instances
        output_list = []
        for i, k in self.corpus_instances.iteritems():
            # dictionary full of corpus instances, had an instance variable with a list of all member ids and titles
            documents_list = '--'.join(self.corpus_instances[i].corpus_vars["corpus_member_titles"])
            data_list = [self.corpus_instances[i].corpus_id, self.corpus_instances[i].corpus_vars["corpus_title"], str(documents_list[0:50]) + " ..."]
            output_list.append(data_list)
        return output_list
    
    def corpus_constructor_temporary(self, documents):
        if not documents:
            corpus_id = 0
            return corpus_id
        
        cursor = db.cursor()
        cursor.execute('INSERT INTO corpus (corpus_id, corpus_title) values (?, ?)', (None, 'temporary'))
        c = cursor.execute('SELECT corpus_id FROM corpus WHERE corpus_title="temporary"')
        for i in c:
            corpus_id = i[0]
        for k in documents:
            cursor.execute('INSERT INTO corpus_doc (corpus_id, doc_id) values (?,?)', (corpus_id, k))
        return corpus_id
    
    def corpus_constructor_and_commit(self, documents, corpus_title):
        cursor = db.cursor()
        if not corpus_title:
            current_time = self.timestamp()
            corpus_title = "user_corpus_" + current_time
        cursor.execute('INSERT INTO corpus (corpus_id, corpus_title) values (?, ?)', (None, corpus_title))
        c = cursor.execute('SELECT corpus_id FROM corpus WHERE corpus_title=(?)', (corpus_title, ))
        for i in c:
            corpus_id = i[0]
        for k in documents:
            cursor.execute('INSERT INTO corpus_doc (corpus_id, doc_id) values (?,?)', (corpus_id, k))
        db.commit()
        return corpus_id
    
    def corpus_assassin(self, corpus_id):
        cursor = db.cursor()
        cursor.execute('DELETE FROM corpus WHERE corpus_id=(?)', (corpus_id,))
        cursor.execute('DELETE FROM corpus_doc WHERE corpus_id=(?)', (corpus_id,))
        db.commit()
        
    def document_assassin(self, doc_id):
        cursor = db.cursor()
        doc_title = 'document_' + str(doc_id)
        cursor.execute('DELETE FROM metadata WHERE doc_id=(?)', (doc_id,))
        cursor.execute('DROP TABLE {}'.format(doc_title))
        cursor.execute('DELETE FROM corpus_doc WHERE doc_id=(?)', (doc_id,))
        db.commit()
        
    def add_docs_to_corpus(self, doc_list, corpus_id):
        cursor = db.cursor()
        corpus_members = []
        row = cursor.execute('SELECT doc_id, corpus_id FROM corpus_doc WHERE corpus_id = (?)', (corpus_id, ))
        for i in row:
            corpus_members.append(i[0])
        for i in doc_list:
            if i not in corpus_members:
                cursor.execute('INSERT INTO corpus_doc (doc_id, corpus_id) values (?, ?)', (i, corpus_id))
        db.commit()
        
    