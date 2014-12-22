import sys
import sqlite3
import py_styleView as view
sys.path.append("/Users/agladwin/Documents/stylometry/testing")
import py_styleModel as model
from prettytable import PrettyTable
import urllib
import time
import datetime
import io
import os

#change to database call
db = sqlite3.connect('py_style.db')

try:
    #metadata table and columns
    db.execute('create table metadata(doc_id integer primary key not null, author_lastname text, author_first_middle text, doc_title text, original_publication_title text, original_publication_type text, year_written text, year_published int, bootstrap integer)') 
    print"Metadata Database Successfully Created"
    
    #corpus id and title
    db.execute('create table corpus(corpus_id integer primary key not null, corpus_title int)')

    #corpus manager table and columns
    db.execute('create table corpus_doc(corpus_id integer, doc_id integer, FOREIGN KEY(corpus_id) REFERENCES corpus(corpus_id), FOREIGN KEY(doc_id) REFERENCES metadata(doc_id))')

    # thrk table
    db.execute('create table thrk(doc_id integer, t real default value null, h real default value null, r real default value null, k real default value null, FOREIGN KEY(doc_id) REFERENCES metadata(doc_id))')  
    
except:
    print"Database Successfully Loaded"
    
_menus = {
    "_home": view.Menu(custom_items=["Tests", "Library"]),
    "_tests": view.Menu(custom_items=["Type-Token Ratio", "Hapax Dislegomena", "Honore's R", "Yule's K", "T, H, R, and K", "Lexical Richness PCA", "Lexical Richness PCA with Bootstrap", "Function Word PCA", "Burrows's Delta"]),
    "_library": view.Menu(custom_items=["View Library", "Add/Remove/Manage Items"]),
    "_documentation": view.Menu(custom_items=["On Library Management", "On General Testing", "On T, H, R, and K", "On Lexical Richness PCA", "On Function Word PCA", "On Burrows's Delta"]),
    "_armi": view.Menu(custom_items=["Add Documents", "Remove Documents", "Manage Corpora", "Chunking"]),
    "_managecorpora": view.Menu(custom_items=["Create Corpus", "Delete Corpus", "Add Documents to Corpus", "Remove Documents from Corpus"])
    }

_commands = {
    "_exit": view.Command(command_type="Exit"),
    "_back": view.Command(command_type="Back"),
    "_yule": view.Command(command_type="Yule's K"),
    "_honore": view.Command(command_type="Honore's R"),
    "_hapax": view.Command(command_type="Hapax Dislegomena"),
    "_typetoken": view.Command(command_type="Type-Token Ratio"),
    "_thrk": view.Command(command_type="T, H, R, and K"),
    "_lrpca": view.Command(command_type="Lexical Richness PCA"),
    "_fwpca": view.Command(command_type="Function Word PCA"),
    "_delta": view.Command(command_type="Burrows's Delta"),
    "_viewlibrary": view.Command(command_type="View Library"),
    "_adddocuments": view.Command(command_type="Add Documents"),
    "_removedocuments": view.Command(command_type="Remove Documents"),
    "_createcorpus": view.Command(command_type="Create Corpus"),
    "_deletecorpus": view.Command(command_type="Delete Corpus"),
    "_adtc": view.Command(command_type="Add Documents to Corpus"),
    "_rdfc": view.Command(command_type="Remove Documents from Corpus"),
    "_chunking": view.Command(command_type="Chunking"),
    "_lrpcawb": view.Command(command_type="Lexical Richness PCA with Bootstrap"),
    "_onlm": view.Command(command_type="On Library Management"),
    "_ongt": view.Command(command_type="On General Testing"),
    "_onthrk": view.Command(command_type="On T, H, R, and K"),
    "_onlrpca": view.Command(command_type="On Lexical Richness PCA"),
    "_onfwpca": view.Command(command_type="On Function Word PCA"),
    "_ondelta": view.Command(command_type="On Burrows's Delta")
    }

