from massdash.plotting.GenericPlotter import PlotConfig
import pytest

class TestPlotConfig:

    @pytest.mark.parametrize('include_ms1,include_ms2,expected', [
        (True, True, 'ms1ms2'),
        (True, False, 'ms1'),
        (False, True, 'ms2'),
    ])
    def test_update(self, include_ms1, include_ms2, expected):
        config = PlotConfig()
        config.update({'include_ms1': include_ms1, 'include_ms2': include_ms2})
        assert config.include_ms1 == include_ms1
        assert config.include_ms2 == include_ms2
        assert config.ms_level_str == expected

    def test_update_invalid_key(self):
        config = PlotConfig()
        config.update({'invalid_key': 'invalid_value'})

        # invalid key should not be saved
        assert not hasattr(config, 'invalid_key')