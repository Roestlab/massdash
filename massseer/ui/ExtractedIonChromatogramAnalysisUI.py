
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.ui.TransitionListUISettings import TransitionListUISettings

class ExtractedIonChromatogramAnalysisUI(TransitionListUISettings):
    def __init__(self, transition_list: SpectralLibraryLoader) -> None:
        super().__init__()
        self.transition_list = transition_list
        self.transition_settings = None
        self.target_transition_list = None

    def show_transition_information(self) -> None:
        # Create a UI for the transition list
        self.transition_settings = TransitionListUISettings()
        # Show proteins
        self.transition_settings.show_protein_selection(self.transition_list.get_unique_proteins())
        # Show peptides for selected protein
        self.transition_settings.show_peptide_selection(self.transition_list.get_unique_peptides_per_protein(self.transition_settings.selected_protein))
        # Show charge states for selected peptide
        self.transition_settings.show_charge_selection(self.transition_list.get_unique_charge_states_per_peptide(self.transition_settings.selected_peptide), self.transition_list)
        # Show library features
        self.transition_settings.show_library_features(self.transition_list)

        # Filter the transition list based on the selected protein, peptide and charge state
        self.target_transition_list =  self.transition_list.filter_for_target_transition_list(self.transition_settings.selected_protein, self.transition_settings.selected_peptide, self.transition_settings.selected_charge)