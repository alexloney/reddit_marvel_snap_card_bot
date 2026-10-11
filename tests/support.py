import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from catalog import Catalog, Card, Location


class StaticSource:
    """
    A Catalog source that hands back the Entries it was given. `fail` makes the
    next fetch raise, to simulate an upstream outage.
    """
    def __init__(self, *entries):
        self.set(*entries)
        self.fail = False

    def set(self, *entries):
        self.cards = [e for e in entries if isinstance(e, Card)]
        self.locations = [e for e in entries if isinstance(e, Location)]

    def fetch(self):
        if self.fail:
            raise RuntimeError('upstream unavailable')
        return list(self.cards), list(self.locations)


def build_catalog(*entries, **kwargs):
    catalog = Catalog(StaticSource(*entries), **kwargs)
    catalog.refresh()
    return catalog
