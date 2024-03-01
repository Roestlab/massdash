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
extraction_config.im_window = 0.2
extraction_config.rt_window = 50
extraction_config.mz_tol = 20

feature_df = loader.loadFeatureMaps("AFVDFLSDEIK", 2, extraction_config)[dataFiles].feature_df

feature_df.to_csv(f"{basePath}/featureMap/ionMobilityTestFeatureDf.tsv", sep='\t', index=False)


