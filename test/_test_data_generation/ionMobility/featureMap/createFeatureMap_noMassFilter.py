# Create a featureMap based on the ion mobility test data
from massdash.loaders import MzMLDataLoader
from massdash.structs import TargetedDIAConfig

import pandas as pd

basePath="../../../test_data"
dataFiles=f'{basePath}/mzml/ionMobilityTest.mzML'
rsltsFile=f'{basePath}/osw/ionMobilityTest.osw'

loader = MzMLDataLoader(dataFiles=dataFiles,
                        rsltsFile=rsltsFile,
                        rsltsFileType="OpenSWATH")

extraction_config = TargetedDIAConfig()
extraction_config.im_window = 0.06
extraction_config.rt_window = 3
extraction_config.mz_tol = 1e26

feature_df = loader.loadFeatureMaps("AFVDFLSDEIK", 2, extraction_config)['ionMobilityTest'].feature_df

#print(feature_df)
#print(feature_df.keys())
#[dataFiles].feature_df

feature_df.to_csv(f"{basePath}/featureMap/ionMobilityTestFeatureDfEntireSpectra.tsv", sep='\t', index=False)


