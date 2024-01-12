#!/bin/bash


####################### .d file and library all from PXD017703 ########################
d1=20190816_TIMS05_MA_FlMe_diaPASEF_25pc_50ng_A2_1_25.d
d2=20190816_TIMS05_MA_FlMe_diaPASEF_25pc_50ng_A2_1_26.d
d3=20190816_TIMS05_MA_FlMe_diaPASEF_25pc_50ng_A2_1_27.d
lib="190513_hela_24fr_library_ptypic_decoy.pqp" 

libtsv=$(basename ${lib/.pqp/.tsv})

## Format Library for DIA-NN requires OpenMS
TargetedFileConverter -in $(basename ${lib}) -out ${libtsv}

## prepare library for DIA-NN (remove decoys, rename columns)
libDIANN=$(basename -s .tsv ${lib})_diann.tsv
python ${fromMain}/${scripts}/format_library_diann.py ${libtsv} ${libDIANN}

checkAndRunSbatch report.stats.tsv ${scripts}/run_diann_multiple.sh library/${libDIANN} ../../bin/sif/2022-08-29-diann-1.8_c1.sig $d1 $d2 $d3

library=$1
sig=$2
shift 2
inputfiles=$@

############################################
# Run DIA-NN
############################################
diann \ 
	--f $d1 --f $d2 --f $d3 \
	--lib ${libDIANN} \
	--threads 8 \
	--verbose 4 \ 
	--matrices \
	--out-lib 'report-lib.tsv' \ 
	--gen-spec-lib \ 
	--report-lib-info \
	--reanalyse \
	--matrix-qvalue 0.05 \
	--smart-profiling"
