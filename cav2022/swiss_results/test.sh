#!/bin/bash

rm -rf ian/results/
mkdir -p "ian/results/"
echo "protocol,success,duration (sec),protocol invs,# synthesized invs,output loc,notes,swiss command" > ian/results/results-templ.csv
echo "protocol,success,duration (sec),protocol invs,# synthesized invs,output loc,notes,swiss command" > ian/results/results-auto.csv

do_test() {
	conf="$1"
	f="$2"
	n="$3"
	output_loc="results/$n/"
	swiss_comm="./run.sh $f --config $conf --threads 1 --minimal-models --with-conjs"
	#timeout --foreground 5m ./run.sh "$f" --config "$conf" --threads 1 --minimal-models --with-conjs 1> "ian/results/$n/run_output-${conf}.log" 2> "ian/results/$n/run_output-${conf}.err"
	timeout 4m ./run.sh "$f" --config "$conf" --threads 1 --minimal-models --with-conjs 1> "ian/results/$n/run_output-${conf}.log" 2> "ian/results/$n/run_output-${conf}.err"
	err_f=$(cat "ian/results/$n/run_output-${conf}.err")
	if [[ "$err_f" = "" ]]
	then
		# no crash, but not necessarily success
		succ_line=$(grep '^Success: ' "ian/results/$n/run_output-${conf}.log")
		if [[ "$succ_line" = "" ]]
		then
			# timeout
			echo "$n,NA,NA,NA,NA,$output_loc,timeout after 4min,$swiss_comm" >> "ian/results/results-${conf}.csv"
		else
			# swiss finished, it may not have been successful though
			pre_invs=$(grep '^safety\|^invariant\|^conjecture' "$f" | wc -l)
			succ=$(grep '^Success: ' "ian/results/$n/run_output-${conf}.log" | sed 's/^Success: //g')
			sec=$(grep '^total time:' "ian/results/$n/run_output-${conf}.log" | sed 's/^total time: //g' | sed 's/\..*$//g')
			log_folder=$(grep '^logs ' "ian/results/$n/run_output-${conf}.log" | sed 's/^logs //g')
			invs_f="$log_folder/invariants"
			post_invs=$(grep -v '^#' $invs_f | wc -l)
			echo "$n,$succ,$sec,$pre_invs,$post_invs,$output_loc,,$swiss_comm" >> "ian/results/results-${conf}.csv"
			cp "$invs_f" "ian/results/$n/invariants-${conf}.txt"
		fi
	else
		# crash
		echo "$n,NA,NA,NA,NA,$output_loc,crash,$swiss_comm" >> "ian/results/results-${conf}.csv"
	fi
}

for f in `ls ian/src/*.pyv ian/src/*.ivy`
do
	n=$(echo "$f" | sed 's|^.*/||g' | sed 's|\..*$||g')

	# skip files without a config
	if [ ! -f "ian/src/${n}.config" ]
	then
		#echo "skipping $n because ian/src/${n}.config DNE"
		continue
	fi

	echo "Running $n"
	mkdir -p "ian/results/$n/"

	do_test templ "$f" "$n"
	do_test auto "$f" "$n"
done
