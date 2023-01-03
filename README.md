# Terminology Management

This repository contains scripts and workflows for the management of Mozilla's l10n terminology.

## Scripts

### glossary_compare
Script for comparing tbx files between Pontoon and Smartling. Returns terms unique to each glossary. See [here](./scripts/glossary_compare/) for details.

### tbx_merge
Script for merging Pontoon glossary tbx files with Smartling. See [here](./scripts/tbx_merge/) for details.


## Automation
The automation periodically checks Pontoon terminology for any new terms or translations that have been added. If new terms are found, the workflow will fail then a pull request will be created. 

The pull request commits the latest tbx files from Pontoon into the `terminology` folder. This folder contains terminology files that reflect the current state of the Smartling glossary. The new terms/translations should be synced with Smartling using the [TBX Merge](./scripts/tbx_merge/) script before the Pull Request is merged. Once Smartling is updated and the Pull Request merged, the two repos' status can be considered in-sync. 

### Terminology sync workflow

1. Terminology Update Check:  
Automatically runs 2 times a month. If the workflow fails it means some locales have updated/added terms. A Pull Request will be created with the changes to pertinent files.

2. Export Smartling glossary  
Go to [Smartling](https://www.smartling.com/) and export main glossary. See details on how to do this [here](./scripts/tbx_merge/). 
* Select `TBX V2 Core` 
* Choose`Select displayed results` to export all languages

3. Copy the downloaded file to your working folder, run [tbx_merge.py script](./scripts/tbx_merge/)  
Example: 
```
python ./terminology_management/scripts/tbx_merge/tbx_merge.py --locales ./terminology_management/scripts/tbx_merge/locales.txt --id-format smartling --smartling ./smartling.tbx
```

4. Import `smartling_merge_glossary.tbx` into Smartling  
Compare the import information (locales, number of terms changed) that appears in Smartling to what appears in step 1. If everything appears OK, complete the import. After import complete, spot check that terms have been added successfully.

5. Merge pull request and delete branch

6. Manually run workflow to confirm PR in sync  
Run the [workflow](https://github.com/mozilla-l10n/terminology_management/actions/workflows/term_check.yml) again.  
It is possible more terms were added between when the PR was created and when you did the sync. In that case, git is not in sync with Smartling, and you should merge the second PR generated after confirming that only terms added during step 4 are included in the PR.

## Smartling / Pontoon sync status 
[![Smartling sync status](https://github.com/mozilla-l10n/terminology_management/actions/workflows/term_check.yml/badge.svg)](https://github.com/mozilla-l10n/terminology_management/actions/workflows/term_check.yml)