menu_keys = {
    "Home": ("menu", "_home"),
    "Documentation": ("menu", "_documentation"),
    "Tests": ("menu", "_tests"),
    "Library": ("menu", "_library"),
    "Exit": (None, "_exit"),
    "Back": (None, "_back"),
    "Yule's K": ("command", "_yule"),
    "Honore's R": ("command", "_honore"),
    "Hapax Dislegomena": ("command", "_hapax"),
    "Type-Token Ratio": ("command", "_typetoken"),
    "T, H, R, and K": ("command", "_thrk"),
    "Lexical Richness PCA": (None, "_lrpca"),
    "Function Word PCA": (None, "_fwpca"),
    "Burrows's Delta": (None, "_delta"),
    "View Library": (None, "_viewlibrary"),
    "Add/Remove/Manage Items": ("menu", "_armi"),
    "Add Documents": ("library_command", "_adddocuments"),
    "Remove Documents": ("library_command", "_removedocuments"),
    "Manage Corpora": ("menu", "_managecorpora"),
    "Create Corpus": ("library_command", "_createcorpus"),
    "Delete Corpus": ("library_command", "_deletecorpus"),
    "Add Documents to Corpus": ("library_command", "_adtc"),
    "Remove Documents from Corpus": ("library_command", "_rdfc"),
    "Chunking": ("library_command", "_chunking"),
    "Lexical Richness PCA with Bootstrap": (None, "_lrpcawb"),
    "On Library Management": ("on_command", "_onlm"),
    "On General Testing": ("on_command", "_ongt"),
    "On T, H, R, and K": ("on_command", "_onthrk"),
    "On Lexical Richness PCA": ("on_command", "_onlrpca"),
    "On Function Word PCA": ("on_command", "_onfwpca"),
    "On Burrows's Delta": ("on_command", "_ondelta")
    }

#retrieve data from Library (in Model)
#input handler method
#generate output files (collect raw_input from view such as filename)
#calls first menu
#coordinates successive menu and command views
        
_library = model.Library()

