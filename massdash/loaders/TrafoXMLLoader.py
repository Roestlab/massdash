"""
massdash/loaders/TrafoXMLLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Dict, Union

# Access
from .access.TrafoXMLAccess import TrafoXMLAccess

class TrafoXMLLoader:
    def __init__(self, 
                 dataFiles: Union[str, List[str]], 
                 libraryFile: Union[str, List[str]] = None, 
                 mzDebugFile: Union[str, List[str]] = None, 
                 imDebugFile: Union[str, List[str]] = None):
        ## store the file names
        if isinstance(dataFiles, str):
            self.dataFiles_str = [dataFiles]
        else:
            self.dataFiles_str = dataFiles
            
        if isinstance(libraryFile, str):
            self.libraryFile_str = [libraryFile]
        else:
            self.libraryFile_str = libraryFile
            
        if isinstance(mzDebugFile, str):
            self.mzDebugFile_str = [mzDebugFile]
        else:
            self.mzDebugFile_str = mzDebugFile
            
        if isinstance(imDebugFile, str):
            self.imDebugFile_str = [imDebugFile]
        else:
            self.imDebugFile_str = imDebugFile
    
        if self.libraryFile_str is not None and len(self.libraryFile_str) > 1:
            self.dataFiles = [TrafoXMLAccess(f, l, mz_f, im_f) for f, l, mz_f, im_f in zip(self.dataFiles_str, self.libraryFile_str, self.mzDebugFile_str, self.imDebugFile_str)]
        elif self.libraryFile_str is not None and len(self.libraryFile_str) == 1:
            self.dataFiles = [TrafoXMLAccess(f, self.libraryFile_str[0], mz_f, im_f) for f, mz_f, im_f in zip(self.dataFiles_str, self.mzDebugFile_str, self.imDebugFile_str)]
    
    def __str__(self):
        return f"TrafoXMLLoader(dataFiles={self.dataFiles_str}, libraryFile={self.libraryFile_str}"

    def __repr__(self):
        return f"TrafoXMLLoader(dataFiles={self.dataFiles_str}, libraryFile={self.libraryFile_str}"
    
    
    def plot(self, debug_plot_type = "rt", split: bool = False):
        import pandas as pd
        from bokeh.plotting import show
        
        from massdash.plotting.DebugPlotter import DebugPlotter
        
        debug_plot_type_map = {
            "rt": ['experiment_rt', 'library_rt', 'Retention Time Transformation', 'Original RT [s]', 'Delta RT [s]'],
            "mz": ['mz', 'theo_mz', 'm/z calibration', 'Experiment m/z', 'Theoretical m/z'],
            "im": ['im', 'theo_im', 'Ion mobility calibration', 'Experiment Ion Mobility', 'Theoretical Ion Mobility']
        }
        
        if split:
            for i in range(len(self.dataFiles)):
                df = self.dataFiles[i].load_pairs_df()
                plotter = DebugPlotter()
                p = plotter.plot(df, *debug_plot_type_map[debug_plot_type])
                show(p)
        else:
            df = [self.dataFiles[i].load_pairs_df() for i in range(len(self.dataFiles))]
            df = pd.concat(df)

            plotter = DebugPlotter()
            p = plotter.plot(df, *debug_plot_type_map[debug_plot_type])
            show(p)