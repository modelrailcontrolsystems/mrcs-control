"""
Created on 21 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

The track state
"""

from mrcs_core.data.json import PersistentJSONable
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport


# --------------------------------------------------------------------------------------------------------------------

class PersistentTrack(TrackReport, PersistentJSONable):
    """
     the track state
     """

    __FILENAME = "track.json"


    @classmethod
    def persistence_location(cls):
        return cls.conf_dir(), cls.__FILENAME


    @classmethod
    def type_name(cls):
        return TrackReport.type_name()  # Persistent classes are for internal use - advertise the base class


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, mode: TrackMode):
        super().__init__(mode)
