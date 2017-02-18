#!/usr/bin/env python
#
# Copyright (C) 2013 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
"""
Test crontab ranges.
"""

import os
import sys

sys.path.insert(0, '../')

import unittest
from crontab import CronTab, CronSlice, PY3
try:
    from test import test_support
except ImportError:
    from test import support as test_support

if PY3:
    unicode = str

class RangeTestCase(unittest.TestCase):
    """Test basic functionality of crontab."""
    def setUp(self):
        self.crontab = CronTab(tab="")

    def test_01_atevery(self):
        """At Every"""
        tab = CronTab(tab="""
*  *  *  *  * command
61 *  *  *  * command
*  25 *  *  * command
*  *  32 *  * command
*  *  *  13 * command
*  *  *  *  8 command
        """)
        self.assertEqual(len(tab), 1)

    def test_02_withinevery(self):
        """Within Every"""
        tab = CronTab(tab="""
*    *    *    *    * command
1-61 *    *    *    * command
*    1-25 *    *    * command
*    *    1-32 *    * command
*    *    *    1-13 * command
*    *    *    *    1-8 command
        """)
        self.assertEqual(len(tab), 1)

    def test_03_outevery(self):
        """Out of Every"""
        tab = CronTab(tab="""
*    *    *    *    *   command
*/61 *    *    *    *   command
*    */25 *    *    *   command
*    *    */32 *    *   command
*    *    *    */13 *   command
*    *    *    *    */8 command
        """)
        self.assertEqual(len(tab), 1)
        
    def test_04_zero_seq(self):
        tab = CronTab(tab="""
*/0 * * * * command
        """)
        self.assertEqual(len(tab), 0)

    def test_05_sunday(self):
        """Test all possible day of week combinations"""
        for (a, b) in (
          ("7", "0"), ("5-7", "0,5-6"), ("1-7","*"), ("*/7", "0"),
          ("0-6", "*"), ("2-7", "0,2-6"), ("1-5", "1-5"), ("0-5", "0-5")):
            v = str(CronSlice(4, a))
            self.assertEqual(v, b, "%s != %s, from %s" % (v, b, a))

if __name__ == '__main__':
    test_support.run_unittest(
       RangeTestCase,
    )
