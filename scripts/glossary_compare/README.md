# Smartling/Pontoon glossary compare documentation

## Summary

This tool takes a glossary export from Smartling and a Pontoon locale export as input, and exports a csv list of terms that only exist in the Smartling export.

## Syntax

Call glossary_compare.py from your command line, with the following arguments:

--smartling *filepath*  
(***Required***) Designate the filepath of a .tbx (version 2) file that contains the list of terminology exported from Smartling.

--pontoon *filepath*  
(***Required***) Designate the filepath of a .tbx (version 2) file that contains the list of terminology exported from Pontoon.

--locale *locale name, default: en-US*  
Select if you want to compare terms for a specific locale. Will default to en-US locale if omitted.

--csv  
If included will output unique terms to CSV files.


## Output

This script outputs a csv file in the directory this script was run.
