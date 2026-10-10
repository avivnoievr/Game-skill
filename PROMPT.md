# Activation prompts

Open Claude Code in the game repository after installing. Project copy: `/game-studio`.
Marketplace plugin: `/game-studio:game-studio`. These prompts activate the installed files; they do
not install tools or change the model selected in your client.

## משחק קיים — להדבקה

```text
טען עכשיו את game-studio (/game-studio, או /game-studio:game-studio בהתקנת פלאגין) והשתמש בו להמשך המשחק הזה.

קרא קודם את הוראות הפרויקט, progress.md ואת מפת references/design-loading.md. טען את חומר העיצוב המתאים לשלב, בלי לקרוא את כל הספרייה בכל משימה. השתמש בבלנדר שכבר מותקן; אל תתקין עותק נוסף אוטומטית.

המטרה: כיוון אמנותי מכוון ומקצועי, מודלים ניתנים לעריכה ושליטה במשחק, אנימציה טובה, תשתית נקייה ובקרת איכות אמיתית. קודם בדוק מה כבר עובד ומה חסר. אם יש משחק, הרץ אותו, צלם משחק אמיתי, בדוק את המודלים הבולטים והיעזר ב-art-critic להערכה עצמאית. כתוב audit קצר עם 3–5 השיפורים בעלי ההשפעה הגדולה ביותר וראיות לכל בעיה.

לפני ייצור חדש, כשאין תוכנית שימושית, הפעל שני סוכני פתיחה במקביל: genre-art-researcher יחקר את הז׳אנר, הטון ורפרנסים וימליץ על שפה חזותית ותנועה; production-planner ימפה מכניקות, התקדמות, תלויות ואבני דרך. ״סימולטור״ לא מחייב ריאליזם ו״מצחיק״ לא מחייב סגנון גנרי. חבר את שני הדוחות לתוכנית design/plan.md עם מקטע משחק מייצג, סדר בנייה, בעלים, תקציבים ובדיקות יציאה לפני הייצור. שמור את הממצאים והשתמש בהם שוב בסשנים הבאים.

חלק עבודה משמעותית לסוכנים עם תחום בעלות ברור: asset-builder לנכס עצמאי, animator לאנימציה, art-critic ו-playtest-qa לביקורת אבני דרך. עד שלושה במקביל, בלי שני כותבים באותו קובץ או סצנת Blender חיה. אל תפתח סוכן בשביל בירור טריוויאלי.

לכל מודל קבע מראש חלקים, pivots, joints, sockets, collision ותקציב. שמור מקור ניתן לעריכה ואל תאחד חלקים שצריכים לנוע בנפרד. אל תציג mesh מאוחד עם פרטים מצוירים כתחליף למודל שניתן לשלוט בו. אל תשתמש ביצירה בתשלום בלי הרשאה מפורשת.

התקדם עצמאית בהחלטות הפיכות שמתאימות להנחיות שלי; סמן החלטות טעם לא מוכרעות כזמניות. שאל רק כשהמידע באמת חסר ומשנה את התוצאה. בנה מקטע מייצג לפני שאתה מכפיל תוכן. בדוק את הייצוא ואת התוצאה במצלמת המשחק, פתח את התמונות ובדוק תנועה. אין PASS כשהראיות או המדדים חסרים, ואין החלשת בדיקות כדי לעבור.

דווח בקצרה מה שינית, מה בדקת בפועל, מה עדיין חלש ומה לא נבדק. תוצאה תקינה טכנית אינה הוכחה שהיא נראית טוב. עדכן progress.md ואל תבטיח איכות שלא הוכחת.
```

## Existing game — English equivalent

```text
Load game-studio now (/game-studio for a project copy, /game-studio:game-studio for the plugin) and use it to continue this game.

Read project instructions, progress.md and references/design-loading.md first. Load design material for the current phase instead of the entire library. Use installed Blender; do not automatically install another copy.

Aim for deliberate professional art direction, editable and controllable game assets, good animation, clean architecture and evidence-based QA. Audit before rebuilding: run the game, capture actual input/gameplay, inspect prominent models and ask art-critic for independent assessment. Write a short audit with the 3–5 most valuable changes and evidence for each defect.

Before production when a usable plan is missing, start genre-art-researcher and production-planner in parallel. The first researches genre/tone and visual/motion references; the second maps mechanics, progression, dependencies and milestones. A simulator need not be photorealistic, and comedy does not justify generic cartoons. Reconcile both reports into design/plan.md with one representative playable slice, ordered work, owners, budgets and exit checks before building. Reuse saved findings in later sessions.

Delegate substantial isolated work with explicit ownership: asset-builder for an asset, animator for motion, art-critic and playtest-qa for milestone reviews. At most three concurrent agents; never two writers in one file or shared live Blender scene. Do not delegate tiny lookups.

Declare parts, pivots, joints, sockets, collision and budgets before modeling. Keep editable source; do not merge independently moving pieces. Reject a fused mesh with painted-on details as a substitute for controllable geometry. No paid generation without explicit authorization.

Proceed independently on reversible choices consistent with my instructions; mark unsettled taste decisions provisional. Ask only for genuinely necessary information. Build one representative playable slice before multiplying content. Inspect the export and gameplay-camera output, open images and check motion. Missing evidence or metrics cannot pass; never weaken checks to pass them.

Report changes, actual verification, weak points and unverified work concisely. Technical validity does not prove visual quality. Keep progress.md current and do not promise quality you have not demonstrated.
```

## משחק חדש / new game

Add this brief before the existing-game prompt and replace its audit with Phase 0:

```text
Game idea / רעיון: <core loop and genre>
Engine/platform/camera / מנוע, פלטפורמה ומצלמה: <...>
Visual references / רפרנסים: <links or images>
Scope and quality level / היקף ורמת איכות: <prototype | standard | premium>
Start at Phase 0. Reuse this information and ask at most five necessary questions. Propose a small set of concrete directions before substantial visual production.
```

The specialist definitions use `model: inherit` and high effort. Select the actual available model
in Claude Code; this package does not claim an unavailable model name or force the director's effort
setting. Use maximum director effort only if your client supports it and the task warrants it.

## תוספת לבדיקת הטעם העיצובי / design-quality supplement

לבדיקת מודל או עיצוב, אפשר לצרף לפרומפט הקיים:

```text
קרא גם references/design-judgment.md. לפני בנייה משמעותית רשום בבריף הקיים החלטת עיצוב קצרה עם נימוק ורפרנס חזותי שפתחת בפועל. בדוק את הצורה במרחק השימוש לפני ליטוש. המלצות הסגנון הן נקודת התחלה שצריך להתאים לפרויקט. אני בודק כאן איכות עיצוב: השתמש בביקורת חזותית ברמת standard/premium גם למודל בודד, ודווח בנפרד על תקינות טכנית, השוואה חזותית וחולשות שנותרו. אל תציג השלמת prototype או מעבר בדיקות כהוכחה לטעם מקצועי.
```

English: Read `references/design-judgment.md`; record a concise design commitment and an actually
opened visual reference in the existing brief. Check form at intended distance before polish.
A design-quality test uses standard/premium art review even for one asset; technical evidence,
visual comparison and unresolved weaknesses are reported separately.
