class PeakFeature:
    '''
    This is a generic PeakFeature Object. All Peak Picking algorithms should an object of this class 
    '''

    def __init__(self, area_intensity=None, apex=None, leftWidth=None, rightWidth=None, qvalue=None):

        self.apex = apex
        self.leftWidth = leftWidth
        self.rightWidth = rightWidth
        self.area_intensity = area_intensity
        self.qvalue = qvalue
