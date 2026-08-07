# Proofing pass — typography & grammar (skill-local)

Runs on the CV text **before rendering** to `.docx`/`.pdf` (and before saving any base-CV version). Detect the CV's language first (**Bulgarian or English**) and apply the matching grammar rules. **Never change facts, names, numbers, dates, employers, or titles while proofing** — if something reads wrong but might be intentional, flag it, don't "fix" it.

Produce a short **change report** grouped as: Typography · Grammar/spelling · Consistency.

---

## 1. Dashes → en-dashes (–, U+2013)

Convert to an en-dash:
- **Ranges** (numbers, dates, times): `2019-2024` → `2019–2024`, `10-15%` → `10–15%`, `Mon-Fri` → `Mon–Fri`. For month-year ranges keep the **spaced** form the ATS rules use: `March 2019 - April 2024` → `March 2019 – April 2024`.
- **Parenthetical / interruptive dash** in a sentence or bullet (a hyphen doing a dash's job): `Led the team - grew revenue 20%` → `Led the team – grew revenue 20%` (spaced en-dash). *The house choice is the en-dash, not the em-dash.*
- **Double hyphen** used as a dash: `--` → `–`.

**Do NOT convert (leave as hyphen `-`):**
- Compound modifiers: `data-driven`, `full-stack`, `cross-functional`, `part-time`, `well-known`, `24-hour`, `end-to-end`.
- Prefixes / set spellings: `co-founder`, `e-commerce`, `re-architect`, `non-technical`.
- Hyphenated surnames, phone numbers, URLs, file names, negative numbers.

Rule of thumb: **hyphen joins words; en-dash spans a range or breaks a clause.** When unsure whether a hyphen is a compound or a dash, leave it and flag it.

Also normalize: collapse double spaces, straighten spacing around the en-dash to match the rules above, ensure one consistent bullet-end punctuation (all bullets end with a period, or none — pick the document's majority and make it consistent).

---

## 2. Grammar & spelling — English CVs

- **Tense:** past roles in past tense; the current role may use present. Consistent within each role.
- **Subject–verb agreement**, article use (a/an/the), preposition choice.
- **Parallelism:** every bullet starts with a verb in the same form (all past: "Led / Built / Reduced").
- **Spelling:** one variant throughout (US *or* UK — match what's already dominant). Fix typos.
- **Punctuation & capitalization:** consistent capitalization of section headings, job titles, and technologies (e.g. `JavaScript`, not `Javascript`); no stray commas; consistent Oxford-comma choice.
- **Numbers:** consistent style (e.g. numerals for metrics: "8 people", "30%").

## 3. Grammar & spelling — Bulgarian CVs

- **Правопис** — правописни грешки, я/е, главни/малки букви.
- **Членуване** — пълен/кратък член (напр. подлог с пълен член), правилно членуване на прилагателни.
- **Съгласуване** — по род, число и лице (подлог–сказуемо, прилагателно–съществително).
- **Глаголни форми** — правилен вид/време; минали роли в минало време, последователно.
- **Пунктуация** — запетаи (подчинени изречения, обособени части), без излишни/липсващи.
- **Предлози и бройна форма** — правилен предлог; бройна форма при мъжки род (напр. „два проекта").
- **Паралелизъм** — всички bullet-и започват с еднаква форма (напр. глагол в мин. вр. или отглаголно съществително — избери едно и го спази).

> This is a **grammar** pass only — do not apply blog voice/style rules here. A CV is not a blog post.

---

## 4. Output

1. Apply all confident fixes to the text.
2. List anything ambiguous you deliberately left (with why) so the person can decide.
3. Then continue to rendering (or, for a base-CV edit, save the new version per `ats-rules.md`).
