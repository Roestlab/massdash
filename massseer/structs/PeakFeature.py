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

    def __str__(self):
        return f"PeakFeature\nApex: {self.apex}\nLeftWidth: {self.leftWidth}\nRightWidth: {self.rightWidth}\nArea: {self.area_intensity}\nQvalue: {self.qvalue}"