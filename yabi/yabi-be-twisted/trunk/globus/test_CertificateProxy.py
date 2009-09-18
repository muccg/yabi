import CertificateProxy
from twisted.trial import unittest, reporter, runner
import os

TEST_CERT = """Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 13 (0xd)
        Signature Algorithm: sha1WithRSAEncryption
        Issuer: O=YABIGrid, OU=YABI, OU=ccg.murdoch.edu.au, CN=YABI CA
        Validity
            Not Before: Sep 18 05:38:56 2009 GMT
            Not After : Sep 18 05:38:56 2010 GMT
        Subject: O=YABIGrid, OU=YABI, OU=ccg.murdoch.edu.au, OU=localdomain, CN=Testing User
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
            RSA Public Key: (1024 bit)
                Modulus (1024 bit):
                    00:e2:28:dc:9b:d4:64:90:64:aa:22:63:45:b4:45:
                    b3:8d:af:70:d9:87:6b:96:50:3e:1b:ed:80:e9:29:
                    55:b4:5f:78:0b:0e:06:d5:89:10:e0:a8:bb:ab:0f:
                    6d:fe:48:7e:2c:84:3b:f4:d0:d6:1c:83:fe:d3:35:
                    47:2b:fb:72:c9:73:95:43:de:29:ba:21:83:26:48:
                    8c:aa:3c:a7:c2:37:62:a4:76:dc:52:b6:ba:26:12:
                    d0:6f:30:88:33:75:e4:c3:90:72:e5:b4:04:fa:d0:
                    1c:13:c6:32:70:a5:1b:21:41:09:5d:43:60:45:0c:
                    9b:a7:d7:b9:4d:48:a4:b9:9d
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            Netscape Cert Type: 
                SSL Client, SSL Server, S/MIME, Object Signing
    Signature Algorithm: sha1WithRSAEncryption
        55:17:b3:9b:25:ae:08:bb:c2:8b:17:09:e7:26:6e:dd:42:d7:
        6f:20:91:92:2e:08:e9:86:0e:7f:0f:ca:40:ba:bc:a6:89:ca:
        23:8e:ae:b0:e4:fb:f1:e0:1b:a4:85:a5:08:02:cf:84:74:c2:
        54:0d:b8:2b:fb:dd:5f:b9:f7:5a:05:9e:a2:86:24:5e:15:58:
        3c:38:f9:43:e4:cf:46:5f:85:a4:fc:ef:f8:78:db:97:33:f5:
        98:86:ee:c3:02:b9:03:d9:e9:c0:04:30:81:6d:a9:3a:05:5c:
        22:03:0e:7a:62:7e:5e:0c:80:1b:93:5c:9b:28:8b:c9:a4:f9:
        56:b0
-----BEGIN CERTIFICATE-----
MIICSDCCAbGgAwIBAgIBDTANBgkqhkiG9w0BAQUFADBRMREwDwYDVQQKEwhZQUJJ
R3JpZDENMAsGA1UECxMEWUFCSTEbMBkGA1UECxMSY2NnLm11cmRvY2guZWR1LmF1
MRAwDgYDVQQDEwdZQUJJIENBMB4XDTA5MDkxODA1Mzg1NloXDTEwMDkxODA1Mzg1
NlowbDERMA8GA1UEChMIWUFCSUdyaWQxDTALBgNVBAsTBFlBQkkxGzAZBgNVBAsT
EmNjZy5tdXJkb2NoLmVkdS5hdTEUMBIGA1UECxMLbG9jYWxkb21haW4xFTATBgNV
BAMTDFRlc3RpbmcgVXNlcjCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEA4ijc
m9RkkGSqImNFtEWzja9w2YdrllA+G+2A6SlVtF94Cw4G1YkQ4Ki7qw9t/kh+LIQ7
9NDWHIP+0zVHK/tyyXOVQ94puiGDJkiMqjynwjdipHbcUra6JhLQbzCIM3Xkw5By
5bQE+tAcE8YycKUbIUEJXUNgRQybp9e5TUikuZ0CAwEAAaMVMBMwEQYJYIZIAYb4
QgEBBAQDAgTwMA0GCSqGSIb3DQEBBQUAA4GBAFUXs5slrgi7wosXCecmbt1C128g
kZIuCOmGDn8PykC6vKaJyiOOrrDk+/HgG6SFpQgCz4R0wlQNuCv73V+591oFnqKG
JF4VWDw4+UPkz0ZfhaT87/h425cz9ZiG7sMCuQPZ6cAEMIFtqToFXCIDDnpifl4M
gBuTXJsoi8mk+Vaw
-----END CERTIFICATE-----
"""

