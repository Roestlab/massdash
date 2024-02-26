- Raw data used was 20190816_TIMS05_MA_FlMe_diaPASEF_25pc_50ng_A2_1_26.d (PXD017703)

- Conversion to diaPysef was done using diaPysef (version 1.0.1) with the following command (executed in the .d folder)

``diapysef converttdftomzml --in=./ --out=20190816_TIMS05_MA_FlMe_diaPASEF_25pc_50ng_A2_1_25.mzML``

- The .mzML file was subset to the target peptide using the following `create_test_mzml.ipynb` notebook

- The `.osw` file was created based on the published `.tsv` results as outlined in the `create_osw_file.ipynb` notebook. 


- DIANN (version 1.8) was run via the commandline with the following arguments as outlined in `run_diann.sh`	- Note some modifications from the original script were made for increased readability/portability


- DIANN test file was created using `create_diann_report.ipynb`
