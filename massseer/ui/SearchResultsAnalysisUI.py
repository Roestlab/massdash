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
        self.analysis = st.sidebar.selectbox("Analysis type", ["Identifications", "Quantifications", "Score Distributions"])
        
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


    