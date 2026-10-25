"""
Created on 19 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

A prolog route finder
"""

from pathlib import Path

import janus_swi as janus

from mrcs_core.layout.route import Route
from mrcs_core.layout.segment.prolog_link import PrologLink
from mrcs_core.layout.segment.prolog_segment import PrologSegment
from mrcs_core.layout.segment.segment_location import SegmentLocation
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class RoutePlanner(object):
    """
    A prolog route finder
    """

    __ROUTE_FILE = Path(__file__).parent / 'route.pro'


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, segments: list[PrologSegment], links: list[PrologLink]):
        self.__segments = segments
        self.__links = links
        self.__initialised = False

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def initialise(self):
        janus.consult('segments', data='\n'.join(map(repr, self.segments)))
        for segment in self.segments:
            self.logger.debug(repr(segment))

        janus.consult('links', data='\n'.join(map(repr, self.links)))
        for link in self.links:
            self.logger.debug(repr(link))

        janus.consult(str(self.__ROUTE_FILE))

        self.__initialised = True


    def route(self, start: SegmentLocation, end: SegmentLocation):
        if not self.initialised:
            raise RuntimeError('initialise before invoking route')

        params = {'Start': start.as_prolog(), 'End': end.as_prolog(), 'ConfIn': []}
        query = janus.query('route(Start, End, Length, Dir, Route, ConfIn, ConfOut)', params)

        try:
            routes = [Route.construct_from_prolog(pdict) for pdict in query]
        finally:
            query.close()

        return routes


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def segments(self):
        return self.__segments


    @property
    def links(self):
        return self.__links


    @property
    def initialised(self):
        return self.__initialised


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'RoutePlanner:{{segments:{self.segments}, links:{self.links}, initialised:{self.initialised}}}'
