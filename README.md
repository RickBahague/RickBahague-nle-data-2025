# scrapER2025

forked from git@github.com:RickBahague/scraper2025.git

full data download - https://github.com/RickBahague/RickBahague-nle-data-2025/releases/tag/release01

This script downloads all data from `2025electionresults.comelec.gov.ph` by storing the json responses of the backend API. The `results` directory mirrors the levels of administrative divisions. Slashes (`/`) in the name of a division is replaced by `_`. Each directory stores information about that level (`info.json`) and the corresponding certificate of canvas (`coc.json`) or clustered precinct results (election return). It will not redownload an already existing json file so multiple invocations of the script won't download everything again. The modification time of the created file is matched to the `Last Modified` HTTP response header of the source URL.

## Dependencies

* python-requests
* python-click
* tqdm
 
## Invocation

This is a python script which can be invoked by

    python scraper.py

or

    ./scraper.py

if on an Ubuntu or Debian-based machine.

It also accepts the following parameters:

    -b, --base-dir TEXT             directory from which all downloaded data
                                    will be stored
    -d, --download-delay FLOAT      minimum delay between successive downloads
    -l, --log-level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                    log output level

