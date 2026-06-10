# ParamaCPNS Tryout 1 dummy scrape report

- Source: https://paramacpns.com/tryout/1
- Scraped at: 20260602_075227 UTC
- Auth: Supabase dummy signup used because anon RLS returns empty rows
- Raw records: 1500
- Dummy 110 candidate: 110

## Counts by section
- TWK: 720
- TIU: 390
- TKP: 390

## Counts by topic
- TIU / Figural: 30
- TIU / Numerik: 180
- TIU / Verbal: 180
- TKP / Anti Radikalisme: 30
- TKP / Jejaring Kerja: 60
- TKP / Pelayanan Publik: 90
- TKP / Profesionalisme: 120
- TKP / Sosial Budaya: 30
- TKP / Teknologi Informasi dan Komunikasi: 60
- TWK / Bahasa Negara: 90
- TWK / Bela Negara: 120
- TWK / Integritas: 150
- TWK / Nasionalisme: 240
- TWK / Pilar Negara: 120

## Validation issues
- bad_option_count: 38
- bad_correct_index: 2
- short_or_empty_stem: 28
- duplicate_stem: 6

First 30 issues:
- ('424425eb-0d7e-4586-9df7-9ddaf27b921d', 'bad_option_count', 9)
- ('67a57fc2-5b32-401e-a5ed-6a130ed65cb3', 'bad_option_count', 0)
- ('67a57fc2-5b32-401e-a5ed-6a130ed65cb3', 'bad_correct_index', None)
- ('f0378a4c-f025-4650-889e-3f578793e4e7', 'bad_option_count', 3)
- ('b4762d64-ee53-443c-a2f6-f86bff2d23e7', 'bad_option_count', 2)
- ('2606815b-64df-4625-961b-7ab238fc1fb7', 'bad_option_count', 1)
- ('8b0cb71a-3d9d-4f3c-8aec-523358e4740e', 'bad_option_count', 3)
- ('d10541da-0dc1-4c78-952e-d694fdbd5bd4', 'bad_option_count', 0)
- ('d10541da-0dc1-4c78-952e-d694fdbd5bd4', 'bad_correct_index', None)
- ('3b292c3d-7a41-4f37-afb6-2191c8eb0aa7', 'bad_option_count', 4)
- ('bfc2d181-889e-4569-a614-ab2edf6dd292', 'bad_option_count', 4)
- ('2f80a4f4-4cf4-4668-9580-ae2cf3c8b656', 'bad_option_count', 7)
- ('5fceacfc-1267-4c04-82b0-186c7a452631', 'bad_option_count', 10)
- ('354b7177-d748-48c9-9b31-d6cd062feaf6', 'bad_option_count', 8)
- ('e4dd995f-d728-406c-bb23-60d526174283', 'bad_option_count', 8)
- ('e5b8c11d-a415-4282-a6a8-0523f7078a4f', 'bad_option_count', 9)
- ('9dcd28f6-8ee2-4702-9622-e8516340380f', 'bad_option_count', 7)
- ('0928490f-9cef-47a5-a9b0-efe5e73bf30b', 'bad_option_count', 4)
- ('892f9498-952c-4d16-8d8c-a60771e2653d', 'bad_option_count', 6)
- ('b59835ae-7e94-4921-9dc3-545fb8ab58f1', 'bad_option_count', 4)
- ('d8b1c396-a2fd-46de-976a-cd7e941f8dbd', 'bad_option_count', 4)
- ('9f8abca7-3f6c-4c27-9038-5532e40a6208', 'bad_option_count', 4)
- ('1f18a7d1-1e74-4d9a-912f-67cf1846897d', 'bad_option_count', 4)
- ('c4ba0ac1-946a-4978-b86c-32199844f68d', 'bad_option_count', 4)
- ('7f7653a5-249d-4b62-81a3-00c1dbe78f34', 'bad_option_count', 2)
- ('776f844d-7cf6-45b8-aba1-505eda1c85d0', 'bad_option_count', 6)
- ('c8a0d16d-0ee9-42b5-b293-f9cb8956690d', 'bad_option_count', 4)
- ('b6af9838-f082-4893-92ab-5a7db5aefee4', 'bad_option_count', 3)
- ('5d72930f-060c-418c-8949-dc0e8b5a3d19', 'bad_option_count', 7)
- ('351cf0f7-1505-4315-9e69-45b1f2c8b135', 'bad_option_count', 6)

## Import note
Do not import yet. Review answer legitimacy and source/license first. TKP uses option_scores; TWK/TIU correct_answer is derived from max score.
