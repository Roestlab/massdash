import unittest
from massdash.structs.TargetedDIAConfig import TargetedDIAConfig

class TestTargetedDIAConfig(unittest.TestCase):

    def setUp(self):
        self.config = TargetedDIAConfig()
    def test_update(self):
        config = TargetedDIAConfig()
        config_dict = {
            'ms1_mz_tol': 50,
            'mz_tol': 40,
            'rt_window': 15,
            'im_window': 0.05,
            'mslevel': [1]
        }
        config.update(config_dict)
        self.assertEqual(config.ms1_mz_tol, 50)
        self.assertEqual(config.mz_tol, 40)
        self.assertEqual(config.rt_window, 15)
        self.assertEqual(config.im_window, 0.05)
        self.assertEqual(config.mslevel, [1])

    def test_get_upper_lower_tol(self):
        mz = 100
        ppm = 50
        config = TargetedDIAConfig()
        config.mz_tol = ppm
        lower_tol, upper_tol = config.get_upper_lower_tol(mz)
        self.assertEqual(upper_tol, 100 + 100 * (ppm/2) * 1e-6) # 100.0025
        self.assertEqual(lower_tol, 100 - 100 * (ppm/2) * 1e-6) # 99.9975

    def test_get_upper_lower_rt(self):
        config = TargetedDIAConfig()
        window = 40
        rt = 100
        config.rt_window = window
        lower_rt, upper_rt = config.get_rt_upper_lower(rt)
        self.assertEqual(lower_rt, rt - window/2) # 80
        self.assertEqual(upper_rt, rt + window/2) # 120
    
    def test_get_im_upper_lower(self):
        ## Case 1: StartIM and EndIM are not set
        config = TargetedDIAConfig()
        config.im_window = 0.1
        lower_im, upper_im = config.get_im_upper_lower(1)
        self.assertEqual(upper_im, 1 + 0.1/2) # 0.105
        self.assertEqual(lower_im, 1 - 0.1 /2) # 0.095

        ## Case 2: StartIM and EndIM are set
        config = TargetedDIAConfig()
        config.im_start = 0.6
        config.im_end = 0.65
        lower_im, upper_im = config.get_im_upper_lower(1) # note that the argument is not used
        self.assertEqual(upper_im, 0.65)
        self.assertEqual(lower_im, 0.6)

        ## Case 3: StartIM is set, EndIM is not set should ignore StartIM
        config = TargetedDIAConfig()
        config.im_start = 0.6
        config.im_window = 0.1
        lower_im, upper_im = config.get_im_upper_lower(1)
        self.assertEqual(upper_im, 1 + 0.1/2) # 0.105
        self.assertEqual(lower_im, 1 - 0.1/2) # 0.095

        ## Case 4: StartIM is not set, EndIM is set should ignore EndIM
        config = TargetedDIAConfig()
        config.im_end = 0.65
        config.im_window = 0.1
        lower_im, upper_im = config.get_im_upper_lower(1)
        self.assertEqual(upper_im, 1 + 0.1/2) # 0.105
        self.assertEqual(lower_im, 1 - 0.1/2) # 0.095

    def test_is_mz_in_product_mz_tol_window(self):
        config = TargetedDIAConfig()
        self.assertTrue(config.is_mz_in_product_mz_tol_window(100, [(100, 105)])) # lower boundary is inclusive
        self.assertTrue(config.is_mz_in_product_mz_tol_window(105, [(100,105 )])) # upper boundary is inclusive 
        self.assertFalse(config.is_mz_in_product_mz_tol_window(95, [(100, 105)])) 


if __name__ == '__main__':
    unittest.main()
