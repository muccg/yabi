# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from crypto_utils import encrypt_to_annotated_block, \
    decrypt_annotated_block, looks_like_annotated_block, DecryptException


class CryptoTest(unittest.TestCase):
    TEST_KEY = 'percy_is_a_budgerigar'
    # nonce is a number used once - you would not normally hard-code this, but
    # it is required for tests so that output of the encryption function remains
    # constant over consecutive runs
    TEST_NONCE = [59, 191, 174, 66, 108, 252, 184, 77]

    TEST_PAIRS = [
        # test a simple password-ish string
        ('chicken', '$AESCTR$7MQ6Y/z3xlWDDA9104mTejDyQPM7v65CbPy4TaNvVFXX+XY=$'),
        # test a really long, ascii string
        ('chickens have beaks ' * 10,
            '$AESCTR$MJJjGptEshL1q+7rrLB51sQpgWk7v65CbPy4TaNvVFXX+XZqj2KFGRE5Qo'
            'gvLByEqAiiMF8VtRXG7h4/p/gGzBg6WDDSvgbSwbGIJNTL1wzxtuec9HhtMq/PwScJ'
            'XTeTAJpwu3BMXBXGzhS8j+vU1+ayMsBM1p1ZqhwoWKlHMSK5pncIbrVBIYDeUlGtUX'
            'MwFxsfMgkmvl9SKTVOoL1/Glo0Gux6SipVM+/PbNX5gLg8a7GgshHAH6dxppA3sf6n'
            'rEfqy5XLXO10N74sbIR7NBbZlyXMQevCAqz0jHCUElFOGPRE$'),
        # a blob of binary - start of grumpy cat JPEG
        ('\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF',
            '$AESCTR$u2fZloRU43p871YSWuSix1xHHmU7v65CbPy4TZx/W1Dg5Hwh83KCCShhRd'
            '0SP1+Ulxj6Y342kiA=$')
    ]

    def test_encrypt(self):
        for plaintext, encrypted in CryptoTest.TEST_PAIRS:
            self.assertEqual(encrypt_to_annotated_block(plaintext, CryptoTest.TEST_KEY, nonce=CryptoTest.TEST_NONCE), encrypted)

    def test_decrypt(self):
        for plaintext, encrypted in CryptoTest.TEST_PAIRS:
            self.assertEqual(decrypt_annotated_block(encrypted, CryptoTest.TEST_KEY), plaintext)

    def test_wrong_key_fails(self):
        for _, encrypted in CryptoTest.TEST_PAIRS:
            with self.assertRaises(DecryptException):
                decrypt_annotated_block(encrypted, 'wrong' + CryptoTest.TEST_KEY)

    def test_encrypt_empty_string(self):
        self.assertEqual(encrypt_to_annotated_block("", CryptoTest.TEST_PAIRS), "")

    def test_decrypt_empty_string(self):
        self.assertEqual(decrypt_annotated_block("", CryptoTest.TEST_PAIRS), "")

    def test_looks_like_annotated_block(self):
        for _, encrypted in CryptoTest.TEST_PAIRS:
            self.assertTrue(looks_like_annotated_block(encrypted))

    def test_not_looks_like_annotated_block_empty_string(self):
        self.assertFalse(looks_like_annotated_block(""))

    def test_not_looks_like_annotated_block(self):
        for plaintext, _ in CryptoTest.TEST_PAIRS:
            self.assertFalse(looks_like_annotated_block(plaintext))
