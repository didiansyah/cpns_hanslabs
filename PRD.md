# PRD: CPNS 2026 Learning Platform

## Overview
Platform belajar CPNS 2026 GRATIS untuk semua calon peserta. Akses penuh dengan registrasi + OTP verifikasi. Platform ini membantu tracking progress belajar, simulasi soal adaptif, analisis kekuatan/kelemahan, dan jadwal belajar terstruktur dengan AI-powered recommendations.

## Problem Statement
Persiapan CPNS membutuhkan konsistensi dan strategi yang terstruktur. Banyak calon peserta:
- Tidak tahu harus mulai dari mana
- Tidak punya tracking progress yang baik
- Sulit mengetahui topik mana yang masih lemah
- Tidak punya simulasi CAT yang realistis
- Bimbel CPNS mahal (500rb-2jt)
- Tidak ada feedback personalisasi

## Target User
- Calon peserta CPNS 2026 di seluruh Indonesia
- Akses gratis, tidak perlu bimbel
- Belajar mandiri dengan panduan terstruktur
- Target: 10,000+ user di 6 bulan pertama

## Value Proposition
- ✅ **100% GRATIS** — tidak ada biaya apapun
- ✅ Registrasi mudah dengan OTP via email/WhatsApp
- ✅ Dashboard lengkap: progress tracker, simulasi, analisis
- ✅ AI-powered adaptive learning
- ✅ Jadwal belajar terstruktur 12 minggu
- ✅ Bank soal TWK, TIU, TKP dengan pembahasan
- ✅ Tren soal 2020-2025 + prediksi 2026
- ✅ Mobile responsive + PWA (installable)
- ✅ Dark mode support

## Monetization
- **TIDAK ADA biaya** — platform gratis
- **Donasi sukarela** — tombol donate di header
- Dana donasi untuk: server, domain, maintenance
- Transparansi: laporan penggunaan donasi

---

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod validation
- **PWA**: next-pwa (installable di mobile)
- **Dark Mode**: next-themes

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 + Alembic (migrations)
- **Auth**: JWT + OTP (email/WhatsApp)
- **Task Queue**: Celery + Redis (async OTP sending)
- **Caching**: Redis
- **API Docs**: Swagger UI (auto-generated)

### Database
- **Primary**: PostgreSQL 15
- **Cache**: Redis 7
- **File Storage**: Supabase Storage / MinIO (untuk QRIS image, dll)

### AI/ML
- **Adaptive Learning**: Custom algorithm (spaced repetition + difficulty adjustment)
- **Question Generation**: OpenAI API (optional, untuk generate soal baru)
- **Analytics**: Python pandas + scikit-learn (user behavior analysis)

### Infrastructure
- **Hosting**: VPS (existing Hans Labs VPS)
- **Reverse Proxy**: Nginx
- **SSL**: Cloudflare
- **CI/CD**: GitHub Actions
- **Monitoring**: Uptime Kuma + Sentry
- **Email**: Resend API
- **WhatsApp**: WhatsApp Business API (optional)

### Development Tools
- **Package Manager**: pnpm (frontend), pip (backend)
- **Linting**: ESLint + Prettier (frontend), Ruff (backend)
- **Testing**: Vitest (frontend), pytest (backend)
- **API Testing**: httpx + pytest-asyncio

---

## Features

### Fase 1 (MVP) — Minggu 1-4
- [ ] Landing page dengan info CPNS 2026
- [ ] Registrasi + OTP verifikasi (email)
- [ ] Login dengan OTP (passwordless)
- [ ] Dashboard progress tracker
- [ ] Jadwal belajar 12 minggu
- [ ] Checklist harian (persist di DB)
- [ ] Log simulasi CAT
- [ ] Contoh soal + pembahasan (TWK, TIU, TKP)
- [ ] Tren soal 2020-2025
- [ ] Passing grade reference
- [ ] Resource links
- [ ] Donate button (QRIS + transfer)
- [ ] Dark mode
- [ ] Mobile responsive

### Fase 2 — Minggu 5-8
- [ ] Bank soal interaktif (100+ soal per seksi)
- [ ] Timer simulasi sesuai ujian asli (90 menit)
- [ ] Scoring otomatis + analisis detail
- [ ] Weekly progress charts (Recharts)
- [ ] Leaderboard (anonym) — motivasi kompetitif
- [ ] Export progress ke PDF
- [ ] Push notification reminder belajar
- [ ] PWA support (installable di HP)

### Fase 3 — Minggu 9-12
- [ ] AI-powered adaptive learning
  - Adjust difficulty berdasarkan performa
  - Rekomendasi topik yang perlu dipelajari
  - Prediksi skor ujian berdasarkan progress
