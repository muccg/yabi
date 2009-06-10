import CertificateProxy
import GlobusURLCopy

# module level "singleton"
Certificates = CertificateProxy.CertificateProxy()
Globus = GlobusURLCopy.GlobusURLCopy()


def setup_proxy(proxy):
    cert = """Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 2 (0x2)
        Signature Algorithm: sha1WithRSAEncryption
        Issuer: O=YABIGrid, OU=YABI, OU=ccg.murdoch.edu.au, CN=YABI CA
        Validity
            Not Before: Jun  5 08:06:32 2009 GMT
            Not After : Jun  5 08:06:32 2010 GMT
        Subject: O=YABIGrid, OU=YABI, OU=ccg.murdoch.edu.au, OU=localdomain, CN=Crispin Wellington
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
            RSA Public Key: (1024 bit)
                Modulus (1024 bit):
                    00:ce:62:cd:63:07:04:50:31:8c:ba:a8:d9:a9:fb:
                    1e:b1:86:cf:9a:a9:67:0f:bb:41:71:73:e6:a8:68:
                    89:15:3a:26:ac:44:82:0f:b6:22:15:55:7a:cf:64:
                    4f:6b:3d:ed:30:04:1d:27:bd:0a:9e:76:d1:d5:25:
                    bf:59:e5:dd:fe:f3:38:f7:bb:e2:2f:cd:16:be:f8:
                    0c:88:74:42:e3:6e:e1:28:2b:b6:95:5c:d1:3d:df:
                    56:67:e2:09:25:8f:73:f2:90:2b:bc:d9:9f:cd:15:
                    ef:6e:a4:d7:14:0f:9a:8e:42:ad:6e:2b:5c:01:62:
                    f9:4d:4e:9f:dc:7f:8c:4d:e9
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            Netscape Cert Type: 
                SSL Client, SSL Server, S/MIME, Object Signing
    Signature Algorithm: sha1WithRSAEncryption
        08:80:6f:a5:89:e5:3f:10:cb:39:8c:57:a9:86:ca:7b:f8:a6:
        e7:c6:22:7f:c8:1b:a5:d8:61:d3:cf:62:4e:87:b5:ae:40:34:
        68:30:39:27:81:79:30:60:01:81:08:6f:e2:2f:41:41:c8:f9:
        fd:5b:b3:cc:32:47:79:5e:f1:aa:a8:46:be:83:78:d2:34:bc:
        a0:7e:17:54:a4:9c:14:48:a0:0d:24:99:cf:8b:5d:96:9a:25:
        e9:4e:3e:a0:bb:02:b9:a9:74:5e:05:cf:9f:ea:ad:6b:45:73:
        f0:98:01:24:d8:7a:81:5a:c8:a8:cd:11:18:01:77:06:25:2f:
        de:0e
-----BEGIN CERTIFICATE-----
MIICTjCCAbegAwIBAgIBAjANBgkqhkiG9w0BAQUFADBRMREwDwYDVQQKEwhZQUJJ
R3JpZDENMAsGA1UECxMEWUFCSTEbMBkGA1UECxMSY2NnLm11cmRvY2guZWR1LmF1
MRAwDgYDVQQDEwdZQUJJIENBMB4XDTA5MDYwNTA4MDYzMloXDTEwMDYwNTA4MDYz
MlowcjERMA8GA1UEChMIWUFCSUdyaWQxDTALBgNVBAsTBFlBQkkxGzAZBgNVBAsT
EmNjZy5tdXJkb2NoLmVkdS5hdTEUMBIGA1UECxMLbG9jYWxkb21haW4xGzAZBgNV
BAMTEkNyaXNwaW4gV2VsbGluZ3RvbjCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkC
gYEAzmLNYwcEUDGMuqjZqfsesYbPmqlnD7tBcXPmqGiJFTomrESCD7YiFVV6z2RP
az3tMAQdJ70KnnbR1SW/WeXd/vM497viL80WvvgMiHRC427hKCu2lVzRPd9WZ+IJ
JY9z8pArvNmfzRXvbqTXFA+ajkKtbitcAWL5TU6f3H+MTekCAwEAAaMVMBMwEQYJ
YIZIAYb4QgEBBAQDAgTwMA0GCSqGSIb3DQEBBQUAA4GBAAiAb6WJ5T8QyzmMV6mG
ynv4pufGIn/IG6XYYdPPYk6Hta5ANGgwOSeBeTBgAYEIb+IvQUHI+f1bs8wyR3le
8aqoRr6DeNI0vKB+F1SknBRIoA0kmc+LXZaaJelOPqC7ArmpdF4Fz5/qrWtFc/CY
ASTYeoFayKjNERgBdwYlL94O
-----END CERTIFICATE-----
"""
    
    key = """-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,53291E5C4BEA36B9

PkYhxG+nix812N+bwRXDC90kxgUhketu6NAiTGCB4KbLKpfzU6VyWLlMN5wQI4+8
PF0T6TNLmae8gRRIg4m9im+6tW+Oqy6dnuYHx06A2GAwD9+dCGByd+sUYibZra39
82Q/gVCBEEprY1+y0hrdoy406VDIZxH9C8mXEnvdR+UksVKP0SldqQAtYcoW1imn
UcjSwCUuyOvwTjtfOypt7tJA/QB5nX2O/+ql1yna81b2baTXczPuBePOtz32BgoH
Iimm6K+QV+O9NH9Vtwe3C8RZQtULpD5cbBuHSrmNm0eitGDk6DiTnAde+/yg0ozC
gUqPwNNCUTmY7IpBvbKIKOujB9fzJzm9NtzNPX+GbGbC8Dnj7dTGiVyFTHhfOwgo
hKrr/1BmAZymR5r80kggaF+VPhgUri03Mjhgmd+UdqpD8frC1RuttHEY0levwXL0
r5cqKWSjoYTDqusi4vhmILwRCknUtcC8/izef3AVdXa10zhCGoJjau6G5WTvYQLu
hzYeW2v77xa2cS2EgU3uP3MDzO+vXkBGX+QW1lWO4XCkvOcTJc5gzE/VB913l00F
SpEX8dkZL5TCDZGdvWShdA5lBU7Z75inTI/63wg5QHzhb+DqsnPMOwEOr40Rimcv
Sl7DVJHZuUQGVdDPPMLDrVepKvlcYnpv8hR21XiCgSni/3wee2P9NtUyt1bQD63/
cWeKETneLSvf6BriqvKkj3lfNsDD9GENqxSLrNyQ1d2H7t2omtaanprJex/yS74S
xkrEVg2k7nOFrhLdbItTFZz7kyr9mOq6KL3+o4K9L5g0usL3YqdQMQ==
-----END RSA PRIVATE KEY-----
"""
    proxy.CreateUserProxy("crispin", cert, key, "lollipop")
    
#setup_proxy(Certificates)