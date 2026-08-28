# Dossier — {име на човека}

The shared case file. The orchestrator and every subagent read and write it. This is how cold-started subagents get warm context without the orchestrator re-typing the person's story. Keep it current; it is the single source of truth for the session.

> One dossier per person, at `Personal/<date>-<slug>/dossier.md` (git-ignored, not the project repo). Update the relevant section after every meaningful exchange or subagent run.

## Profile
- **Име:** {за CV/файлове}
- **Роля / професия:** {}
- **Ниво / години опит:** {}
- **Индустрия:** {}
- **Локация / дистанционно:** {}
- **Език за работа/CV:** {BG / EN / и двете}

## Layoff facts (for story + legal)
- **Тип:** {съкращение / уволнение}
- **Дата на прекратяване:** {}
- **Масово съкращение?** {да/не}
- **Стаж при работодателя:** {}
- **Последна заплата (за изчисления, ако е споделена):** {}

## Emotional read (orchestrator only writes here)
- **Състояние:** {паника / вцепенен / ядосан / делови / обезсърчен}
- **Темпо, което понася:** {}
- **Най-острата болка сега:** {}

## Target
- **Целеви роли:** {}
- **Целеви компании / тип:** {}

## CV (cv-builder writes here)
- **Workspace път:** {}
- **Базова версия:** {напр. v1.2}
- **Таргетирани позиции:** {folder → company/position}
- **Отворени gap въпроси:** {}

## Search (search-strategist writes here)
- **Профил на целта:** {}
- **Мрежа (контакти + статус):** {}
- **Tracker път:** {}
- **Следваща стъпка:** {}

## Interviews (interview-coach writes here)
- **Разказ за напускането (текуща форма):** {}
- **Практикувани въпроси + бележки:** {}
- **Топ 2–3 неща за подобрение:** {}

## Legal / benefits (bg-navigator writes here)
- **Срок за бюро по труда:** {дата}
- **Срок за НОИ:** {дата}
- **Оценка на обезщетение:** {estimate — да се потвърди в НОИ}
- **За потвърждаване:** {}

## Log
- {дата — какво се случи / кой subagent тичаше}
