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


## Smartling / Pontoon sync status 
[![Smartling sync status](https://github.com/mozilla-l10n/terminology_management/actions/workflows/term_check.yml/badge.svg)](https://github.com/mozilla-l10n/terminology_management/actions/workflows/term_check.yml)
