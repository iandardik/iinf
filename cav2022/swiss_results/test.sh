#!/bin/bash

src_loc="ian/src"
top_loc="ian/results"
rm -rf "$top_loc/"
mkdir -p "$top_loc/"
echo "protocol,success,duration (sec),protocol invs,# synthesized invs,output loc,notes,swiss command" > "$top_loc/results-templ.csv"
echo "protocol,success,duration (sec),protocol invs,# synthesized invs,output loc,notes,swiss command" > "$top_loc/results-auto.csv"

do_test() {
	conf="$1"
	f="$2"
	n="$3"

	# swiss makes folders based on a timestamp
	sleep 1s

	output_loc="$top_loc/$n"
	swiss_comm="./run.sh $f --config $conf --threads 1 --minimal-models --with-conjs"
	timeout 4m ./run.sh "$f" --config "$conf" --threads 1 --minimal-models --with-conjs 1> "$output_loc/run_output-${conf}.log" 2> "$output_loc/run_output-${conf}.err"
	err_f=$(cat "$output_loc/run_output-${conf}.err")
	if [[ "$err_f" = "" ]]
	then
		# no crash, but not necessarily success
		succ_line=$(grep '^Success: ' "$output_loc/run_output-${conf}.log")
		if [[ "$succ_line" = "" ]]
		then
			# timeout
			echo "$n,NA,NA,NA,NA,$output_loc,timeout after 4min,$swiss_comm" >> "$top_loc/results-${conf}.csv"
		else
			# swiss finished, it may not have been successful though
			pre_invs=$(grep '^safety\|^invariant\|^conjecture' "$f" | wc -l)
			succ=$(grep '^Success: ' "$output_loc/run_output-${conf}.log" | sed 's/^Success: //g')
			sec=$(grep '^total time:' "$output_loc/run_output-${conf}.log" | sed 's/^total time: //g' | sed 's/\..*$//g')
			log_folder=$(grep '^logs ' "$output_loc/run_output-${conf}.log" | sed 's/^logs //g')
			invs_f="$log_folder/invariants"
			post_invs=$(grep -v '^#' $invs_f | wc -l)
			echo "$n,$succ,$sec,$pre_invs,$post_invs,$output_loc,,$swiss_comm" >> "$top_loc/results-${conf}.csv"
			cp "$invs_f" "$output_loc/invariants-${conf}.txt"
		fi
	else
		# crash
		echo "$n,NA,NA,NA,NA,$output_loc,crash,$swiss_comm" >> "$top_loc/results-${conf}.csv"
	fi
}

for f in `ls $src_loc/*.pyv $src_loc/*.ivy`
do
	n=$(echo "$f" | sed 's|^.*/||g' | sed 's|\..*$||g')

	# skip files without a config
	if [ ! -f "$src_loc/${n}.config" ]
	then
		#echo "skipping $n because $src_loc/${n}.config DNE"
		continue
	fi

	echo "Running $n"
	mkdir -p "$top_loc/$n/"

	do_test templ "$f" "$n"
	do_test auto "$f" "$n"
done