- [ ] Spaced repetition untuk TWK facts
- [ ] Forum diskusi antar peserta
- [ ] Video pembahasan soal (YouTube embed)
- [ ] Mock test full simulation (CAT-like)
- [ ] Admin dashboard (monitor users, analytics)

### Fase 4 (Nice to Have)
- [ ] Mobile app (React Native / Expo)
- [ ] WhatsApp bot untuk reminder
- [ ] AI chatbot untuk tanya jawab
- [ ] Sistem reward / badge / streak
- [ ] Study groups (join group belajar)
- [ ] Content management system (tambah soal via admin)
- [ ] Multi-bahasa (Indonesian primary)
- [ ] Integrasi dengan SSCASN (jika API tersedia)

---

## User Flow

### 1. Landing Page
```
Hero Section
├── "Belajar CPNS 2026 GRATIS"
├── Subtitle: "Platform #1 untuk persiapan CPNS"
├── CTA: "Daftar Sekarang" (primary)
├── CTA: "Login" (secondary)
└── Donate button di header (❤️)

Features Section
├── 100% Gratis
├── Registrasi Mudah (OTP)
├── Dashboard Lengkap
├── AI-Powered Learning
├── Simulasi CAT Realistis
└── Tren Soal 2020-2025

Stats Section
├── 10,000+ Soal
├── 500+ Pengguna
├── 95% Tingkat Kelulusan
└── 24/7 Akses

Testimonials
└── (placeholder untuk user reviews)

Footer
├── Links
├── Social Media
└── Donate CTA
```

### 2. Registrasi Flow
```
Step 1: Input Data
├── Nama Lengkap
├── Email (valid format)
├── No. WhatsApp (optional)
└── Target Formasi (dropdown)

Step 2: Verifikasi OTP
├── Kirim OTP ke email
├── Input 6-digit OTP
├── Resend OTP (max 3x, cooldown 60 detik)
└── Verifikasi → JWT token

Step 3: Profil Singkat
├── Pendidikan terakhir
├── Target instansi
└── Pengalaman CPNS sebelumnya (ya/tidak)

→ Redirect ke Dashboard
```

### 3. Dashboard Flow
```
Dashboard
├── Header
│   ├── Countdown ujian SKD
│   ├── Donate button
│   └── User profile / logout
│
├── Stats Overview
│   ├── Hari belajar
│   ├── Total jam
│   ├── Simulasi selesai
│   └── Rata-rata skor
│
├── Progress Section
│   ├── Progress bar per seksi (TWK, TIU, TKP)
│   ├── Target vs actual score
│   └── Weekly trend chart
│
├── Today's Checklist
│   ├── TWK: Baca materi 30-60 menit
│   ├── TIU: Latihan soal 15-20 soal
│   ├── TKP: Review skenario 10 soal
│   ├── Review kesalahan kemarin
│   └── Update progress tracker
│
├── Jadwal Mingguan
│   ├── Tab: Minggu 1-12
│   └── Table: Hari | Pagi | Siang | Malam
│
├── Simulasi CAT
│   ├── Mulai simulasi baru
│   ├── Timer 90 menit
│   ├── Soal per seksi
│   └── Hasil + analisis
│
├── Bank Soal
│   ├── Filter: TWK / TIU / TKP
│   ├── Filter: Topik
│   ├── Filter: Tahun (2020-2025)
│   └── Latihan per topik
│
├── Contoh Soal + Pembahasan
│   ├── Tab: TWK / TIU / TKP
│   └── Soal + opsi + penjelasan
│
├── Tren Soal 2020-2025
│   ├── Perbandingan per tahun
│   ├── Grafik tren kesulitan
│   └── Prediksi 2026
│
└── Resources
    ├── Website & Apps
    ├── YouTube Channels
    ├── Buku Rekomendasi
    └── Tips dari yang lulus
```

### 4. Simulasi CAT Flow
```
Mulai Simulasi
├── Pilih jenis: Full / Per Seksi
├── Konfirmasi → Timer mulai
│
├── TWK (30 soal, 35 menit)
│   ├── Soal 1-30
│   ├── Navigation: prev/next
│   └── Flag soal untuk review
│
├── TIU (35 soal, 30 menit)
│   ├── Soal 1-35
│   └── Auto-submit saat waktu habis
│
├── TKP (45 soal, 25 menit)
│   ├── Soal 1-45
│   └── Skor 1-5 per opsi
│
└── Hasil
    ├── Skor per seksi
    ├── Status: PASS / FAIL
    ├── Analisis kekuatan/kelemahan
    ├── Topik yang perlu diperbaiki
    └── Rekomendasi belajar
```

