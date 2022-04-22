# SWISS results

I performed the benchmarking by running test.sh in the homedir of the swiss docker container (/home/root/swiss).  The 

The pyv/ivy source files can be found in ian/src/ and the results are in ian/results/.  There is now a top level CSV summary for the 'auto' config and the 'templ' config, both found in ./ian/results/\*.csv.  The results also include subfolders with all of stdout and stderr (and hence any crashes) that a run may have produced.  The command used for the run can be found inside the CSV summary table.

A note on reading the ./ian/results/\*.csv files:
If a swiss benchmark completes then I populate the columns with all the information from the run output; this includes a “Success” field which I use to populate the "success" column.  If the success column is true then swiss was able to find an inductive invariant, otherwise the column is false.  However if the run doesn’t complete (from either a crash or timeout) then swiss does not output the Success field (or any other information) so the "success", "duration", etc. fields are all NA.
