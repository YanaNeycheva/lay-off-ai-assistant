# E2E fixture — persona "Мартин"

The **canonical end-to-end scenario** for the smoke harness. Feed this persona and
its scripted turns to the running assistant (invoke `/comeback`, act as the
orchestrator, drive the six turns below), then validate the produced run folder
with `check_artifacts.py`. See [README.md](README.md) for the full runbook.

This is a **fixture**, not person data — it is fabricated and safe to commit.
Everything a *real* run generates (dossier, CVs, tracker, `.docx`/`.pdf`) lands
under `Personal/` and is **never** committed.

---

## Persona — Мартин Георгиев

Coherent, self-consistent facts. Used to steer triage → benefits → search → CV →
interview end to end.

- **Име:** Мартин Георгиев
- **Роля / професия:** Backend software engineer (Python / Go)
- **Ниво / опит:** Senior, ~9 години общ професионален стаж
- **Осигурителен стаж:** ~9 години непрекъснат осигурителен стаж (consistent — не
  бъркай с години на текущия работодател)
- **Стаж при последния работодател:** 3 години и 2 месеца
- **Индустрия:** SaaS / финтех
- **Локация:** София; отворен за дистанционна работа
- **Език за работа/CV:** и двете; целевата обява е на **английски**, значи CV-то е EN
- **Тип раздяла:** съкращение (масово — закрит цял отдел)
- **Дата на прекратяване:** 2026-08-14
- **Последна брутна заплата:** ~3200 лв/месец (≈ 1636 EUR)
- **Идентификация пред НАП/НОИ:** има **ПИК** (персонален идентификационен код)
- **Базово CV:** има готово базово CV (една актуална версия), нуждае се от
  ATS-чистка и таргетиране към конкретна обява
- **Емоционално състояние:** делови, но подтиснат — иска план, не утеха

### Целева обява (target JD) — за CV tailoring

> **Company:** Nordwind Labs (remote-first, EU)
> **Position:** Senior Backend Engineer (Python)
>
> We're hiring a Senior Backend Engineer to own our payments and ledger services.
> You'll design and ship high-throughput APIs in Python, own service reliability
> (SLOs, on-call), and mentor mid-level engineers.
>
> **Requirements:** 6+ years backend experience; strong Python; production
> experience with PostgreSQL and message queues (Kafka/RabbitMQ); REST/gRPC API
> design; observability (metrics, tracing); comfort with AWS. Nice to have: Go,
> fintech/payments domain, Kubernetes.

---

## Scripted persona turns

Six turns, in order. Send each as the **person's** message; let the orchestrator
respond, delegate, and write files between turns. The goal is to exercise the full
arc so a real run produces the artifacts the checker asserts.

**Turn 1 — trigger + triage**
> Съкратиха ме. Закриха целия ни отдел преди три седмици, последният ми ден беше
> 14 август. Backend инженер съм, Python и Go, около 9 години стаж. В момента съм
> по-скоро в режим "какъв е планът", отколкото в паника — просто искам да не
> изпусна нещо важно със сроковете.

**Turn 2 — benefits / deadlines (→ bg-navigator, then freshness-checker)**
> Какво трябва да направя със сроковете — бюро по труда, НОИ, обезщетение? Имам
> ПИК. Последната ми брутна заплата беше около 3200 лв, осигурителният ми стаж е
> някъде към 9 години без прекъсване.

**Turn 3 — search system (→ search-strategist: target profile + tracker)**
> Ок, това го подредих. Сега искам система за самото търсене — да не пускам
> хаотично по обяви. Дай ми план и нещо, с което да следя докъде съм с всяка
> компания. Целя senior backend роли, за предпочитане remote.

**Turn 4 — CV tailoring (→ cv-builder / /tailor-cv → .docx + .pdf)**
> Имам базово CV, но искам да го таргетирам за една конкретна обява — Senior
> Backend Engineer (Python) в Nordwind Labs (по-горе е текстът). CV-то да е на
> английски. Пусни ми готова версия за тази позиция.

**Turn 5 — interview prep (→ interview-coach: layoff story + mock)**
> Имам първи разговор с тях другата седмица. Помогни ми да разкажа защо напуснах
> предишната работа, без да звучи като оправдание, и ми дай няколко въпроса за
> репетиция.

**Turn 6 — wrap / next step**
> Стига за днес. Кажи ми само едно нещо, което да свърша до утре.

---

## What a good run leaves behind

After the six turns, the run folder `Personal/<date>-martin[-suffix]/` should hold:

- `dossier.md` — filled from the template (Profile, Layoff facts, Target, CV brief,
  Search + Tracker път, Legal / benefits, Log).
- a CV workspace (`cv/`) with a **tailored** `.docx` **and** matching `.pdf` for the
  Nordwind Labs position, plus the base CV.
- `tracker.md` — the live search tracker (momentum + zones), built by
  search-strategist.

`check_artifacts.py` asserts exactly this shape.
