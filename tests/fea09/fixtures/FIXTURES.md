# FEA-09 frozen fixtures (pre-generated, C-16 §3 / AC-1)

| file | bytes | sha256 | note |
|---|---|---|---|
| `aes_member.zip` | 218 | `437fe717fdfe74d52ba83475f9af836894101597ec23397054a251678274acc1` | WinZip AES (method 99) advertisement; payload never decryptable — typed unsupported (C-16 §3) |
| `zipcrypto_page.cbz` | 444 | `13c5b49039454d6fe6d53f6d8a97125b938d8752b8b94714685352e2b600b9dd` | ZipCrypto CBZ, password 'fea09-fixture', two 24x32 PNG members |
| `flat3_letter.pdf` | 664 | `a8eb076a2914fab903e38dc58c26bb1ca21816ee915f98ec0401d1cc0607cfd3` | unencrypted 3-page letter-size PDF (page-identity scan fixture) |
| `single_letter.pdf` | 344 | `5d34b50b50f60c4c1e42576b35fc811690a59f99f2a6afc873e0c4f1694447e6` | unencrypted single-page letter PDF (minimal container) |

Passwords exist only in these fixtures' test usage; never in product code.
Regenerate deterministically via `tests/fea09/zip_fixtures.py`.
