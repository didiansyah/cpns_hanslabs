# PrivatAlfaiz CASN access check

Source: https://casn.privatalfaiz.id/#!/login

## Result
- Login succeeded for provided account.
- `Paket Belajar Saya` / `tryout-ku` loads but no owned tryout package is visible in the page body.
- `Mulai Belajar` / `paket-tryout` lists paid tryout products and public metadata only.
- Browser console: no JS errors observed during login/navigation.

## Network/API observed
- Base API discovered from browser resources: `https://service26.tryoutsiswa.com/api/...`
- Public/product endpoints observed:
  - `/api/auth`
  - `/api/siswa/username`
  - `/api/global/paket-program-post`
  - `/api/global/paket-kelas-online-post`
  - `/api/global/tryoutku`

## Safety/import note
Do not bypass payment/purchase controls and do not scrape paid module questions unless the account has legitimate purchase/access. Current account appears to have no owned tryout package visible, so only public catalog metadata is accessible for scraping/testing.
