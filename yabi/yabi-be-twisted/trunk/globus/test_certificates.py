##
## Test user. Valid, but has no access.
##

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



##
## Expired certificate
##

EXPIRED_CERT = """Certificate:
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

EXPIRED_KEY = """-----BEGIN RSA PRIVATE KEY-----
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

EXPIRED_KEY_PW = "lollipop"



##
## Valid certificate
##

VALID_CERT = """Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 14 (0xe)
        Signature Algorithm: sha1WithRSAEncryption
        Issuer: O=YABIGrid, OU=YABI, OU=ccg.murdoch.edu.au, CN=YABI CA
        Validity
            Not Before: Sep 21 06:28:45 2009 GMT
            Not After : Sep 21 06:28:45 2010 GMT
        Subject: O=YABIGrid, OU=YABI, OU=ccg.murdoch.edu.au, OU=localdomain, CN=Crispin Wellington
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
            RSA Public Key: (1024 bit)
                Modulus (1024 bit):
                    00:bf:a8:41:f1:fd:4c:3f:b1:98:84:48:21:b4:0a:
                    3e:51:c7:f2:63:c2:1c:ed:76:45:fa:22:aa:f9:95:
                    8d:2f:57:86:a6:76:f6:55:9c:de:61:d4:cf:c0:57:
                    09:36:6f:75:29:9c:84:0c:74:de:4d:29:8f:ca:84:
                    ae:bf:2a:7b:da:5a:73:4a:57:7f:42:7d:58:da:5c:
                    f5:24:af:02:22:60:87:cb:72:3e:6e:4c:49:d5:07:
                    1a:be:fe:79:c2:e4:58:7f:c2:53:1f:e6:77:a5:ba:
                    c4:2e:f2:11:26:20:ec:09:4e:22:6c:0d:de:0b:07:
                    a9:2e:15:bf:57:91:26:60:b3
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            Netscape Cert Type: 
                SSL Client, SSL Server, S/MIME, Object Signing
    Signature Algorithm: sha1WithRSAEncryption
        18:4f:44:d0:9a:a7:68:15:a6:7c:6e:fd:29:4d:1b:56:b0:df:
        91:a5:97:6f:2b:f8:77:f5:6d:9f:c0:cd:8f:a8:7c:9f:0f:e9:
        09:4f:04:dc:a9:d9:a8:c6:bf:0a:11:ce:c2:64:21:82:46:78:
        e7:3b:f7:bd:04:71:a3:05:0a:fb:8c:b2:4b:8a:27:9e:90:9e:
        87:59:1f:e9:dc:80:fb:ef:ca:9e:9e:ba:fa:83:93:5e:35:31:
        57:f3:a7:18:6b:51:55:e3:93:5d:fb:c5:c3:3a:5e:ea:2a:fb:
        17:71:e3:55:86:12:b1:03:a7:5c:cf:2c:87:9a:1a:fe:8b:7e:
        f8:29
-----BEGIN CERTIFICATE-----
MIICTjCCAbegAwIBAgIBDjANBgkqhkiG9w0BAQUFADBRMREwDwYDVQQKEwhZQUJJ
R3JpZDENMAsGA1UECxMEWUFCSTEbMBkGA1UECxMSY2NnLm11cmRvY2guZWR1LmF1
MRAwDgYDVQQDEwdZQUJJIENBMB4XDTA5MDkyMTA2Mjg0NVoXDTEwMDkyMTA2Mjg0
NVowcjERMA8GA1UEChMIWUFCSUdyaWQxDTALBgNVBAsTBFlBQkkxGzAZBgNVBAsT
EmNjZy5tdXJkb2NoLmVkdS5hdTEUMBIGA1UECxMLbG9jYWxkb21haW4xGzAZBgNV
BAMTEkNyaXNwaW4gV2VsbGluZ3RvbjCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkC
gYEAv6hB8f1MP7GYhEghtAo+UcfyY8Ic7XZF+iKq+ZWNL1eGpnb2VZzeYdTPwFcJ
Nm91KZyEDHTeTSmPyoSuvyp72lpzSld/Qn1Y2lz1JK8CImCHy3I+bkxJ1Qcavv55
wuRYf8JTH+Z3pbrELvIRJiDsCU4ibA3eCwepLhW/V5EmYLMCAwEAAaMVMBMwEQYJ
YIZIAYb4QgEBBAQDAgTwMA0GCSqGSIb3DQEBBQUAA4GBABhPRNCap2gVpnxu/SlN
G1aw35Gll28r+Hf1bZ/AzY+ofJ8P6QlPBNyp2ajGvwoRzsJkIYJGeOc7970EcaMF
CvuMskuKJ56QnodZH+ncgPvvyp6euvqDk141MVfzpxhrUVXjk137xcM6Xuoq+xdx
41WGErEDp1zPLIeaGv6Lfvgp
-----END CERTIFICATE-----
"""

VALID_KEY = """-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,7022400C77F5AA78

615s7E1NmKFXlB5xnPVzOSK180b5SQAx+opS3hE0YBapnttrWa36k3unnwCiXX/y
RtfsrKMv/9ufH0SZ4J8gtbh49+FDGZMLIs3GdaflXcBeocoh802OTyHvWgrqmO3J
lu4jBaDIsQmdvY5uaJk177k7Tzht3kiwTCCr2fBB1D2GAHj1nl0TrYrK3avt5gN/
hbWoC4CdM4xwaHDnM7cWlufjqbO/RtEKtkihIFO1dveR4DLo9fZVQ6Q1mu8c4DYP
qTQ0sKa3IS+B/RD7IT7D12ysCWJ0O/FOiU8gK0rzzMSNmb/N8ylt4w0k3j75J2dg
nRExCQ9m2Ow761tn3yhCidhMqrfpcIpskRH2OnHrTj4AIsuH6JiRDVwSzaPSnhdL
ynIhUh3fJc7qR8uglR6DraG/zXO9bDuWM9Uq/jNP0IPI5nt2aDkfQfcqKrB/SvM9
HN6D2mmukWAy4w5zD8RlLvtMtScbcs0/pORy8GDFvNM0psSEBBDYkEuzaDB7Kt//
G1URo//BS6M4t/ImBoSbYEorE0FH9aBVaxWRkOo1yVcpz2mBQb/lNSW7MCeDBBKv
dZqQsHI8vfy0kEtrhoY9KRfMbdW6Lenyabnp3BQLrDlMs0X9AmgdDKEnpj7hOgh6
+h5dfwlpKJeDdJxBnNE6C1GKoaSQoaI/ixjCgctb/vGS1UxZHT8y9AsUigtpdIo2
kDR9oqJ3o/Drowt9Hgl0A/sygDChQY4lz5Njnn+OKeaVAinewM1/j4DI4seUqlfC
0kGiIRttzq0yCQRe3EHvvSdJRNy5yLMrVY9Z1gDUTIbROEIG4lzJyQ==
-----END RSA PRIVATE KEY-----
"""

VALID_KEY_PW = "lollipop"
