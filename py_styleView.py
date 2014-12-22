import sqlite3
from prettytable import PrettyTable
import nltk
from nltk import FreqDist
import math
import time
import datetime
from prettytable import PrettyTable

# Menu classes
class PrettyTableMaker(object):
    def __init__(self):
        self.vars = {"alignment": "l", "width": 25, "header": [], "rows": [], "variable": None, "sortby": None}
    def make_from_rows(self):
        x = PrettyTable(self.vars["header"])
        x.align = self.vars["alignment"]
        x.max_width = self.vars["width"]
        if self.vars["sortby"] != None:
            x.sortby = self.vars["sortby"]
        for i in self.vars["rows"]:
            x.add_row(i)
        print x
    def make_and_enum(self):
        x = PrettyTable(self.vars["header"])
        x.align = self.vars["alignment"]
        x.max_width = self.vars["width"]
        if self.vars["sortby"] != None:
            x.sortby = self.vars["sortby"]
        count = 1
        for i in self.vars["rows"]:
            x.add_row([count, i])
            count += 1
        print x
    def make_from_variable(self):
        x = PrettyTable(self.vars["header"])
        x.align = self.vars["alignment"]
        x.max_width = self.vars["width"]
        if self.vars["sortby"] != None:
            x.sortby = self.vars["sortby"]
        x.add_row(self.vars["variable"])
        print x

class Menu(object):
    """A class that constructs all menu parameters."""
    items = ["Exit", "Home", "Back", "Documentation"]
    def __init__(self, **kwargs):
        self.custom_items = kwargs.get('custom_items')
        self.custom_items = self.items + self.custom_items
    def print_menu(self):
        _prettymenu = PrettyTableMaker()
        _prettymenu.vars["header"] = ["#", "Selection"]
        _prettymenu.vars["rows"] = self.custom_items
        _prettymenu.make_and_enum()
    def gather_user_input(self):
        valid_input = False
        while valid_input == False:
            try:
                user_choice_number = int(raw_input("Please make a selection (number only) and press Enter/Return: "))
                user_choice_number -= 1
                if user_choice_number in range(0, len(self.custom_items)):
                    user_choice_name = self.custom_items[user_choice_number]
                    valid_input = True
                    return user_choice_name
                else:
                    print "Make a valid selection."
                    #self.gather_user_input()
            except: 
                print "Make a valid selection."
                #self.gather_user_input()
            
