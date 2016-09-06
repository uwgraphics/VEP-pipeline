**VEP-Pipeline Readme** \
written and maintained by Erin Winter (wintere@cs.wisc.edu)

These scripts require Python 3 and a command line interface. Anaconda -- a distribution of Python and many useful packages -- is recommended.
If you have questions about what arguments each script requires, run python {name of script} -h to get a command line menu.

**Standard Processing Script Pipeline:**
1. character-cleaner.py: given a folder of .xml files, outputs character cleaned files with the same extension\
2. tei-decoder.py OR tei-decoder-stage.py (early modern drama XML only): given a folder of character-cleaned xml files, outputs extracted plain-text files
3. (optional) EMStandardizer.py: given a folder of character cleaned, extracted plain-text texts, outputs standardized plain-text files 


**Other Files:**\
conversion_dict.py: a python dictionary class that enumerates unicode characters and ascii substitutions. limited to characters from the TCP.

config_all_TCP.yaml AND stage_config.yaml: files that tells our tei-decoder which divs (or XML tags) to extract text from. use config_all_TCP to extract all text on the page, and stage_config.yaml to extract only dialogue from plays.

standardizer_dictionary.txt: the dictionary for our standardizer, instructions for reading the dictionary are in the form of comments at the top

*Our standardizer dictionary was curated for spelling from Early Modern texts keyed by the Text Creation Partnership, which means its dictionary is heavily skewed towards the Early English Books Online corpora. It makes changes like doe->do that have largely positive effects on the majority of Early Modern texts, but those same changes will have undesirable effects on texts dated 1700 or later because of change in spelling practices over time. 
