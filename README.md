# WEMASA Tanzania Organization — Website & Dashboard

Tovuti rasmi ya **WEMASA (Weka Mazingira Safi)** pamoja na dashboard ya kusimamia maudhui yote.

- **Backend:** Django 5.2 (LTS)
- **Database:** Supabase Postgres
- **Picha na nyaraka:** Supabase Storage (bucket, S3-compatible)
- **Lugha ya tovuti:** Kiingereza

## Kilichomo

### Tovuti ya umma (kurasa 19)
Home · About · Focus areas (+ ukurasa wa kila eneo) · Projects (+ ukurasa wa kila project na gallery yake) ·
Impact · SDGs · News & stories · In the media · Reports & documents · Gallery · Team · Partners ·
Get involved · Donate · Contact · Search · 404

- Design ya kisasa: cards, animations nyepesi, inafaa kwenye simu na kompyuta.
- **Kasi:** kila ukurasa unahifadhiwa kwenye cache (≈2ms kwa ombi linalofuata). Picha zinabadilishwa kuwa
  WebP na kupunguzwa ukubwa zinapopakiwa. Hakuna jQuery wala Bootstrap.
- SEO: meta tags, Open Graph (WhatsApp/Facebook previews), `sitemap.xml`, `robots.txt`, schema.org.
- Fomu ya mawasiliano (inahifadhi ujumbe kwenye dashboard na kutuma email), newsletter, kitufe cha WhatsApp,
  lightbox ya picha, search.

### Dashboard (`/dashboard/`)
Kila kitu kinabadilika bila kugusa code:
maandishi ya kila ukurasa, picha za juu (banners), takwimu za impact, projects na figures zake, photo gallery
(upload ya picha nyingi kwa mara moja), team, partners, core values, objectives, timeline, SDGs, news (rich text
editor), media coverage, reports (PDF), njia za kuchangia (bank / mobile money), FAQs, mawasiliano na social media.
Pia inaonyesha ujumbe kutoka fomu ya Contact na orodha ya subscribers (export CSV).

Mabadiliko yakihifadhiwa, cache inafutwa papo hapo — tovuti inaonyesha maudhui mapya mara moja.

## Kuendesha kwenye kompyuta (local)

```bash
cp .env.example .env            # DEBUG=True, bila DATABASE_URL → SQLite
pip install -r requirements.txt
python manage.py migrate
python manage.py createcachetable
python manage.py seed_content   # maudhui ya awali + picha
python manage.py createsuperuser
python manage.py runserver
```
Fungua http://127.0.0.1:8000 na dashboard http://127.0.0.1:8000/dashboard/

Tests: `python manage.py test`

## Kuweka mtandaoni (Supabase + Render)

### 1. Supabase
1. Unda project mpya kwenye https://supabase.com (region karibu na Afrika Mashariki, mfano *Frankfurt / eu-central-1*).
2. **Database:** Project Settings → Database → *Connection string* → **Session pooler** → nakili URI
   (weka password yako). Hii ndiyo `DATABASE_URL`.
3. **Storage:** Storage → *New bucket* → jina `wemasa-media` → chagua **Public bucket**.
4. **S3 keys:** Storage → Settings → *S3 Connection* → *New access key*. Nakili:
   `SUPABASE_S3_KEY`, `SUPABASE_S3_SECRET`, na `SUPABASE_REGION`.
   `SUPABASE_PROJECT_REF` ni sehemu ya kwanza ya URL ya project (`https://<project-ref>.supabase.co`).

### 2. Render
1. https://dashboard.render.com → **New → Blueprint** → chagua repo hii.
2. Jaza thamani zinazoulizwa (`DATABASE_URL`, `SUPABASE_*`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, domain).
3. **Apply.** `build.sh` itasakinisha, ita-`migrate`, itaunda admin wa kwanza na kuingiza maudhui ya awali.

> `render.yaml` inatumia plan ya **Free**. Plan ya bure hulala baada ya dakika 15 bila wageni, kwa hiyo weka
> **UptimeRobot** iiamshe kila wakati (hatua 2a hapa chini).

### 2a. UptimeRobot (kuzuia tovuti isilale)
1. Fungua akaunti ya bure kwenye https://uptimerobot.com → **Add New Monitor**.
2. Monitor type: **HTTP(s)**.
3. URL: `https://<jina-la-service>.onrender.com/health/` (au domain yako, mfano `https://wemasa.or.tz/health/`).
4. Monitoring interval: **5 minutes** → Create Monitor.

`/health/` ni ukurasa mwepesi sana unaojibu `ok` (na kukagua database), hivyo hautumii rasilimali nyingi.
UptimeRobot pia itakutumia email tovuti ikishindwa kufunguka.

> Plan ya bure ya Render inatoa takriban saa 750 kwa mwezi — zinatosha service moja iwe hewani muda wote.

### 3. Domain
Render → Settings → Custom Domains → ongeza domain (mfano `wemasa.or.tz`), weka DNS records, kisha ongeza domain
hiyo kwenye `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` na `SITE_URL`.

### 4. Email (hiari)
Weka `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (mfano Gmail SMTP na *App password*) na
`CONTACT_NOTIFY_EMAILS` ili kila ujumbe wa fomu ya Contact utumwe kwa email.

## Muundo wa code

```
config/      settings, urls
website/     models (maudhui yote), views za tovuti, cache, seed_content
dashboard/   dashboard ya admin (registry.py inaeleza kila sehemu inayoharirika)
templates/   website/, dashboard/, partials/
static/      css/site.css, js/site.js, css/dashboard.css, img/
seed/images/ picha za awali zinazoingizwa na seed_content
```
