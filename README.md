# folio-stuff

Days in the life of a FOLIO librarian... 

This is a collection of scripts that I wrote, to deal with (one-time or recurring, simple or complex) everyday issues/needs, while working as systems librarian at Chalmers.

## Some highlights

`recalls_with_available_items.py`
This script returns a list of UI URLs for open recall requests on items of instances that also have available items. Staff can then manually move the recall requests to an available item. 

`find_folio_rec_in_libris.py`
A script for identifying locally cataloged records that match one or more records in Swedish Union Catalog LIBRIS. Given a list of FOLIO MARC records in JSON format, for each record, the script looks up ISBN and ISN in LIBRIS, and outputs various lists of FOLIO instance UUIDs for records matching and not matching anything in LIBRIS.

`move_holdings_between_instance.py`
A script for moving holdings between given instances en masse. Given a two column list of FOLIO isntance UUIDs, for each instance pair (row), it fetches the holdings from one of the instances ad reassociates it with the other instance. Written before the Inventory Move API was developed.

`add-call-no-suffix.py`
A set of scripts written to solve a particular issue at Chalmers, where some holdings records had accidentally been migrated without their call no suffix, and we had to add that value afterwards based on item data from our previous ILS. These scripts could use some pretty thorough refactoring.