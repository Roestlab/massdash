#### Fetch Library
wget https://ftp.pride.ebi.ac.uk/pride/data/archive/2020/12/PXD017703/HeLa_200ng_pqp_library.zip
unzip HeLa_200ng_pqp_library.zip

#### Convert to .TSV
TargetedFileConverter -in 190513_hela_24fr_library_ptypic_decoy.pqp -out 190513_hela_24fr_library_ptypic_decoy.tsv
