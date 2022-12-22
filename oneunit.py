class Measure:
    prefix = {'nano', 'micro', 'pico', 'femto', 'mili', 'centi', 'deci',
              'none', 'deca', 'hecta', 'kilo', 'mega', 'giga', 'peta', 'exo', 'tera', 'zato'}  # Note: not corect order

    abr = {}
    unit_type = {'len', 'time'}  # todo list: and use that combo units, mabe dataframe, abrevi,imper

    def __init__(self, val,unit='m'):
        self.val = val
        self.unit = unit  # todo if string

    def __str__(self):
        return f"{self.val} {self.unit}"

    def unit_set(self):
        pass

    def type_set(self):
        pass

    def convert(self):
        pass

    def prefix_get(self):
        pass

    def imperial_frac(self,base):
        pass
