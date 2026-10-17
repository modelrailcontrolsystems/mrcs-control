"""
Created on 29 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/block/test_block_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest
from pathlib import Path

from mrcs_control.db.db_client import DbClient, DbMode
from mrcs_control.equipment.block.persistent_block_occupant import PersistentBlockOccupant
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_control.test.test_helper import TestHelper
from mrcs_core.equipment.block.block_address import BlockAddress
from mrcs_core.equipment.block.block_enums import BlockHeading, BlockOccupantFace, BlockVoltage
from mrcs_core.equipment.block.block_id import BlockID
from mrcs_core.equipment.block.block_occupant import BlockOccupant
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport
from mrcs_core.equipment.block.block_status import BlockStatus
from mrcs_core.layout.layout import Layout


# --------------------------------------------------------------------------------------------------------------------

class TestBlockPersistence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DbClient.set_client_db_mode(DbMode.TEST)
        TestHelper.dbSetup()
        cls.__setup_db()


    @classmethod
    def tearDownClass(cls):
        cls.__setup_db()
        TestHelper.dbTeardown()


    @classmethod
    def __setup_db(cls):
        PersistentBlockStatus.recreate_tables()

        abs_filename = Path(__file__).parent / 'data' / 'test_001_layout.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)

        layout = Layout.construct_from_jdict(jdict)

        for block in layout.block_abstract().items:
            PersistentBlockStatus.narrow(block).save()

        for turnout in layout.turnout_abstract().items:
            PersistentTurnoutStatus.narrow(turnout).save()


    def __find(self, label: str) -> PersistentBlockStatus:
        obj = PersistentBlockStatus.find(label)
        if obj is None:
            self.fail(f'block {label} not found')

        return obj


    # ----------------------------------------------------------------------------------------------------------------
    # each test resets the tables, so that tests that modify the DB do not affect those that follow

    def test_setup(self):
        self.__setup_db()
        objs = PersistentBlockStatus.find_all()
        self.assertEqual(16, len(objs))


    def test_find_all_order(self):
        self.__setup_db()
        labels = [obj.label for obj in PersistentBlockStatus.find_all()]
        self.assertEqual(sorted(labels), labels)


    def test_find(self):
        self.__setup_db()
        obj = PersistentBlockStatus.find('BS02')
        self.assertEqual('BlockStatus:{label:BS02, address:BlockAddress:{detector:5, channel:4}, heading:UNASSIGNED, '
                         'voltage:UNKNOWN, occupants:[]}', str(obj))


    def test_find_not_found(self):
        self.__setup_db()
        obj = PersistentBlockStatus.find('junk')
        self.assertIsNone(obj)


    def test_exists(self):
        self.__setup_db()
        exists = PersistentBlockStatus.exists('BS02')
        self.assertTrue(exists)


    def test_not_exists(self):
        self.__setup_db()
        exists = PersistentBlockStatus.exists('junk')
        self.assertFalse(exists)


    def test_turnouts(self):
        self.__setup_db()
        obj = self.__find('BS02')
        turnouts = obj.turnouts
        self.assertEqual(1, len(turnouts))
        self.assertEqual('TE01', turnouts[0].label)


    def test_turnouts_empty(self):
        self.__setup_db()
        obj = self.__find('BS01')
        self.assertEqual([], obj.turnouts)


    def test_save_new(self):
        self.__setup_db()
        obj1 = PersistentBlockStatus('BX01', BlockAddress(7, 1), BlockHeading.UP,
                                     BlockVoltage.OCCUPIED_WITH_VOLTAGE,
                                     BlockOccupant(17767, BlockOccupantFace.FACE_BACKWARD),
                                     BlockOccupant(4660, BlockOccupantFace.FACE_FORWARD))
        obj1.save()

        obj2 = PersistentBlockStatus.find('BX01')
        self.assertEqual(obj1, obj2)
        self.assertEqual(17, len(PersistentBlockStatus.find_all()))


    def test_save_replace(self):
        self.__setup_db()
        obj1 = self.__find('BS01')
        obj2 = PersistentBlockStatus(obj1.label, obj1.address, BlockHeading.DOWN, BlockVoltage.FREE_WITH_VOLTAGE,
                                     BlockOccupant(3, BlockOccupantFace.FACE_FORWARD))
        obj2.save()

        obj3 = PersistentBlockStatus(obj1.label, obj1.address, BlockHeading.UP, BlockVoltage.OCCUPIED_WITH_VOLTAGE,
                                     BlockOccupant(4, BlockOccupantFace.FACE_BACKWARD))
        obj3.save()

        obj4 = PersistentBlockStatus.find('BS01')
        self.assertEqual(obj3, obj4)                    # previous occupants have been removed
        self.assertEqual(16, len(PersistentBlockStatus.find_all()))


    def test_save_cascades_turnouts(self):
        self.__setup_db()
        obj1 = self.__find('BS02')
        obj2 = PersistentBlockStatus(obj1.label, obj1.address, BlockHeading.UP, BlockVoltage.OCCUPIED_WITH_VOLTAGE)
        obj2.save()                                     # REPLACE deletes the block's turnouts by cascade

        self.assertIsNone(PersistentTurnoutStatus.find('TE01'))
        self.assertEqual([], obj2.turnouts)


    def test_save_duplicate_address(self):
        self.__setup_db()
        obj1 = self.__find('BS01')
        obj2 = PersistentBlockStatus('BX01', obj1.address, BlockHeading.UP, BlockVoltage.UNKNOWN)
        obj2.save()                                     # REPLACE resolves the UNIQUE address conflict

        self.assertFalse(PersistentBlockStatus.exists('BS01'))
        self.assertTrue(PersistentBlockStatus.exists('BX01'))


    def test_find_all_with_occupants(self):
        self.__setup_db()
        obj1 = self.__find('BS03')
        obj2 = PersistentBlockStatus(obj1.label, obj1.address, obj1.heading, obj1.voltage,
                                     BlockOccupant(3, BlockOccupantFace.FACE_FORWARD),
                                     BlockOccupant(4, BlockOccupantFace.FACE_BACKWARD))
        obj2.save()

        objs = {obj.label: obj for obj in PersistentBlockStatus.find_all()}
        self.assertEqual(obj2, objs['BS03'])
        self.assertEqual([], objs['BS04'].occupants)


    def test_update_from_voltage(self):
        self.__setup_db()
        report = BlockVoltageReport(BlockID(BlockAddress(5, 4), 0x1234), BlockVoltage.OCCUPIED_WITH_VOLTAGE)

        obj1 = PersistentBlockStatus.update_from_voltage(report)
        self.assertEqual('BS02', obj1.label)
        self.assertEqual(BlockVoltage.OCCUPIED_WITH_VOLTAGE, obj1.voltage)

        obj2 = PersistentBlockStatus.find('BS02')
        self.assertEqual(obj1, obj2)


    def test_update_from_voltage_preserves_occupants(self):
        self.__setup_db()
        obj1 = self.__find('BS02')
        obj2 = PersistentBlockStatus(obj1.label, obj1.address, obj1.heading, obj1.voltage,
                                     BlockOccupant(3, BlockOccupantFace.FACE_FORWARD))
        obj2.save()

        report = BlockVoltageReport(BlockID(obj1.address, 0x1234), BlockVoltage.OCCUPIED_NO_VOLTAGE)
        obj3 = PersistentBlockStatus.update_from_voltage(report)
        self.assertEqual(obj2.occupants, obj3.occupants)


    def test_update_from_voltage_not_found(self):
        self.__setup_db()
        report = BlockVoltageReport(BlockID(BlockAddress(9, 9), 0x1234), BlockVoltage.OCCUPIED_WITH_VOLTAGE)

        with self.assertRaises(KeyError):
            PersistentBlockStatus.update_from_voltage(report)


    def test_update_from_block_occupancy_report(self):
        self.__setup_db()
        occupants = [BlockOccupant(4660, BlockOccupantFace.FACE_FORWARD),
                     BlockOccupant(17767, BlockOccupantFace.FACE_BACKWARD)]
        report = BlockOccupancyReport(BlockID(BlockAddress(5, 4), 0x1234), 1, occupants)

        obj1 = PersistentBlockStatus.update_from_block_occupancy_report(report)
        self.assertEqual('BS02', obj1.label)
        self.assertEqual(occupants, obj1.occupants)

        obj2 = PersistentBlockStatus.find('BS02')
        self.assertEqual(obj1, obj2)


    def test_update_from_block_occupancy_report_replaces(self):
        self.__setup_db()
        address = BlockAddress(5, 4)

        report = BlockOccupancyReport(BlockID(address, 0x1234), 1, [BlockOccupant(3, BlockOccupantFace.FACE_FORWARD)])
        PersistentBlockStatus.update_from_block_occupancy_report(report)

        report = BlockOccupancyReport(BlockID(address, 0x1234), 1, [])
        obj = PersistentBlockStatus.update_from_block_occupancy_report(report)
        self.assertEqual([], obj.occupants)


    def test_update_from_block_occupancy_report_not_found(self):
        self.__setup_db()
        report = BlockOccupancyReport(BlockID(BlockAddress(9, 9), 0x1234), 1, [])

        with self.assertRaises(KeyError):
            PersistentBlockStatus.update_from_block_occupancy_report(report)


    def test_delete_block(self):
        self.__setup_db()
        PersistentBlockStatus.delete_block('BS01')

        self.assertIsNone(PersistentBlockStatus.find('BS01'))
        self.assertEqual(15, len(PersistentBlockStatus.find_all()))


    def test_delete_block_cascades(self):
        self.__setup_db()
        report = BlockOccupancyReport(BlockID(BlockAddress(5, 4), 0x1234), 1,
                                      [BlockOccupant(3, BlockOccupantFace.FACE_FORWARD)])
        PersistentBlockStatus.update_from_block_occupancy_report(report)

        PersistentBlockStatus.delete_block('BS02')

        self.assertIsNone(PersistentTurnoutStatus.find('TE01'))
        self.assertEqual([], PersistentTurnoutStatus.find_for_block('BS02'))

        # re-create the block - no orphaned occupants should re-appear
        PersistentBlockStatus('BS02', BlockAddress(5, 4), BlockHeading.UNASSIGNED, BlockVoltage.UNKNOWN).save()
        self.assertEqual([], self.__find('BS02').occupants)


    def test_delete_block_not_found(self):
        self.__setup_db()
        PersistentBlockStatus.delete_block('junk')
        self.assertEqual(16, len(PersistentBlockStatus.find_all()))


    def test_delete_occupants(self):
        self.__setup_db()
        block_id = BlockID(BlockAddress(5, 4), 0x1234)
        report = BlockOccupancyReport(block_id, 1, [BlockOccupant(3, BlockOccupantFace.FACE_FORWARD),
                                                    BlockOccupant(4, BlockOccupantFace.FACE_BACKWARD)])
        PersistentBlockStatus.update_from_block_occupancy_report(report)

        PersistentBlockStatus.delete_occupants(block_id)

        obj = self.__find('BS02')                       # the block itself is not deleted
        self.assertEqual([], obj.occupants)


    # ----------------------------------------------------------------------------------------------------------------

    def test_narrow(self):
        obj1 = BlockStatus('BX01', BlockAddress(7, 1), BlockHeading.UP, BlockVoltage.FREE_WITH_VOLTAGE)
        obj2 = PersistentBlockStatus.narrow(obj1)
        self.assertIsInstance(obj2, PersistentBlockStatus)
        self.assertEqual(obj1, obj2)


    def test_construct_from_db(self):
        obj = PersistentBlockStatus.construct_from_db(['BX01', '7/1', 'UP', 'FREE_WITH_VOLTAGE'],
                                                      ['4660', 'FACE_FORWARD'])
        self.assertEqual('BlockStatus:{label:BX01, address:BlockAddress:{detector:7, channel:1}, heading:UP, '
                         'voltage:FREE_WITH_VOLTAGE, occupants:[BlockOccupant:{mpu_address:4660, face:FACE_FORWARD}]}',
                         str(obj))


    def test_as_db_insert(self):
        obj = PersistentBlockStatus('BX01', BlockAddress(7, 1), BlockHeading.UP, BlockVoltage.FREE_WITH_VOLTAGE)
        self.assertEqual(('BX01', '7/1', 'UP', 'FREE_WITH_VOLTAGE'), obj.as_db_insert())


    def test_as_db_update(self):
        obj = PersistentBlockStatus('BX01', BlockAddress(7, 1), BlockHeading.UP, BlockVoltage.FREE_WITH_VOLTAGE)
        with self.assertRaises(NotImplementedError):
            obj.as_db_update()


    def test_children(self):
        obj = PersistentBlockStatus('BX01', BlockAddress(7, 1), BlockHeading.UP, BlockVoltage.FREE_WITH_VOLTAGE,
                                    BlockOccupant(4660, BlockOccupantFace.FACE_FORWARD))
        children = obj.children()
        self.assertEqual(1, len(children))
        self.assertIsInstance(children[0], PersistentBlockOccupant)
        self.assertEqual((4660, 'FACE_FORWARD'), children[0].as_db_insert())


    def test_type_name(self):
        self.assertEqual('BlockStatus', PersistentBlockStatus.type_name())


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
