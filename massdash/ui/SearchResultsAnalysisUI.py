"""
massdash/ui/SearchResultsAnalysisUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st

class SearchResultsAnalysisUI:
    """
    A class representing the user interface 


    """

    def __init__(self) -> None:
        """
        Initializes the ExtractedIonChromatogramAnalysisServer object.

        
        """
        self.analysis = None
        self.selected_score_table = None
        self.selected_score_col = None
        self.selected_score_table_context = None
        
    def analysis_type(self):
        """
        Displays the transition list UI and filters the transition list based on user input.
        """
        # Create a UI for the transition list
        self.analysis = st.sidebar.selectbox("Analysis type", ["Results", "Score Distributions"], help="Select the type of analysis to perform.")
    
    def show_identification_settings(self):
        """
        Displays the identification settings.
        """
        st.sidebar.divider()
        st.sidebar.subheader("Results settings")
        self.biological_level = st.sidebar.selectbox("Biological level", ["Protein", "Peptide", "Precursor"], index=1, help="Select the composition level for the identifications.")
        
        self.qvalue_threshold = st.sidebar.number_input("Qvalue threshold", value=0.01, min_value=0.0, max_value=1.0, step=0.01, key=f'identification_settings_fdr_threshold', help="FDR threshold for identifications.")
        
        # Checkbox to aggregate identifications
        self.aggregate_identifications = st.sidebar.checkbox("Aggregate identifications", value=True, key=f'aggregate_identifications', help="Aggregate identifications per entry.")
        
        # Number of columns for the plots
        self.num_cols = st.sidebar.number_input("Number of columns for plots", value=2, min_value=1, max_value=4, step=1, key=f'num_cols', help="Number of columns for the plots.")
        
        # Multiple select for the type of plots
        self.plot_types = st.sidebar.multiselect("Select plot types", ["Identification", "Quantification", "CV", "UpSet"], default=["Identification", "Quantification", "CV", "UpSet"], key=f'plot_types', help="Select the type of plots to display.")
        
    def show_score_tables(self, data_access_dict):
        """
        Displays the score tables in the database
        """
        score_tables = []
        for entry, data_access in data_access_dict.items():
            score_tables.extend(data_access.get_score_tables())
        score_tables = list(set(score_tables))
        score_tables.sort()
        self.selected_score_table = st.sidebar.selectbox("Select score table", score_tables, index=score_tables.index("SCORE_MS2"))
        
    def show_score_table_contexts(self, data_access_dict):
        """
        Displays the score table contexts.
        """
        score_table_contexts = []
        for entry, data_access in data_access_dict.items():
            score_table_contexts.extend(data_access.get_score_table_contexts(self.selected_score_table))
        score_table_contexts = list(set(score_table_contexts))
        score_table_contexts.sort()
        if 'global' in score_table_contexts:
            use_index = score_table_contexts.index('global')
        else:
            use_index = 0
        self.selected_score_table_context = st.sidebar.selectbox("Select score table context", score_table_contexts, index=use_index)
    
    def show_score_distribution_score_colums(self, data_access_dict):
        """
        Displays the score distribution score columns.
        """
        score_columns = ["SCORE", "QVALUE", "PVALUE", "PEP"]
        
        for entry, df in data_access_dict.items():
            current_cols = [c for c in df.columns if c.startswith("MAIN_VAR_")] + [c for c in df.columns if c.startswith("VAR_")]
            # Check which columns are Null, None or NaN, and if they are, remove them from the current_cols list
            current_cols = [c for c in current_cols if df[c].notnull().any()]            
            score_columns.extend(current_cols)
            
        # Get unique columns
        score_columns = list(set(score_columns))
        # Order alphabetically
        score_columns.sort()
        if 'SCORE' in score_columns:
            use_index = score_columns.index('SCORE')
        elif 'QVALUE' in score_columns:
            use_index = score_columns.index('QVALUE')
        else:
            use_index = 0
            
        self.selected_score_col = st.sidebar.selectbox("Select score column", score_columns, index=use_index)


    def show_plots(self, plot_container: st.container, plot_dict: dict, num_cols=2):
        """
        Displays the plots.
        """
        # Create a UI for the plots
        with plot_container:
            plot_cols = st.columns(num_cols)
            col_counter = 0
            for plot_type, plot_obj in plot_dict.items():
                with plot_cols[col_counter]:
                    if plot_type == "identifications":
                        st.bokeh_chart(plot_obj, use_container_width=True)
                    elif plot_type == "quantifications" or plot_type == "coefficient_of_variation":
                        st.plotly_chart(plot_obj, use_container_width=True)
                    elif plot_type == "upset_diagram":
                        # st.pyplot(plot_obj, use_container_width=True)
                        st.image(plot_obj, use_column_width=True)
                    
                    col_counter+=1
                    if col_counter >= len(plot_cols):
                        col_counter = 0