### 5. Donate Flow
```
Klik Donate Button
├── Modal pop-up
│   ├── QRIS QR Code
│   ├── Transfer bank (BCA/Mandiri)
│   ├── Amount suggestion (10k/25k/50k/100k)
│   └── Custom amount
│
└── Terima kasih
    ├── "Donasi Anda sangat berarti"
    └── Link ke halaman transparansi donasi
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    education VARCHAR(50),  -- SMA/D3/S1/S2
    target_instansi VARCHAR(100),
    previous_cpns BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### OTPs Table
```sql
CREATE TABLE otps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(6) NOT NULL,
    type VARCHAR(10) NOT NULL,  -- 'email' or 'whatsapp'
    expires_at TIMESTAMP NOT NULL,
    attempts INT DEFAULT 0,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Progress Table
```sql
CREATE TABLE progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    study_days INT DEFAULT 0,
    study_hours DECIMAL(10,2) DEFAULT 0,
    sim_count INT DEFAULT 0,
    current_week INT DEFAULT 1,
    twk_score DECIMAL(5,2) DEFAULT 0,
    tiu_score DECIMAL(5,2) DEFAULT 0,
    tkp_score DECIMAL(5,2) DEFAULT 0,
    streak_days INT DEFAULT 0,
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Simulations Table
```sql
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,  -- 'full', 'twk', 'tiu', 'tkp'
    twk_score INT,
    tiu_score INT,
    tkp_score INT,
    total_score INT,
    passed BOOLEAN,
    duration_seconds INT,
    questions_data JSONB,  -- simpan jawaban user
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Questions Table
```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section VARCHAR(3) NOT NULL,  -- 'TWK', 'TIU', 'TKP'
    topic VARCHAR(100) NOT NULL,
    year INT,  -- tahun soal (2020-2025)
    difficulty VARCHAR(20),  -- 'easy', 'medium', 'hard'
    question_text TEXT NOT NULL,
    options JSONB NOT NULL,  -- [{text, score}]
    correct_answer INT,  -- index jawaban benar (TIU/TWK)
    explanation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Checklists Table
```sql
CREATE TABLE checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    chk1 BOOLEAN DEFAULT FALSE,
    chk2 BOOLEAN DEFAULT FALSE,
    chk3 BOOLEAN DEFAULT FALSE,
    chk4 BOOLEAN DEFAULT FALSE,
    chk5 BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, date)
);
```

### Leaderboard Table
```sql
CREATE TABLE leaderboard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(50) NOT NULL,  -- anonymized
    total_score INT DEFAULT 0,
    sim_count INT DEFAULT 0,
    study_days INT DEFAULT 0,
    rank INT,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Donations Table
