# Activation prompts

Paste one of these as the first message of a new Claude Code session opened in your game project, after
installing (see README.md). The English and Hebrew versions say the same thing, so use whichever you
prefer.

With the plugin installed, the skill is `/game-studio:game-studio`. With the project or user copy
(`install.sh`), it is `/game-studio`.

---

## A. Existing game (start here if you already have a game in progress)

```text
Use the game-studio skill for all work on this game. Load it first (/game-studio, or /game-studio:game-studio with the plugin), read its SKILL.md completely, and treat it as this project's standard.

Context: I'm building a 3D game with you. So far the visuals look amateur and AI-generated, and the 3D models are poor. I need intentional, professional art direction, game-ready models, good animation, a clean codebase, and strict quality control. Mediocre results count as failure on this project. I would rather hear an honest "this isn't good yet" than a claim that it's fine.

Start with the existing-project audit from the skill:
1. Read progress.md and CLAUDE.md if they exist, identify the engine and version, and get the game running.
2. Capture real gameplay evidence (screenshots, metrics, errors) and run the skill's inspect/render scripts on the 5 most visible models.
3. Have the art-critic agent score the current state independently against the scorecard.
4. Write design/audit.md: the top problems ranked by player impact, each with evidence, plus what is worth keeping.
5. Then stop and show me: the 3–5 changes that would improve the game most, 2–3 art directions to choose from (with palettes), and your plan, including which agents you will use for what. Ask me only questions whose answers change the result.

Rules for the whole project: no claim without evidence from this session; look at every visual change before calling it done; independent critics judge milestones; one feature at a time, with progress.md kept current; never weaken a test, threshold or requirement to make something pass. Use subagents where the skill says they pay off (asset-builder in parallel for assets, animator for rigs and clips, art-critic and playtest-qa at gates), not for trivial work.
```

## B. New game

```text
Use the game-studio skill for all work on this game. Load it first (/game-studio, or /game-studio:game-studio with the plugin), read its SKILL.md completely, and treat it as this project's standard.

I want to build a new 3D game: <one paragraph: the idea, genre and camera, engine (three.js / Godot / Unity), target platform, references you like>.

Start at Phase 0: ask me at most 5 questions, write design/brief.md, then propose 2–3 art directions with palettes for me to choose from. After I choose, run pre-production as the skill describes (art bible, architecture with QA mode and verify script, features/budgets/assets files) before building any content.

Quality bar: a shipped indie game in this genre. Mediocre results count as failure. No claim without evidence from this session, look at every visual change, independent critics at milestones, honest reporting of limits.
```

---

## א. משחק קיים (מתחילים כאן אם כבר יש לך משחק בעבודה)

```text
השתמש בסקיל game-studio לכל העבודה על המשחק הזה. טען אותו קודם (/game-studio, או /game-studio:game-studio אם הותקן כפלאגין), קרא את ה-SKILL.md שלו במלואו, והתייחס אליו כסטנדרט של הפרויקט.

הקשר: אני בונה איתך משחק תלת-ממדי. עד עכשיו העיצוב נראה חובבני ו"עשוי ב-AI", והמודלים התלת-ממדיים חלשים. אני צריך כיוון אמנותי מקצועי ומכוון, מודלים מוכנים למשחק, אנימציה איכותית, קוד נקי ובקרת איכות קפדנית. תוצאה בינונית נחשבת כישלון בפרויקט הזה. אני מעדיף לשמוע "זה עוד לא טוב" בכנות מאשר טענה שהכול בסדר.

התחל בבדיקת הפרויקט הקיים לפי הסקיל:
1. קרא את progress.md ו-CLAUDE.md אם קיימים, זהה את המנוע והגרסה, והרץ את המשחק.
2. אסוף ראיות אמיתיות ממשחק (צילומי מסך, מדדים, שגיאות) והרץ את סקריפטי הבדיקה והרינדור של הסקיל על 5 המודלים הבולטים ביותר.
3. בקש מסוכן art-critic לדרג את המצב הנוכחי באופן עצמאי מול כרטיס הניקוד (scorecard).
4. כתוב design/audit.md: הבעיות המרכזיות מדורגות לפי ההשפעה על השחקן, כל אחת עם ראיה, ומה שכדאי לשמור.
5. אחר כך עצור והראה לי: 3–5 השינויים שישפרו את המשחק הכי הרבה, 2–3 כיוונים אמנותיים לבחירה (עם פלטות צבע), והתוכנית שלך, כולל איזה סוכן יעשה מה. שאל אותי רק שאלות שהתשובה עליהן משנה את התוצאה.

כללים לכל הפרויקט: אין טענה בלי ראיה מהסשן הנוכחי; מסתכלים על כל שינוי ויזואלי לפני שקוראים לו "גמור"; מבקרים עצמאיים שופטים כל אבן דרך; פיצ'ר אחד בכל פעם, ו-progress.md מעודכן; אסור להחליש בדיקה, סף או דרישה כדי שמשהו יעבור. השתמש בסוכני-משנה איפה שהסקיל אומר שהם משתלמים (asset-builder במקביל למודלים, animator לשלדים ואנימציות, art-critic ו-playtest-qa בשערי האיכות), לא לעבודה טריוויאלית.
```

## ב. משחק חדש

```text
השתמש בסקיל game-studio לכל העבודה על המשחק הזה. טען אותו קודם (/game-studio, או /game-studio:game-studio אם הותקן כפלאגין), קרא את ה-SKILL.md שלו במלואו, והתייחס אליו כסטנדרט של הפרויקט.

אני רוצה לבנות משחק תלת-ממדי חדש: <פסקה אחת: הרעיון, הז'אנר והמצלמה, המנוע (three.js / Godot / Unity), הפלטפורמה, משחקים שאתה אוהב כרפרנס>.

התחל בשלב 0: שאל אותי עד 5 שאלות, כתוב design/brief.md, ואז הצע 2–3 כיוונים אמנותיים עם פלטות צבע לבחירה. אחרי שאבחר, בצע את שלב הקדם-הפקה כפי שהסקיל מתאר (art bible, ארכיטקטורה עם מצב QA וסקריפט verify, קובצי features/budgets/assets) לפני שבונים תוכן.

רף האיכות: משחק אינדי שיצא לשוק בז'אנר הזה. תוצאה בינונית נחשבת כישלון. אין טענה בלי ראיה מהסשן, מסתכלים על כל שינוי ויזואלי, מבקרים עצמאיים בכל אבן דרך, ודיווח כן על מגבלות.
```
