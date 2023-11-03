class Product:
    '''
    Class to represent a product ion
    '''
    def __init__(self, mz: float, charge: int, annotation: str):
        self.mz = mz
        self.charge = charge
        self.annotation = annotation