```sql
CREATE TABLE donations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(20),  -- 'qris', 'bank_transfer', 'ewallet'
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'completed', 'failed'
    reference_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints (FastAPI)

### Auth
```
POST   /api/auth/register        - Register user
POST   /api/auth/send-otp        - Send OTP to email/WhatsApp
POST   /api/auth/verify-otp      - Verify OTP & get JWT
POST   /api/auth/refresh          - Refresh JWT token
POST   /api/auth/logout           - Invalidate token
```

### Users
```
GET    /api/users/me              - Get current user profile
PUT    /api/users/me              - Update profile
GET    /api/users/me/progress     - Get user progress
GET    /api/users/me/stats        - Get user statistics
```

### Progress
```
GET    /api/progress              - Get progress data
PUT    /api/progress              - Update progress
POST   /api/progress/study-log    - Log study session
GET    /api/progress/charts       - Get chart data
```

### Simulations
```
POST   /api/simulations           - Start new simulation
GET    /api/simulations           - Get simulation history
GET    /api/simulations/{id}      - Get simulation detail
POST   /api/simulations/{id}/submit - Submit answers
```

### Questions
```
GET    /api/questions             - Get questions (filter by section, topic, year)
GET    /api/questions/random      - Get random questions for practice
GET    /api/questions/{id}        - Get question detail
POST   /api/questions/check       - Check answer
```

### Checklists
```
GET    /api/checklists/today      - Get today's checklist
PUT    /api/checklists/today      - Update checklist
GET    /api/checklists/history    - Get checklist history
```

### Leaderboard
```
GET    /api/leaderboard           - Get leaderboard (top 100)
GET    /api/leaderboard/me        - Get user's rank
```

### Donations
```
POST   /api/donations             - Create donation record
GET    /api/donations             - Get donation history
GET    /api/donations/stats       - Get donation statistics
```

### AI/ML (Phase 3)
```
POST   /api/ai/adaptive-quiz      - Get adaptive quiz based on performance
GET    /api/ai/recommendations    - Get study recommendations
GET    /api/ai/predict-score      - Predict exam score
POST   /api/ai/spaced-repetition  - Get spaced repetition schedule
```

---

## Passing Grade Reference
| Seksi | Jumlah Soal | Waktu | Passing Grade |
|-------|-------------|-------|---------------|
| TWK | 30 | 35 menit | ≥ 65 |
| TIU | 35 | 30 menit | ≥ 80 |
| TKP | 45 | 25 menit | ≥ 143 |

## Exam Structure
- **SKD (Seleksi Kompetensi Dasar)**: TWK + TIU + TKP
- **SKB (Seleksi Kompetensi Bidang)**: Tergantung instansi
- **Final score**: SKD 40% + SKB 60%
- **Format**: CAT (Computer Assisted Test)

## Study Schedule (12 Minggu)
- Minggu 1-4: Fondasi (TWK + TIU + intro TKP)
- Minggu 5-8: Intensif (fokus area lemah + speed drill)
- Minggu 9-12: Pemantapan (simulasi CAT 4x/minggu)

## Resources
- **Simulasi CAT**: catpns.com
- **Info resmi**: sscasn.bkn.go.id
- **YouTube**: "CPNS TETAP BELAJAR", "Ambis CPNS"
- **Apps**: CPNS Pro, Cat CPNS

---

## Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Registrasi | 10,000 user | 6 bulan pertama |
| Retention rate | 60% | User aktif mingguan |
| Simulasi completion | 80% | User ikut simulasi |
| Study streak | 30% | User belajar 7+ hari berturut |
| Donasi | Rp 5 juta | 6 bulan pertama |
| User satisfaction | 4.5/5 | Rating & feedback |
| Passing rate | 70% | User yang lolos CPNS |

---

## Risks & Mitigation
| Risiko | Impact | Mitigasi |
|--------|--------|----------|
| Server down (traffic tinggi) | High | CDN + auto-scaling + monitoring |
| Spam registrasi | Medium | Rate limiting + CAPTCHA + OTP |
| Donasi tidak cukup | Medium | Sponsor / partnership / grant |
| Konten tidak akurat | High | Review oleh CPNS alumni + update berkala |
| OTP gagal kirim | Medium | Fallback ke WhatsApp + retry |
| Data breach | High | Encryption + rate limiting + audit |
| Bot abuse | Medium | CAPTCHA + behavior analysis |

---

## Development Timeline

### Phase 1: MVP (Minggu 1-4)
**Week 1: Setup & Auth**
- [ ] Setup Next.js project (frontend)
- [ ] Setup FastAPI project (backend)
- [ ] Setup PostgreSQL + Redis
- [ ] Implement auth (register + OTP + JWT)
- [ ] Setup CI/CD pipeline

**Week 2: Dashboard Core**
- [ ] Build landing page (Midday.ai style)
- [ ] Build dashboard layout
- [ ] Implement progress tracker
- [ ] Implement checklist
- [ ] Implement countdown timer

**Week 3: Content & Soal**
- [ ] Build bank soal structure
- [ ] Implement contoh soal + pembahasan
- [ ] Implement tren soal 2020-2025
- [ ] Build jadwal belajar section
- [ ] Implement resource links

**Week 4: Polish & Deploy**
- [ ] Implement dark mode
- [ ] Mobile responsive optimization
- [ ] Donate button + modal
- [ ] Testing + bug fixes
- [ ] Deploy to VPS

### Phase 2: Enhanced (Minggu 5-8)
**Week 5-6: Simulasi CAT**
- [ ] Build simulasi CAT engine
- [ ] Implement timer + auto-submit
- [ ] Build scoring system
- [ ] Implement hasil + analisis

**Week 7-8: Social & Analytics**
- [ ] Build leaderboard
- [ ] Implement progress charts
- [ ] Build export PDF
- [ ] Implement push notifications

### Phase 3: AI & Community (Minggu 9-12)
**Week 9-10: AI Features**
- [ ] Implement adaptive learning algorithm
- [ ] Build spaced repetition system
- [ ] Implement AI recommendations
- [ ] Build score prediction

**Week 11-12: Community**
- [ ] Build forum diskusi
- [ ] Implement study groups
- [ ] Build admin dashboard
- [ ] Final testing + optimization

---

## Notes
- Platform ini GRATIS, tidak ada paywall
- Donasi sukarela dengan transparansi penuh
- Fokus pada UX yang baik dan konten berkualitas
- Mobile-first design (banyak akses dari HP)
- Bahasa Indonesia 100%
- Dark mode support
- PWA support (installable di HP)
- AI-powered adaptive learning (Phase 3)
- Scalable architecture untuk 10,000+ users