TEST_KEY = """-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,4444C0BE11DD02BB

xJLnGrCzpWvt9judU4RRl9sEZ74EBkIkqdVXBzDmM3lIji0DwwQWyWhs9Ehu6Z8z
qUZ16UdBiWdS8JsHFWQa79i+2XT9DHN2zajqF3I9/pJ1BBkgWmPDsHy1Fb+hSt6O
Rmp38bpYA23u2yV7tiHiENu9pnWDSs74R1TMGpSZX/lPeNHXlcgJUcwOVvvWit/I
RRm/6ZACybSiQ2Vv6CBTo2ExiDqaR64Cz6BfMTDOKIIz0rj5Atp84hWUV3LMEaCt
M4noiONFWSNMqvlnYphuzxvB9hVrF1XBN1NNl1ZJSMGMxbXqNK1H4Iq0vUSt48cv
ODkEFLNKggZoqDuAAvWtsv3UdNQX9pUn6wcLKjl+6aQtpK7iBjZPFq1U0oyOZD2p
05S4qGI/N7geQAegAk12hpJ1BQXqFnNRJHqPEBhyfDLOeTcaLbEOvEKZjSYQg4LI
rpaAsRAhmwSJCYc9ByiP0nan9CewcIMQuWyLZekbzKNh0v6PUDAc4FFUUXZdB/9d
XdcRPYG5KcdlFffY3jkbxswhM0ruzKQWMzvGg+Ke8BTqBtlK4rEFhfyHWOPg6T8I
uA4W/81lzpomM1srF1GcVpWONs5UIOsY8rNUQNuNDy4K3BksOCmU12mUWB8Ejke7
g49A9ojD5gGlCRVYyPa1XMGmuCO7domslp8G+3k+vE0O3bV64rKT7Tz5KPKjSzYU
Zd4Sc0DTMo5MVCVSXGqV/CtG8kO0NM7VPDHZO4Qm+mO2g7oXIQTrX/xKtRBy0jVw
mBhcDDtYK60lxLByc853hAQEVD2rnh6iBC2rKLQnIu8gubz0l/crvQ==
-----END RSA PRIVATE KEY-----
"""

TEST_KEY_PW = "1234567890"

class TestSetup(unittest.TestCase):
    """Test the server sets up correctly and tears down correctly."""
    _suppressUpDownWarning = True
    PORT = 9000

    def setUpClass(self):
        self.proxy = CertificateProxy.CertificateProxy()

    def test_certificate_stores_created(self):
        """Check that the storage is created"""
        self.failUnless( os.path.exists(self.proxy.storage) )
        
    def test_unauthed_user_proxy_is_invalid(self):
        self.assert_( self.proxy.IsProxyValid('dummy_user')==False )
        
    def test_create_valid_user_proxy(self):
        """Test that we can successfuly create a user proxy cert"""
        self.proxy.CreateUserProxy('test_user', TEST_CERT, TEST_KEY, TEST_KEY_PW)
        self.assert_( os.path.exists( self.proxy.ProxyFile('test_user') ) )
        self.assert_( self.proxy.IsProxyValid('test_user') )
        
    def test_create_invalid_user_proxy(self):
        INVALID_CERT = TEST_CERT.split()
       
        # change 20 characters randomly
        import random
        for i in range(20):
            INVALID_CERT[random.randint(0,len(INVALID_CERT)-1)]=random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            
        INVALID_CERT = "".join(INVALID_CERT)
            
        self.assertRaises(CertificateProxy.ProxyInitError,self.proxy.CreateUserProxy,'test_user', INVALID_CERT, TEST_KEY, TEST_KEY_PW)
        
    def test_invalid_cert_password(self):
        self.assertRaises(CertificateProxy.ProxyInvalidPassword,self.proxy.CreateUserProxy,'test_user', TEST_CERT, TEST_KEY, "this is an invalid password")
        
    def test_zzz_cleanup(self):
        """Test that the cleanup script works"""
        directory = self.proxy.storage
        self.failUnless( os.path.exists(directory) )
        self.proxy.CleanUp()
        self.failIf( os.path.exists(directory) )

