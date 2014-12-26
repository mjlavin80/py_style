py_style
========

A Python command line tool leveraging NLTK, numpy, scipy, and matplotlib functionalities (with sqlite3 back-end) to allow a user to run authorship attribution tests such as Yule's K, Honore's R, Type Token Ratio, Hapax Dislegomena Function Word PCA, and Burrows Delta. Creates a smooth document library, supports text file ingestion, allows user to output csv results for external analysis.

Installation
========
I. Install lates Python 2 version (2.7.9 as of 12-23-14)

II. Dependencies: Install or verify that the following libraries are installed

1.	scipy (http://www.scipy.org/install.html)
2.	numpy (http://www.scipy.org/install.html)
3.	matplotlib.mlab (http://matplotlib.org/users/installing.html)
4.  nltk (http://www.nltk.org/install.html)
5.	prettytable (supports easy_install)
6.	sqlite3 (already included in standard library)
7.	urllib (already included in standard library)
8.	io (already included in standard library)
9.	os (already included in standard library)
10.	math (already included in standard library)
11.	time (already included in standard library)
12.	datetime (already included in standard library)
13.	random (already included in standard library)
14.	re (already included in standard library)
15.	sys (already included in standard library)


III. Download the source files to a directory of your choice. 

IV. Use Python to run py_styleController.py through the terminal. 

V. On first use, the script will create an sqlite3 database in your root directory called “py_style.db”. This database will contain no texts. 

VI. Navigate the menu by inputting numerical selections and pressing “Return.”