class MenuController(object):
    def __init__(self):
        self.menu_history = ["Home"]
        self.complete_doc_list = []
        self.command_type = None
        self.output = False
        self.test_values = []
        self.start_menu()
        self.headers = []
    def add_doc_messenger(self):
        #self.title, self.last_name, self.first_middle, self.user_file
        corpus_id = _library.corpus_constructor_temporary(None)
        _processingCorpus = model.Corpus(corpus_id)
        _library.corpus_assassin(corpus_id)
        tokens = _processingCorpus.text_file_to_tokens(self.user_file)
        if tokens != False:
            doc_id = _processingCorpus.doc_constructor(self.title, tokens, self.last_name, self.first_middle)
        else:
            print "Add a document to library failed."
    def chunking_messenger(self):
        #creates a temp corpus from source doc_ids
        corpus_id = _library.corpus_constructor_temporary(self.complete_doc_list)
        _processingCorpus = model.Corpus(corpus_id)
        #delete temporary corpus before any commit occurs
        _library.corpus_assassin(corpus_id)
         #invoke corpus_constructor with commit at the end
        new_doc_ids, corpus_title = _processingCorpus.chunking_doc_factory(self.chunk_size, self.chunk_title, self.total_set_of_tokens)                  
        if len(new_doc_ids) > 1:
            new_corpus_id = _library.corpus_constructor_and_commit(new_doc_ids, corpus_title)
    def bootstrap_messenger(self):
        #creates a temp corpus from source doc_ids
        corpus_id = _library.corpus_constructor_temporary(self.complete_doc_list)
        _processingCorpus = model.Corpus(corpus_id)
        #the above is somehow committing, don't know why
        _library.corpus_assassin(corpus_id)
        new_doc_ids, corpus_title = _processingCorpus.bootstrap_doc_factory(self.number_of_samples, self.sample_size)                  
        new_corpus_id = _library.corpus_constructor_and_commit(new_doc_ids, corpus_title)
        #find top corpus id, purge from db?
        #invoke corpus_constructor with commit at the end
    def test_values_retriever(self):
        self.test_values = []
        command_type = self.command_type
        corpus_id = _library.corpus_constructor_temporary(self.complete_doc_list)
        _processingCorpus = model.Corpus(corpus_id)
        _processingCorpus.bootstrapped_docs_finder()
        for i in _processingCorpus.bootstrapped_ids:
            name = "document_" + str(i)
            _library.bootstrap_instances[name] = model.Document(i)
        if command_type == "Burrows's Delta":
            _processingCorpus.send_set_data(self.set1_length, self.set2_length, self.set1_name, self.set2_name)
            self.test_values, self.headers = _processingCorpus.values_getter(command_type)
        elif command_type == "Lexical Richness PCA with Bootstrap":
            _processingCorpus.send_bootstrap_data(self.set1, self.set2, self.set1_name, self.set2_name, self.number_of_samples1, self.sample_size1, self.number_of_samples2, self.sample_size2)
            self.test_values, self.headers = _processingCorpus.values_getter(command_type)
        else:
            corpus_id = _library.corpus_constructor_temporary(self.complete_doc_list)
            _processingCorpus = model.Corpus(corpus_id)
            self.test_values, self.headers = _processingCorpus.values_getter(command_type)
            self.test_values = sorted(self.test_values)
    def test_values_printer(self):
        _prettyoutput = view.PrettyTableMaker()
        _prettyoutput.vars["width"] = 55
        _prettyoutput.vars["rows"] = self.test_values
        _prettyoutput.vars["header"] = self.headers
        _prettyoutput.make_from_rows()
    def timestamp(self):
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_')
    def output_generator(self):
        if self.output == True:
            # look for a folder in the home directory called "output" and create if it doesn't exist
            try:
                os.chdir("./output")
            except:
                os.mkdir("./output")
            current_time = str(self.timestamp())
            file_name = current_time + self.command_type.lower()
            remove_list = [" ", "-", ":", ".", ",", ";", "!", "?", "'"]
            for i in remove_list:
                file_name = file_name.replace(i, "")
            file_name+= '.txt'
            print "This will create a file called %s" % (file_name)
            raw_input("Press Enter/Return to continue.")
            outfile = io.open(file_name, 'a')
            data = ""
            for i, k in enumerate(self.headers):
                if i < len(self.headers) - 1:
                    data += k + '\t'
                elif i == len(self.headers) - 1:
                    data += k + '\n'
            for i in self.test_values:
                for x, y in enumerate(i):
                    if x < len(i) - 1:
                        data += str(y) + '\t'
                    elif x == len(i) - 1:
                        data += str(y) + '\n'
            data = data.decode('utf-8')
            outfile.write(data)
            outfile.close()
    def add_more_loop(self):
        add_more = True
        doc_ids = []
        corpus_ids = []
        menu_instance = menu_keys[self.user_choice_name]
        command_instance = _commands[menu_instance[1]]
        while add_more == True:
            doc = command_instance.doc_or_corpus()
            if doc == True:
                #print the doc library
                output = _library.doc_fetcher()
                ids = []
                for row in output:
                    ids.append(row[0])
                _prettydoc = view.PrettyTableMaker()
                _prettydoc.vars["header"] = ["Doc ID", "Author Last Name", "F. M.", "Title"]
                _prettydoc.vars["sortby"] = "Doc ID"
                _prettydoc.vars["width"] = 55
                _prettydoc.vars["rows"] = output
                _prettydoc.make_from_rows()
                corpus_doc_id = command_instance.doc_choice()
                if corpus_doc_id in ids:
                    doc_ids.append(corpus_doc_id)
                else:
                    print "Doc ID not found in the library. Retry."
                    corpus_doc_id = command_instance.doc_choice()
            elif doc == False:
                #print the corp library
                output = _library.corpora_fetcher()
                ids = []
                for row in output:
                    ids.append(row[0])
                _prettycorpus = view.PrettyTableMaker()
                _prettycorpus.vars["header"] = ["Corpus ID", "Corpus Title", "Documents"]
                _prettycorpus.vars["sortby"] = "Corpus ID"
                _prettycorpus.vars["width"] = 55
                _prettycorpus.vars["rows"] = output
                _prettycorpus.make_from_rows()
                corpus_doc_id = command_instance.corpus_choice()
                if corpus_doc_id in ids:
                    corpus_ids.append(corpus_doc_id)
                else:
                    print "Corpus ID not found in the library. Retry."
                    corpus_doc_id = command_instance.corpus_choice()
            add_more = command_instance.add_more()
        corpus_doc_lists = [doc_ids, corpus_ids]
        docs_list = []
        for i in corpus_doc_lists[1]:
            corpus_name = "corpus_"+str(i)
            docs = _library.corpus_instances[corpus_name].corpus_vars["corpus_member_ids"]
            docs_list.extend(docs)
        self.complete_doc_list = list(set(corpus_doc_lists[0] + docs_list))
    def disputed_doc(self):
        menu_instance = menu_keys[self.user_choice_name]
        command_instance = _commands[menu_instance[1]]
        output = _library.doc_fetcher()
        length = len(output)
        _prettydoc = view.PrettyTableMaker()
        _prettydoc.vars["header"] = ["Doc ID", "Author Last Name", "F. M.", "Title"]
        _prettydoc.vars["sortby"] = "Doc ID"
        _prettydoc.vars["rows"] = output
        _prettydoc.make_from_rows()
        command_instance.burrows_printer(3)
        corpus_doc_id = command_instance.doc_choice()
        if corpus_doc_id in range(1, length + 1):
            disputed_id = corpus_doc_id
        else:
            print "Doc ID not found in the library. Retry."
            corpus_doc_id = command_instance.doc_choice()
        return [disputed_id]
    def print_corpora(self):
        self.output = _library.corpora_fetcher()
        length = len(self.output)
        _prettycorpus = view.PrettyTableMaker()
        _prettycorpus.vars["header"] = ["Corpus ID", "Corpus Title", "Documents"]
        _prettycorpus.vars["sortby"] = "Corpus ID"
        _prettycorpus.vars["width"] = 55
        _prettycorpus.vars["rows"] = self.output
        _prettycorpus.make_from_rows()
    def start_menu(self):
        self.user_choice_name = "Home"
        while True:
            #check if user_choice_name is a menu, command, or oncommand
            menu_instance = menu_keys[self.user_choice_name]
            if self.user_choice_name == "Exit":
                return False
            elif self.user_choice_name == "Back":
                try:
                    del self.menu_history[-1]
                    self.user_choice_name = self.menu_history[-1]
                except:
                    self.user_choice_name = "Home"
                    self.menu_history.append(self.user_choice_name)
            elif menu_instance[0] == "menu":
                _menus[menu_instance[1]].print_menu()
                self.user_choice_name = _menus[menu_instance[1]].gather_user_input()
                if menu_keys[self.user_choice_name][0] == "menu":
                    self.menu_history.append(self.user_choice_name)
                elif self.user_choice_name == "Manage Corpora":
                    self.menu_history.append(self.user_choice_name)
                else:
                    pass
            #if menu: do correct instance method; if command: do the command protocol
            elif menu_instance[0] == "command":
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                self.add_more_loop()
                self.command_type = command_instance.command_type
                self.test_values_retriever()
                self.test_values_printer()
                self.output = command_instance.output_mode()
                #if output was True, save output file to output folder
                self.output_generator()
                raw_input("All tasks complete. Press Enter/Return to return to the Tests menu.")
                self.user_choice_name = "Tests"
            elif menu_instance[0] == "library_command":
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                if self.user_choice_name == "Chunking":
                    self.add_more_loop()
                    #need to get total number of tokens from self.comple_doc_list
                    self.total_set_of_tokens = []
                    for i in self.complete_doc_list:
                        doc_name = 'document_' + str(i)
                        doc_tokens = _library.document_instances[doc_name].metadata["tokenized_doc"]
                        self.total_set_of_tokens += doc_tokens
                    self.total_number_of_tokens = len(self.total_set_of_tokens)
                    self.chunk_size, self.chunk_title = _commands["_chunking"].chunking_parameters(self.total_number_of_tokens)
                    self.chunking_messenger()
                elif self.user_choice_name == "Add Documents":
                    #call a view method to collect metadata and file
                    self.user_file, self.title, self.last_name, self.first_middle = _commands["_adddocuments"].add_doc_parameters()
                    #controller method creates a temp corpus, passes metadata and file to model, and manufactures document
                    self.add_doc_messenger()
                elif self.user_choice_name == "Remove Documents":
                    self.add_more_loop()
                    self.confirmation = command_instance.user_confirmation()
                    if self.confirmation == True:
                        for i in self.complete_doc_list:
                            _library.document_assassin(i)
                    else:
                        print "Remove action cancelled."
                elif self.user_choice_name == "Create Corpus":
                    self.title = command_instance.user_title()
                    self.add_more_loop()
                    _library.corpus_constructor_and_commit(self.complete_doc_list, self.title)
                elif self.user_choice_name == "Delete Corpus":
                    self.print_corpora()
                    corpus_doc_id = command_instance.corpus_choice()
                    ids = []
                    for row in self.output:
                        ids.append(row[0])
                    while corpus_doc_id not in ids:
                        print "Corpus ID not found in the library. Retry."
                        corpus_doc_id = command_instance.corpus_choice()
                    _library.corpus_assassin(corpus_doc_id)
                    title = "corpus_" + str(corpus_doc_id)
                    del _library.corpus_instances[title]
                elif self.user_choice_name == "Add Documents to Corpus":
                    print "Select a corpus to add documents to."
                    self.print_corpora()
                    corpus_doc_id = command_instance.corpus_choice()
                    ids = []
                    for row in self.output:
                        ids.append(row[0])
                    while corpus_doc_id not in ids:
                        print "Corpus ID not found in the library. Retry."
                        corpus_doc_id = command_instance.corpus_choice()
                    print "Select items to add to this corpus. Duplicate documents will not be added."
                    self.add_more_loop()
                    _library.add_docs_to_corpus(self.complete_doc_list, corpus_doc_id)
                elif self.user_choice_name == "Remove Documents from Corpus":
                    pass
                _library.__init__()
                self.user_choice_name = "Library"
            elif menu_instance[0] == "on_command":
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                raw_input("Press Return/Enter to go back to the Documentation page.")
                self.user_choice_name = "Documentation"
            elif self.user_choice_name == "Lexical Richness PCA":
                # define empty lists for doc selections
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                # asks for 5 documents or more (explains why)
                # standard library print / doc loop
                self.add_more_loop()
                if len(self.complete_doc_list) > 4:
                    self.command_type = command_instance.command_type
                    self.test_values_retriever()
                    self.test_values_printer()
                    # sends appropriate corpus to the Model
                    # gets data from model
                    # sends data to prettyprinter and prints
                    self.output = command_instance.output_mode()
                    self.output_generator()
                    raw_input("All tasks complete. Press Enter/Return to return to the Tests menu.")
                else:
                    command_instance.pca_error_description(len(self.complete_doc_list))
                self.user_choice_name = "Tests"
            elif self.user_choice_name == "Lexical Richness PCA with Bootstrap":
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                self.disputed_id = self.disputed_doc()
                command_instance.burrows_printer(1)
                self.add_more_loop()
                self.set1_name = raw_input("What would you like to call this set? ")
                self.set1 = self.complete_doc_list
                self.sample_size1, self.number_of_samples1 = command_instance.bootstrap_parameters()
                self.set1_length = len(self.set1)
                command_instance.burrows_printer(2)
                self.add_more_loop()
                self.set2_name = raw_input("What would you like to call this set? ")
                self.set2 = self.complete_doc_list
                self.sample_size2, self.number_of_samples2 = command_instance.bootstrap_parameters()
                self.set2_length = len(self.set2)
                self.complete_doc_list = self.disputed_id + self.set1 + self.set2
                self.command_type = command_instance.command_type
                self.test_values_retriever()
                # sends data to prettyprinter and prints
                self.test_values_printer()
                self.output = command_instance.output_mode()
                self.output_generator()
                raw_input("All tasks complete. Press Enter/Return to return to the Tests menu.")
                self.user_choice_name = "Tests"
            elif self.user_choice_name == "Function Word PCA":
                # print correct description
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                self.add_more_loop()
                if len(self.complete_doc_list) > 50:
                    self.command_type = command_instance.command_type
                    self.test_values_retriever()
                    self.test_values_printer()
                    # standard library print / doc loop (redefine as a method of its own?)
                    # self.add_more_loop()
                    # send appropriate corpus to the Model
                    # get data from model
                    # call prettyprinter and print
                    self.output = command_instance.output_mode()
                    self.output_generator()
                    raw_input("All tasks complete. Press Enter/Return to return to the Tests menu.")
                else:
                    command_instance.pca_error_description(len(self.complete_doc_list))
                self.user_choice_name = "Tests"
            elif self.user_choice_name == "Burrows's Delta":
                # print description
                command_instance = _commands[menu_instance[1]]
                command_instance.menu_description()
                #contested document (no add_more_loop)
                self.disputed_id = self.disputed_doc()
                command_instance.burrows_printer(1)
                # call method to retrieve choices for corpus 1 (use add_more_loop here)
                self.add_more_loop()
                self.set1_name = raw_input("What would you like to call this set? ")
                self.set1 = self.complete_doc_list
                self.set1_length = len(self.set1)
                command_instance.burrows_printer(2)
                #corpus 2 (use add_more_loop here)
                self.add_more_loop()
                self.set2_name = raw_input("What would you like to call this set? ")
                self.set2 = self.complete_doc_list
                self.set2_length = len(self.set2)
                self.complete_doc_list = self.disputed_id + self.set1 + self.set2
                self.command_type = command_instance.command_type
                # gets data from model
                self.test_values_retriever()
                # sends data to prettyprinter and prints
                self.test_values_printer()
                self.output = command_instance.output_mode()
                self.output_generator()
                raw_input("All tasks complete. Press Enter/Return to return to the Tests menu.")
                self.user_choice_name = "Tests"
            elif self.user_choice_name == "View Library":
                menu_instance = menu_keys[self.user_choice_name]
                command_instance = _commands[menu_instance[1]]
                # ask to view corpuses or docs? both?
                doc = command_instance.doc_or_corpus()
                # if docs, print table from db as pretty table
                if doc == True:
                    output = _library.doc_fetcher()
                    length = len(output)
                    _prettydoc = view.PrettyTableMaker()
                    _prettydoc.vars["header"] = ["Doc ID", "Author Last Name", "F. M.", "Title"]
                    _prettydoc.vars["sortby"] = "Doc ID"
                    _prettydoc.vars["rows"] = output
                    _prettydoc.vars["width"] = 55
                    _prettydoc.make_from_rows()
                # if corpuses, print table from db as pretty table
                elif doc == False:
                    self.print_corpora()
                # return to selection (aka View Library "start menu")
                raw_input("Press Enter/Return to return to Library menu.")
                self.user_choice_name = "Library"
            elif self.user_choice_name == "Add/Remove/Manage Items":
                menu_instance = menu_keys[self.user_choice_name]
                command_instance = _menus[menu_instance[1]]
                # if docs, print table from db as pretty table
                # in corpuses, have add, remove, manage
                # if add, allow user to create new corpus
                # if remove, allow user to remove a corpus
                # if manage, allow a user to add or remove docs in the corpus, possibly retitle?
                # in docs, have add and remove
                # if add, allow user to add a doc
                # if remove, allow user to remove a doc
                self.user_choice_name = "Library"
            else:
                self.user_choice_name = "Home"
                
def main():
    _menucontroller = MenuController()

if __name__ == "__main__": main()
