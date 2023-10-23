import unittest
from snapshottest import TestCase
from massseer.data_loader import process_file

class TestProcessFile(TestCase):
    def test_process_file(self):
        # Test case 1: include_ms1=True, include_ms2=True
        file_path = "test_data/xics/test_chrom_1.sqMass"
        include_ms1 = True
        include_ms2 = True
        precursor_id = 30
        transition_id_list = [180, 181, 182, 183, 183, 185]
        trace_annotation = ["y4^1", "y3^1", "y6^1", "Y5^1", "y7^1", "y1^1"]
        output = process_file(file_path, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation)

        self.assertMatchSnapshot(output)

        # Test case 2: include_ms1=True, include_ms2=False
        file_path = "test_data/xics/test_chrom_1.sqMass"
        include_ms1 = True
        include_ms2 = False
        precursor_id = 30
        transition_id_list = [180, 181, 182, 183, 183, 185]
        trace_annotation = ["y4^1", "y3^1", "y6^1", "Y5^1", "y7^1", "y1^1"]
        output = process_file(file_path, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation)

        self.assertMatchSnapshot(output)

        # Test case 3: include_ms1=False, include_ms2=True
        file_path = "test_data/xics/test_chrom_1.sqMass"
        include_ms1 = False
        include_ms2 = True
        precursor_id = 30
        transition_id_list = [180, 181, 182, 183, 183, 185]
        trace_annotation = ["y4^1", "y3^1", "y6^1", "Y5^1", "y7^1", "y1^1"]
        output = process_file(file_path, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation)

        self.assertMatchSnapshot(output)

        # Test case 4: include_ms1=False, include_ms2=False
        file_path = "test_data/xics/test_chrom_1.sqMass"
        include_ms1 = False
        include_ms2 = False
        precursor_id = 30
        transition_id_list = [180, 181, 182, 183, 183, 185]
        trace_annotation = ["y4^1", "y3^1", "y6^1", "Y5^1", "y7^1", "y1^1"]
        output = process_file(file_path, include_ms1, include_ms2, precursor_id, transition_id_list, trace_annotation)

        self.assertMatchSnapshot(output)

if __name__ == '__main__':
    unittest.main()