class AttributeDict(object):
    """
    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttributeDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)
    """

    def __init__(self, **entries):
        self.add_entries(**entries)

    def add_entries(self, **entries):
        for key, value in entries.items():
            self.add_entry(key, value)

    def add_entry(self, key, value):
        if type(value) is dict:
            self.__dict__[key] = AttributeDict(**value)
        else:
            self.__dict__[key] = value

    def has_entry(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)
