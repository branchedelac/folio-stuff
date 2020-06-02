# (a) Get a list of all holdings records connected to the old (Enigma) instance
# Query {{baseUrl}}/holdings-storage/holdings?query=(instanceId=="Instance_ID") 
# Input: Current Instance ID
# (a) For each Holdings record, change the Instance ID property to the Libris equivalent in FOLIO
# Input: Current Instance ID, New Instance ID
# (a) Create a MARC record with a delete flag and send it to EDS.
# (a) Delete the SRS record connected to the Enigma Instance
# (a) Delete the Enigma Instance

# Open a csv with two columns containing, on each row,
#   old_inst_id = UUID of the old instance, from which the holdings will be disconnected, and the old instance and its srs record then deleted
#   new_inst_id UUID of the new nstance, to which the holdings will be moved

#___Move holdings to new instance___
# For each row in csv
#   From FOLIO, GET all holdings where "instanceId" = old_inst_id and add them to a list
#   For each holding
#       Replace the value in "instanceId" (currently old_inst) to new_inst_id
#       PUT the updated holdings record to FOLIO

#___Delete obsolete records___
# For each row in csv
#   From FOLIO, GET all types of SRS records (all of them!) where "instanceId" = old_inst_id
#   Create a minimal MARC record with DELETE flag (and write to file that we'll send to EDS)
#   From FOLIO, DELETE the SRS records
#   From FOLIO, DELETE the instance old_inst_id
    