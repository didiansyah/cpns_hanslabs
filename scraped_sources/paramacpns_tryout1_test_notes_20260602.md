# ParamaCPNS Tryout 1 test notes

Source: https://paramacpns.com/tryout/1

## Browser E2E
- Landing `/tryout/1` loads.
- `Mulai Simulasi` opens `/tryout/1/register/FULL`.
- Direct TWK flow `/tryout/1/register/TWK` accepts name/city input but submit fails.
- Visible error: `Terjadi kesalahan. Coba lagi.`
- Evidence screenshot: `/root/.hermes/cache/screenshots/browser_screenshot_f7955a2437974c33a3bd0812cb559010.png`

## Root cause found from network/API
The frontend calls Supabase RPC:

```txt
POST https://gksxpfbpgrqvpksktwbs.supabase.co/rest/v1/rpc/start_exam
```

Payload shape used by frontend:

```json
{
  "p_name": "Dummy Tester",
  "p_city": "Jakarta",
  "p_phone": "",
  "p_package_id": "1",
  "p_subtest": "TWK"
}
```

Supabase response when reproduced by curl/Python:

```json
{
  "code": "PGRST202",
  "message": "Could not find the function public.start_exam(p_city, p_name, p_package_id, p_phone, p_subtest) in the schema cache",
  "hint": "Perhaps you meant to call the function public.start_session"
}
```

So the public tryout start flow is currently broken by a stale/mismatched RPC name/signature.

## Scrape result
Used Supabase dummy signup/auth because anon RLS returned empty tables. Scraped question tables directly for dummy staging only.

Files:
- Raw scraped candidates: `/root/cpns/scraped_sources/paramacpns_tryout1_dummy_raw_20260602_075227.json`
- Dummy SKD 110 set: `/root/cpns/scraped_sources/paramacpns_tryout1_dummy_110_20260602_075227.json`
- Scrape validation report: `/root/cpns/scraped_sources/paramacpns_tryout1_dummy_report_20260602_075227.md`

Counts:
- Raw: 1,500 questions
- TWK: 720
- TIU: 390
- TKP: 390
- Dummy 110 selected: TWK 30, TIU 35, TKP 45

Raw structural issues found:
- bad_option_count: 38
- bad_correct_index: 2
- short_or_empty_stem: 28
- duplicate_stem: 6

Dummy 110 structural check:
- 0 issues found
- All selected questions have 5 options, correct index, explanation, and valid section.

Import note: do not insert yet. Treat these as dummy/candidate data only until answer legitimacy and source/license review are done.