class Command(object):
    descriptions = {
        "Chunking": "Chunking allows the user to divide a text (or a corpus) into smaller, more useful subsets \
                        \n Select a document or set of documents, a chunking size (number of tokens per chunk), and the subsets will be added to the library as a new corpus .",
        "Yule's K": "Yule's K measures the diversity of the vocabulary in a text. The higher the K value, the less diverse the vocabulary.",
        "Honore's R": "Honore's R measures the ratio of the number of hapax legomenon (V_1), or words used exactly once, to the number of distinct words in a text (V). \
                                \n \n This ratio is weighted against the total word count (N).",
        "Hapax Dislegomena": "H measures the ratio of the number of hapax dislegomena (V_2), or words used exactly twice, to the number of distinct words in a text (V). \
                                \n \n It is not weighted against the total word count (N) because it is stable within a large range of N values.",
        "Type-Token Ratio": "T measures the ratio of distinct words in a text (V) to the total word count (N). \
                                \n \n The closer to 1, the more diverse the vocabulary.",
        "T, H, R, and K": "T, H, R, and K runs tests for Type-Token Ratio, Hapax Dislegomena Ratio, Honore's R, and Yule's K.",
        "Lexical Richness PCA": "Lexical Richness Principal Component Analysis takes T, H, R, and K for each story and remaps the four variables for each text to two variables that cover the most variation, allowing you to map as a scatter plot in two dimensions. \
                                \n If these tests reveal differences between the corpuses and similarity amongst a corpus, the graphed points for a corpus should cluster together apart from the other corpus points. \
                                \n \n IMPORTANT: You must select at least five documents, because PCA requires more documents than variables, of which there are four for LRPCA (T, H, R, and K).",
        "Function Word PCA": "Function Word Principal Component Analysis measures the frequency of the top 50 words for each text and compares the usage between corpuses. The fifty points for each text are remapped to two points each that cover the most variation found in the original data. \
                                \n When graphed as a scatter plot, which is now two-dimensional, if there is a stylistic difference between corpuses and similarity amongst a corpus, then the graphed points for a corpus should cluster together apart from the other corpus points. \
                                \n \n IMPORTANT:You must select at least fifty-one documents, because PCA requires more documents than variables, of which there are fifty for FWPCA (the frequencies for the top 50 words).",
        "Burrows's Delta": "Burrows's Delta measures the frequency of the top 30 words for a disputed text and each text in two corpuses. It then compares the average usages for each word in each corpus and compares them to the usage in the disputed text. \
                                \n Delta is, in effect, a measure of the 'average difference' of one corpus's usage of common words from the disputed text. Thus, a smaller Delta means one corpus's style is on average 'less unlike' the style in the disputed text.",
        "View Library": "\n The Library displays a list of current documents and corpora.",
        "Add/Remove/Manage Items": "Add, Remove, or Manage the documents or corpora in your Library.",
        "Add Documents": "Add a document to the library.",
        "Remove Documents": "Remove a document from the library. If you select a corpus, then all of the documents in that corpus will be removed from the library.",
        "Create Corpus": "Create a corpus from documents in the library.",
        "Delete Corpus": "Delete a corpus from the library. This will not delete the documents from the library.", 
        "Add Documents to Corpus": "Add documents from the library to an extant corpus.",
        "Remove Documents from Corpus": "Remove documents from an extant corpus.",
        "Lexical Richness PCA with Bootstrap": "Bootstrapping is a resampling method that allows the user to assign measures of accuracy to a sample. The user inputs a set of documents and/or corpora, sample size, and number of samples. \
                                The T, H, R, and K values are resampled with replacement to provide a greater number of values for the purposes of PCA.",
        "On Library Management": """When a document is uploaded to Py_style, the program creates a tokenized version and stores Type-Token Ratio (T), Hapax Dislegomena Ratio (H), Honore's R (R), and Yule's K (K), which are lexical richness values that attempt to capture aspects of style in terms of lexical diversity and the usage of words that show up infrequently. \
                                    \n The tokenized version is created by deleting apostrophes, commas, periods, and semicolons, replacing any improperly decoded characters, running Natural Language Tool Kit's "word_tokenize()" function, and then removing any additional items in the tokenized list that are punctuation marks (http://www.nltk.org). This creates a list of only the words from the document on which T, H, R, and K are based.""",
        "On General Testing": """Each test will ask if the results should be outwritten into a file or not. Then, it will ask if the user wants to upload a document or corpus, and presents the respective library from which the user will choose what to add to the set of items being tested. Then, it will ask if the user wants to add more documents or corpora. Once the user is done selecting documents and corpora, the test will run.""",
        "On T, H, R, and K": """T, H, R, and K are calculated using NLTK's FreqDist class, which creates a frequency distribution for each word in a document's tokenized list. From here, the total token count, or total number of words (N); the total type count, or distinct number of words (V); and hapaxes can be calculated. Hapaxes refer to the count of the number of words that appear a certain number of times, so hapax dislegomena (V_2), or words that appear exactly twice, is found by finding the number of words in the frequency distribution that appear twice. The actual formulas for the lexical richness tests are as follows: \
                                \n \n T = V / N, \
                                \n H = V_2 / V, \
                                \n R = (100 * log(N)) / (1 - (V_1 / V)), \
                                \n and K = (10^4 * (S - N)) / N^2, \
                                \n \n where S is the summation of i^2 * V_i, with i running from 1 (thus making V_1 the number of hapax legomenon) up to n, with n representing the token count of the word that appears the most frequently. All of the values used to find the lexical richness variables are calculated using methods in the FreqDist class. These variables are automatically stored for each document. \
                                \n \n When T, H, R, or K is run as a test, the values are simply retrieved from the database. T and H are bound below by 0 and above by 1. R and K are bound below by 0 but not bound above.""",
        "On Lexical Richness PCA": """Lexical Richness tests attempt to capture aspects of style in terms of lexical diversity and the usage of words that show up infrequently; Lexical Richness PCA attempts to "boil down" the differences between documents and corpora based on these measurements and find stylistic differences, graphing the results on a scatter plot. If the test does find stylistic differences, the points representing documents that are close in style---say those by one author---will cluster together, whereas those that are not close---say those by another author---will not be in that cluster. If two distinct clusters show up representing two different authors and the point representing a disputed text shows up in a cluster, then that means the lexical richness style in the disputed text captured by T, H, R, and K is closer to that of the clustered document points. \
                                \n \n When the Lexical Richness PCA test is run, the variables are accessed for each document and standardized against the respective variable's mean and standard deviation for the set of all documents and corpora on which the text is being run, creating an n x 4 data matrix, in which n is the number of documents on which the test is being performed. In order for this test to run, the number of rows---in this case documents---must be greater than the number of columns---in this case the T, H, R, and K variables. Thus, there must be at least 5 documents being tested. \
                                \n \n The standardized values are found with basic Python functions and SciPy's "stats" package (http://www.scipy.org). The standardized values are put into a matrix using "NumPy"---which is another SciPy package---and then run through a PCA function from Matplotlib's "mlab" module (http://www.matplotlib.org). \
                                \n \n The process of PCA takes in a matrix of values where the columns represent variables---in this case T, H, R, and K---and finds new axes that capture the most variation in the data. The data are remapped on these axes, or principal components, creating a scatter plot. \
                                \n \n The axes are found and the data remapped in the "mlab" module, but the mathematical process behind it is as follows: a correlation matrix is formed containing the Pearson's r values that describe the correlation between two columns. The eigenvectors and eigenvalues of the correlation matrix are found, with the eigenvectors representing the principal components and the eigenvalues allowing for the calculation of the percent of variation in the original data covered by the respective principal component (found by taking the respective eigenvalue and dividing it by the sum of all of the eigenvalues).""",
        "On Function Word PCA": """Function Word measurements attempt to capture aspects of style in terms of function word usage, namely function words that show up the most frequently; Function Word PCA attempts to "boil down" the differences between documents and corpora based on these measurements and find stylistic differences, graphing the results on a scatter plot. If the test does find stylistic differences, the points representing documents that are close in style----say those by one author---will cluster together, whereas those that are not close---say those by another author---will not be in that cluster.  If two distinct clusters show up representing two different authors and the point representing a disputed text shows up in a cluster, then that means the style in the disputed text captured by commonly used function word frequencies is closer to that of the clustered document points.\
                                \n \n When the Function Word PCA test is run, the 50 most common function words in the set of documents are found, and then the frequency of each of those words in each document is also found using the NLTK FreqDist class (http://www.nltk.org). The frequencies of a word across the documents are standardized against the mean and standard deviation of that word, creating an n x 50 standardized matrix of values, where n is the number of documents on which the test is being performed. In order for this test to run, the number of rows---in this case documents---must be greater than the number of columns---in this case the word frequencies. Thus, there must be at least 51 documents being tested. \
                                \n \n The standardized values are found with basic Python functions and SciPy's "stats" package (http://www.scipy.org). The standardized values are put into a matrix using "NumPy"---which is another SciPy package---and then run through a PCA function from Matplotlib's "mlab" module (http://www.matplotlib.org). \
                                \n \n The process of PCA takes in a matrix of values where the columns represent variables---in this case word frequencies---and finds new axes that capture the most variation in the data. The data are remapped on these axes, or principal components. \
                                \n \n The axes are found and the data remapped in the "mlab" module, but the mathematical process behind it is as follows: a correlation matrix is formed containing the Pearson's r values that describe the correlation between two columns. The eigenvectors and eigenvalues of the correlation matrix are found, with the eigenvectors representing the principal components and the eigenvalues allowing the calculation of the percent of variation in the original data covered by the respective principal component (found by taking the respective eigenvalue and dividing it by the sum of all of the eigenvalues).""",
        "On Burrows's Delta": """Burrows's Delta attempts to capture aspects of style in terms of common word usage; it attempts to "boil down"the differences between documents and corpora based on these measurements and find stylistic differences, calculating Delta scores for each set of documents being compared to a disputed document. The specifics of what Delta scores mean are discussed below. \
                                \n \n When the Burrows's Delta test is run, it requires a specific set of documents: a disputed document and two corpora. The 30 most common words in the set of documents are found, and then the frequency of each of those words in each document is also found using the NLTK FreqDist class (http://www.nltk.org). The frequencies of a word across the documents are standardized against the mean and standard deviation of that word. \
                                \n \n The average standardized value, or z-score, for each word in each corpus is found. For each corpus, the difference of the 30 z-scores from the z-scores for the disputed text are found, and then the absolute value of each difference is found. The 30 absolute differences of the corpus's z-scores from the disputed text's are averaged, returning a value that represents an average difference in common word usage in the corpus from that in the disputed text. This averaged value is Delta. If Delta is 0, then, on average, the usage of the top 30 words in a corpus is exactly the same as in the disputed text. If Delta is 1, then, on average, the usage of the top 30 words in a corpus differs from the usage in the disputed text by one standard deviation. \
                                \n \n The Delta for each of the two corpora is found, and the lower Delta score reflects the corpus that is "less unlike"---to use J. Burrows's phrasing---the disputed text in terms of common word usage. The phrasing "less unlike" is important to use here, because a lower Delta score does not necessarily mean the style in that corpus is close to that in the disputed text, but rather that the usage is closer than that of the other corpus. \
                                \n \n Because Delta averages standardized values, the scores are likely to be in the range between 0 and 2, sometimes reaching up to 3. Because these values are relatively small, differences do not need to be large to be significant; if one corpus's Delta is .85, while the other's is 1, then that is a notable difference."""
        }
    def __init__(self, **kwargs):
        # take in the command type and set correct variable to true
        self.command_type = kwargs.get('command_type')
    def menu_description(self):
        _prettydescription = PrettyTableMaker()
        _prettydescription.vars["width"] = 50
        _prettydescription.vars["header"] = ["Description"]
        if self.command_type == "T, H, R, and K":
            my_list =  [[self.descriptions[self.command_type]], [self.descriptions["Type-Token Ratio"]], [self.descriptions["Hapax Dislegomena"]], [self.descriptions["Honore's R"]], [self.descriptions["Yule's K"]]]
            _prettydescription.vars["rows"] = my_list
            _prettydescription.make_from_rows()        
        else:
            _prettydescription.vars["variable"] = [self.descriptions[self.command_type]]
            _prettydescription.make_from_variable()
        #return x
    def pca_error_description(self, docs_count):
        _prettyerror = PrettyTableMaker()
        _prettyerror.vars["width"] = 50
        _prettyerror.vars["header"] = ["Description"]
        if self.command_type == "Lexical Richness PCA":
            _prettyerror.vars["variable"] = ["You need to select at least 5 documents in order to run this test. You have selected %d. \
                    \n \n Either rerun the test with more selected documents, or bootstrap your selection (in Library > Add/Remove/Manage Items) to yield a proper sample size." % (docs_count)]
            _prettyerror.make_from_variable()        
        else:
            _prettyerror.vars["variable"] = ["You need to select at least 51 documents in order to run this test. You have selected %d. \
                    \n \n Either rerun the test with more selected documents, or bootstrap your selection (in Library > Add/Remove/Manage Items) to yield a proper sample size." % (docs_count)]
            _prettyerror.make_from_variable()
    def burrows_printer(self, set_num):
        if set_num == 1:
            print "Build the first set of documents to test against the disputed text."
        if set_num == 2:
            print "Build the second set of documents to test against the disputed text."
        if set_num == 3:
            print "Select the disputed document to test against."
    def doc_or_corpus(self):
        valid_input = False
        while valid_input == False:
            try:
                doc_or_corpus = int(raw_input("(1) Document or (2) Corpus? Choose 1 or 2 (number only) and press Enter/Return: "))
                if doc_or_corpus == 1:
                    doc = True
                    valid_input = True
                    #return doc
                elif doc_or_corpus == 2:
                    doc = False
                    valid_input = True
                else:
                    print "Select 1 or 2."
                    #self.doc_or_corpus()
            except:
                print "Select 1 or 2."
                #self.doc_or_corpus()
        return doc
    def user_confirmation(self):
        valid_input = False
        while valid_input == False:
            delete_confirmation = raw_input("Are you sure? (y/n) ")
            if delete_confirmation.lower()=="y":
                confirmed = True
                valid_input = True
            elif delete_confirmation.lower()=="n":
                confirmed = False
                valid_input = True
            else:
                print "Select y or n."
        return confirmed
    def output_mode(self):
        valid_input = False
        while valid_input == False:
            output_mode = raw_input("Save output as a txt file in output folder? Choose y or n and press Enter/Return: ")
            if output_mode.lower() == "y":
                output_txt = True
                valid_input = True
            elif output_mode.lower() == "n":
                output_txt = False
                valid_input = True
            else:
                print "Enter either y or n."
        return output_txt
    def add_doc_parameters(self):
        print "Manually enter metadata. Hit Enter/Return to leave field blank"
        title = raw_input("Enter a title: ")
        last_name = raw_input("Enter an author's last name: ")
        first_middle = raw_input("Enter a first and middle name: ")
        user_file = raw_input("Enter a file path for the document you would like to import (txt file only): ")
        return user_file, title, last_name, first_middle
    
    def user_title(self):
        title = str(raw_input("Enter a title: "))
        return title
        
    def chunking_parameters(self, total_number_of_tokens):
        valid_input = False
        while valid_input == False:
            try:
                print "Your chosen set of documents contains " + str(total_number_of_tokens) + " tokens"
                chunk_size = int(raw_input("How many token would you like in each chunk (min 1, max "+ str(total_number_of_tokens) + ", integer only)? "))
                if chunk_size not in range(1, total_number_of_tokens):
                    print "Enter an integer between 1 and " + total_number_of_tokens+"."
                else:
                    valid_input = True
            except:
                pass
        valid_input = False
        while valid_input == False:
            try:
                chunk_title = raw_input('What would you like to call this collection of chunks? ')
                if len(chunk_title) == 0:
                    print "Title should not be left blank."
                else:
                    valid_input = True
            except:
                pass
        return chunk_size, chunk_title

    
    def bootstrap_parameters(self):
        valid_input = False
        while valid_input == False:
            try:
                sample_size = int(raw_input("Select a sample size percentage (1-100, integer only): "))
                if sample_size not in range(1,101):
                    print "Enter an integer between 1 and 100."
                else:
                    valid_input = True
            except:
                pass
        valid_input = False
        while valid_input == False:
            try:
                number_of_samples = int(raw_input("How many samples would you like (1-1000, integer only)? "))
                if number_of_samples not in range(1, 1001):
                    print "Enter an integer between 1 and 1000."
                else:
                    valid_input = True
            except:
                pass
        return sample_size, number_of_samples
    
    def corpus_choice(self):
        #asks which corpus?
        valid_input = False
        while valid_input == False:
            try:
                corpus_choice = int(raw_input("Choose a Corpus ID from the library (number only) and press Enter/Return: "))
                valid_input = True
            except:
                print "Enter a valid selection."
            #returns selection
        return corpus_choice
    def doc_choice(self):
        #asks which doc?
        valid_input = False
        while valid_input == False:
            try:
                doc_choice = int(raw_input("Choose a Doc ID from the library (number only) and press Enter/Return: "))
                valid_input = True
            except:
                print "Enter a valid selection."
        #returns selection
        return doc_choice
    def add_more(self):
        #asks add more to selection?
        valid_input = False
        while valid_input == False:
            add_more = raw_input("Do you want to add additional items? Choose y or n and press Enter/Return: ")
            if add_more.lower() == "y":
                add_more = True
                valid_input = True
            elif add_more.lower() == "n":
                add_more = False
                valid_input = True
            else:
                print "Enter either y or n."
        return add_more
    def completion_screen(self, headers, data):
        x = PrettyTable(headers) #headers must be a list of headers
        x.align = "l" # Left align
        for i in data:  #data must be lists in a list. # of items in sub-lists must equal number of items in header
            x.add_row(i)
        print x
        
    """ 
    test_choices = ['Perform this test on a Text', 'Perform this test on a Corpus', 'Home', 'Back']
    test_description = " "

         
            
    def select_test(self):
        print("\n")
        y = PrettyTable(["Test", "Description"])
        y.align = "l"
        y.add_row([self.test, self.test_description])
        y.max_width["Test"] = 5
        y.max_width = 40
        print y
        x = PrettyTable(["#", "Selection"])
        x.align["#"] = "l" # Left align
        x.align["Selection"] = "l"
        for i, n in enumerate(self.test_choices):
            x.add_row([str(i+1), str(n)])
        x.max_width = 40
        print x
        mode = raw_input("Please make a selection (number only): ")
        mode = int(mode)
        if mode == 1:
            #print list of library items (docs) with numbers
            #ask user to select a number
            #call appropriate instance method (docs)
            pass
        elif mode == 2:
            #print list of library items (corpus) with numbers
            #ask user to select a number
            #call appropriate instance method (corpus)
            pass
        elif mode == 3:
            menu_keys['Home'].select_item()
        elif mode == 4:
            pass
        else:
            self.select_test()
        
        #tsv = raw_input("Save as TSV? (y/n): ")
        #if tsv.lower() == 'y':
            #print "TSV worked"
    def select_item(self):
        self.print_menu()
        selection = raw_input("Choose a menu item. Enter only the corresponding number: ")
        try:
            selection = int(selection)-1
            if selection < 0 or selection > len(self.custom_items)-1:
                print ("Please make a valid selection.")
                self.select_item()
            else:
                key = self.custom_items[selection]
                # Don't need any conditionals, just use inheritance/replacement to create ExitMenu.select_item and add to master dictionary
                if key in menu_keys:
                    menu_keys[key].select_item()
                else:
                    print ("Please make a valid selection.")
                    self.select_item()
        except:
                print ("Please make a valid selection.")
                self.select_item()
"""




def main():
    print("Matt Lavin is wrong because he sucks.")
    
    """
    _menus = {
    "_main": Menu(custom_items=["Tests", "Library"]),
    "_tests": Menu(custom_items= ["Yule's K", "Honore's R", "Hapax Dislegomena", "Type-Token Ratio", "Lexical Richness PCA", "Function Word PCA", "Burrows's Delta"]),
    "_library": Menu(custom_items= ["View Library", "Add/Remove/Manage Items"]),
    "_documentation": Menu(custom_items= [ None ])
    }    
    response = _menus["_main"].gather_user_input("Gimmee!")
    print response
    #print user_choice
    """
    
if __name__ == "__main__": main()
