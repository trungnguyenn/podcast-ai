# AI Weekly Radar — Script Writing Guide

Two-host dialogue format for a 40-45 minute weekly AI briefing. The biggest failure mode
is a pair of hosts who just take turns reading summaries at each other. The weekly format
only earns its length when HOST and GUEST genuinely push, challenge, and build on each other
— not when they politely agree and move on.

---

## HOST & GUEST PERSONAS

### Trung — The Anchor (HOST)

Trung sets the frame, controls the pace, and translates technical/strategic points into
decisions the listener can act on. In weekly mode, Trung is:

- **Structurally sharp.** Introduces each segment, names what we're looking at, and closes
  each segment with a concrete takeaway.
- **The audience's voice.** Asks the question the listener is thinking but might not know
  how to ask technically.
- **Occasionally provocative.** Willing to push back on An's take or take a contrarian view
  to force a more honest analysis.
- **miền Tây grounded.** Drops a natural Southern Vietnamese metaphor when it clarifies
  rather than when it decorates.

**Characteristic Trung moves:**
- Opens stories with a number: "Con số của tuần này:"
- Names what's really at stake: "Nhưng câu hỏi thực sự là..."
- Forces specificity: "Nói thật hơn chút đi, ý em là gì cụ thể?"
- Closes segments with decision framing: "Vậy anh em manager cần làm gì với thông tin này?"
- Signals the counter: "Có người sẽ phản biện rằng..."

### An — The Analyst (GUEST)

An is an AI Market & Product Strategist. Her role is to provide the analytical depth behind
Trung's questions — the data, the competitive read, and the operational implication. An is:

- **Evidence-anchored.** Every claim has a number or a specific source behind it.
- **Willing to say what's hard.** If the honest answer is "it's too early to tell" or
  "this is dangerous for teams without governance," she says it.
- **Decision-oriented.** Never leaves a topic without a recommendation framed as a
  concrete action or a watch item.
- **Warm but firm.** Agreeable on tone, direct on substance. Doesn't hedge to be polite.

**Characteristic An moves:**
- Leads with evidence: "Chuẩn. Và con số em thấy là..."
- Layers the analysis: "Có hai lớp ở đây. Lớp đầu là... Lớp thứ hai, quan trọng hơn, là..."
- Names the winner and loser: "Ai được lợi từ đây? Và ai cần lo?"
- Signals uncertainty honestly: "Dữ liệu chưa đủ để kết luận, nhưng tín hiệu cho thấy..."
- Gives specific advice: "Với builder đang build X, em khuyên..."

---

## REQUIRED SKELETON SEGMENTS

Every episode uses these five segments in order. Everything else is optional modules
inserted between Segment 3 and Segment 5.

### SEGMENT: Cold Open (after INTRO_MUSIC, before first SEGMENT_BREAK)

- **Length:** 6–10 turns, alternating HOST/GUEST
- **HOST opens:** One number or one claim that defines the week. No greeting. No preamble.
- **GUEST:** First analytical take on why this number/claim matters
- **HOST:** Frames the week's thread — "three stories that look unrelated but point at the same thing"
- **GUEST:** Names the modules coming up in today's episode (naturally, not as a list)
- **Closes:** HOST gives the time window — "Tuần từ [date] tới [date], và mình sẽ kéo dài
  tới [2-4 week horizon]"

**Opening patterns (rotate — never repeat the same one twice):**
```
"Con số của tuần này: [X]. Đây là cách tuần vừa qua mở đầu trong ngành AI."
"Tuần vừa rồi có ba thứ xảy ra mà nếu bỏ qua, bạn sẽ ra quyết định thiếu dữ liệu cả tháng."
"Nếu phải đặt tên cho tuần này, anh sẽ gọi là tuần của [theme]. Em có đồng ý không?"
"Tuần này thị trường không ồn vì tin mới. Nó ồn vì tin cũ bắt đầu va nhau."
"Có một điều xảy ra tuần này mà nhiều người nghe rồi gật đầu, nhưng chưa ai rút ra đúng kết luận."
```

---

### SEGMENT: Week Recap (Segment_BREAK: Tuần qua — [theme])

- **Length:** 3–5 stories, 6–10 turns per story
- **Per story structure (6-turn pattern):**

```
Turn 1 [HOST] — WHAT HAPPENED
  One sentence. Lead with the key number.
  "Microsoft vừa ra ba model MAI tự phát triển, với team dưới 10 kỹ sư mỗi model."

Turn 2 [GUEST] — WHY IT MATTERS TECHNICALLY
  2–3 sentences. The mechanism. What constraint is being broken or capability unlocked.

Turn 3 [HOST] — AUDIENCE QUESTION / PUSHBACK
  Speak for the listener. "Nhưng nhiều người sẽ nói đây chỉ là marketing move của
  Microsoft để giảm giá Microsoft 365. Em nghĩ sao?"

Turn 4 [GUEST] — COMPETITIVE SIGNAL
  Who gains, who is threatened. Be specific about companies or categories.
  Name the second-order effect.

Turn 5 [GUEST] — ANALYST TAKE
  Direct recommendation framed as a decision:
  "Nếu bạn là engineering manager đang ký hợp đồng Azure mới trong Q2 này, đây là
  đòn bẩy bạn có mà chưa dùng..."

Turn 6 [HOST] — BRIDGE
  1 sentence connecting to the next story or naming what we just established.
```

**Between stories:** `[SEGMENT_BREAK: Tuần qua — [story N title]]` labels keep navigation clean.
For 3 stories, use three breaks. For 5 stories, group stories 4-5 under one break with faster pacing.

---

### SEGMENT: Pattern Analysis (Segment_BREAK: Phân tích — [theme name])

The highest-value segment of the weekly. Surfaces the pattern connecting the week's news.

- **Length:** 8–12 turns
- **Structure:**

```
Turn 1 [HOST] — NAME THE PATTERN
  "Nhìn lại [N] tin tuần này, có một mẫu chung mà mình muốn đặt tên cho nó:"
  State the cross-story theme in one sentence.

Turn 2 [GUEST] — EVIDENCE FROM THIS WEEK'S NEWS
  Connect 2–3 specific facts from the stories to this pattern.
  "Microsoft làm MAI, OpenAI cắt Sora, và doanh nghiệp siết agent governance — ba
   bước đi hoàn toàn khác nhau nhưng cùng báo hiệu: lớp model đang bị commoditize."

Turn 3 [HOST] — HISTORICAL ANALOG (optional but powerful)
  What does this remind us of from tech history?

Turn 4 [GUEST] — WHY THIS WEEK WAS THE INFLECTION POINT
  Not "this is a trend" (everyone says that). Why this specific week moved things.

Turn 5 [HOST] — CHALLENGE THE PATTERN
  "Nhưng em có chắc không? Có người sẽ nói [counter-argument]..."

Turn 6 [GUEST] — DEFEND OR QUALIFY
  Either defend with more evidence, or honestly qualify: "Đúng là có giới hạn của
  lý luận này, cụ thể là..."

Turn 7 [GUEST] — IMPLICATION TIMELINE
  What to expect in the next 30, 60, 90 days based on this pattern.

Turn 8 [HOST] — MANAGER DECISION FRAME
  "Câu hỏi cho manager tuần này là..."
  Give them the framework to answer it for their own context.

Turn 9 [GUEST] — BUILDER DECISION FRAME
  "Với người đang build:"
  Specific go/no-go or build/buy/wait signal.

Turn 10 [HOST or GUEST] — UNCERTAINTY ACKNOWLEDGMENT
  What remains genuinely unknown. "Điều chúng ta chưa biết là..."
```

---

### SEGMENT: Forward Look (Segment_BREAK: Tín hiệu tuần tới)

- **Length:** 4–6 turns
- Draws from `forward` array in `research.json` and from pattern analysis implications
- Per signal: what to watch, what trigger confirms it, what action it implies

```
[HOST] Trước khi khép lại, nhìn ra 2 tới 4 tuần tới.
[GUEST] Tín hiệu thứ nhất: [signal]. Trigger cần theo dõi: [specific event]. Nếu nó xảy ra, [implication].
[HOST] Tín hiệu thứ hai? 
[GUEST] [second signal]
[HOST] Tín hiệu thứ ba, nếu có?
[GUEST] [third signal or honest "chưa rõ"]
```

---

### SEGMENT: Closing (Segment_BREAK: Kết)

- **Length:** 6–9 turns
- Three consecutive `[HOST]` lines for the closing questions
- GUEST send-off — one line, no sign-off phrase
- HOST final line — resonant, carries a frame for the week ahead

```
[HOST] [Week summary in 1–2 sentences — what this week established]
[GUEST] [Guest's final synthesis — the one thing to carry from this week]
[HOST] Trước khi kết thúc, ba câu hỏi mở mà anh em mang vào cuộc họp tuần sau.
[HOST] Câu một: [question — genuinely unresolved, no obvious answer]
[HOST] Câu hai: [question — forward-looking, about timing or who captures value]
[HOST] Câu ba: [question — structural, long-horizon]
[GUEST] [One line send-off — warm, not a sign-off]
[HOST] [Final resonant line — a frame for the week, not a summary]
```

**Good closing questions:**
- About timing: "Khi nào thì [shift] thực sự xảy ra ở quy mô enterprise Việt Nam?"
- About who captures value: "Khi lớp model AI trở thành hàng hóa, ai thực sự nắm giá trị?"
- About second-order effects: "Nếu [trend] tiếp tục thêm hai quý, bài toán nào sẽ buộc các
  công ty phải giải quyết mà họ chưa chuẩn bị?"

**Good final lines (resonant close, no sign-off):**
```
"Tuần tới sẽ có thêm tin. Nhưng câu hỏi từ tuần này sẽ không biến mất."
"Tốc độ thay đổi nhanh hơn tốc độ ra quyết định. Nhiệm vụ của bạn là thu hẹp khoảng cách đó."
"Trong AI, kẻ thắng không phải người đi nhanh nhất. Mà là người biết dừng đúng lúc để nhìn bản đồ."
```

---

## OPTIONAL CREATIVE MODULES

Pick **2–3 per episode** based on `brief.md` module selection. Insert between Pattern Analysis
and Forward Look.

---

### MODULE: Forecast Review *(series memory — use when open_forecasts ≥ 1)*

**Use when:** There are open forecasts from previous **weekly** episodes in `weekly_series_context.json`.
**Length:** 6–10 turns
**Label:** `[SEGMENT_BREAK: Forecast Review]`
**Position:** Immediately after the opening segment, before main stories — anchors continuity early.

This module is triggered automatically when `open_forecasts` in the weekly registry is non-empty.
Include at most 3 forecasts; summarise the rest in one line. Mark each as **resolved**, **still open**, or **partially confirmed**.

```
[HOST] Trước khi đi vào tin tức tuần này, mình điểm lại mấy dự báo từ các số trước.
[GUEST] Có [N] dự báo còn mở. Em bắt đầu từ cái gần nhất.
[GUEST] Tuần trước mình nói [forecast text]. Tuần này có gì xảy ra?
[HOST] [What actually happened — one sentence of evidence.]
[GUEST] Mình đánh dấu đây là [resolved / vẫn còn mở / xác nhận một phần].
        Lý do: [brief rationale — max 2 sentences].

[GUEST] Dự báo tiếp theo: [next forecast text]. Cập nhật: [status + evidence].
[HOST] Cái này thú vị hơn — [add a quick observation or reframe if resolved].

--- if ≥ 3 open forecasts ---
[HOST] Còn [N] dự báo khác từ các số cũ — mình tổng hợp nhanh.
[GUEST] [One-sentence summary of remaining open items.]
[HOST] Tốt. Giờ đi vào tin tức tuần này.
```

**Memory write-back (in Phase 7 Step 7a):**
After producing the script, fill in `resolved_slugs` in the memory update script with the slugs
of any forecasts the Forecast Review module closed this episode.

---

### MODULE: Forecast (base/bull/bear)

**Use when:** Week has enough directional signals for a 2-4 week forecast with real stakes.
**Length:** 10–14 turns
**Label:** `[SEGMENT_BREAK: Forecast — [scenario title]]`

```
[HOST] Mình vô forecast. Ba kịch bản cho 2 tới 4 tuần tới.
[GUEST] Em chia base, bull, bear với xác suất ước tính. Base khoảng [N] phần trăm, bull [N], bear [N].

--- Base case ---
[HOST] Base case trước.
[GUEST] [What happens, trigger signals, manager implication, builder implication, the trap]

--- Bull case ---
[HOST] Bull case?
[GUEST] [What happens, trigger signals, how to position, what to do NOW to capture it]

--- Bear case ---
[HOST] Bear case. Nói thật coi.
[GUEST] [What happens, trigger signals, early warning metrics, how to defend]

[HOST] Đội nào dễ hưởng lợi nhất bất kể case nào?
[GUEST] [Teams with discipline] vì [reason].
[HOST] Đội nào dễ đau nhất?
[GUEST] [Teams without discipline] vì [reason].
[GUEST] [One memorable forecast sentence]
```

---

### MODULE: Action Board

**Use when:** Week has enough discrete, actionable signals for both roles.
**Length:** 12–18 turns
**Label:** `[SEGMENT_BREAK: Action Board — Manager]` then `[SEGMENT_BREAK: Action Board — Builder]`

Structure: HOST asks "Việc [N]?" after each one. GUEST delivers each action (2–4 sentences: what to do + why + common mistake to avoid). Aim for 5–7 actions per role.

**Manager action pattern:**
```
[HOST] Với manager, việc [N]?
[GUEST] [Action]. [Why now]. [Common mistake to avoid].
```

**Builder action pattern:**
```
[HOST] Builder, việc [N]?
[GUEST] [Action]. [Specific technical or workflow detail]. [When it's done].
```

End with a 7-day plan for small teams (2–3 people, one manager/PM):
```
[HOST] Team nhỏ hai ba người, nổi không?
[GUEST] Nổi. Ngày một [X]. Ngày ba [Y]. Ngày năm [Z]. Ngày bảy xem số.
```

---

### MODULE: Myth vs Reality

**Use when:** Week had recurring misconceptions in coverage or community reaction.
**Length:** 8–14 turns (1 turn per myth-reality pair)
**Label:** `[SEGMENT_BREAK: Myth vs Reality]`

Format: HOST states the myth, GUEST delivers the reality in 1–3 sentences.
Aim for 5–8 pairs. Keep each pair under 4 turns total.

```
[HOST] Myth số [N]: [claim that sounds true but isn't, or is only half-true].
[GUEST] Reality: [specific counter-evidence or qualification]. [Implication for teams].
[HOST] [Optional: reinforcing point or "nghe đau mà đúng" acknowledgment]
```

**Good myths come from:**
- Viral LinkedIn/X takes that oversimplify
- Marketing claims from vendors that week
- Beliefs your target audience holds that the week's evidence contradicts

---

### MODULE: CTO Decision Board

**Use when:** Week's news demands several discrete, time-sensitive decisions.
**Length:** 10–14 turns
**Label:** `[SEGMENT_BREAK: Nếu là CTO trước 5PM hôm nay]`

HOST frames the scenario. GUEST delivers 5–7 decisions a CTO should make today (or this week).
Keep each decision to 2–3 sentences: what to decide + why now + common mistake.

```
[HOST] Bài tập nhanh. Nếu bây giờ là chiều thứ Sáu, trước 5PM, anh là CTO.
       Chỉ được quyết vài việc. Anh chọn gì?
[GUEST] Quyết định thứ nhất: [decision]. [Why this week specifically]. [What happens if you skip it].
[HOST] Thứ hai?
[GUEST] [decision 2]
...
[HOST] Anh thêm một cái: [HOST's own decision — adds a peer perspective].
[GUEST] Đồng ý. [Reinforcement or qualifier].
```

---

### MODULE: Hot Take Duel

**Use when:** The week has a genuinely controversial claim where smart people disagree.
**Length:** 10–16 turns
**Label:** `[SEGMENT_BREAK: Hot Take — [claim]]`

HOST and GUEST take opposite sides (HOST is the challenger/skeptic, GUEST is the defender/analyst).
After 3–4 turns each, one of them concedes or qualifies. No consensus forced.

```
[HOST] Mình chơi Hot Take một cái. Tuyên bố: "[Controversial claim from this week's news]".
       Anh đứng phía [side]. Em bảo vệ phía ngược lại.
[GUEST] Được. Em đồng ý với tuyên bố này vì...
[HOST] Không đồng ý. Vì...
[GUEST] Em hiểu góc đó, nhưng...
[HOST] Fair point. Nhưng anh vẫn giữ rằng...
[GUEST] Okay, anh thắng ở điểm [X]. Nhưng điểm [Y] em vẫn giữ.
[HOST] Kết: không có đáp án đơn. Người nghe tự quyết theo ngữ cảnh của mình.
```

**Good hot take claims:**
- "[Company X]'s [move] is more about narrative control than product strategy"
- "The [Y] trend will plateau by Q3 2026 because [Z]"
- "Teams that adopt [tool/approach] now are taking on more risk than reward"

---

### MODULE: Rebuttal Round

**Use when:** Week generated strong pushback or controversy in the community.
**Length:** 8–12 turns (2 turns per rebuttal)
**Label:** `[SEGMENT_BREAK: Phản biện nhanh]`

HOST voices 4–5 counterarguments heard that week. GUEST rejects, accepts, or qualifies each.
Keep each rebuttal pair tight (1 HOST line + 1–2 GUEST lines).

```
[HOST] Có một phản biện em nghe nhiều tuần này: "[counterargument]".
[GUEST] [Reject with evidence] / [Accept with qualification] / [Partially accept + reframe].
```

---

### MODULE: Signal vs Noise

**Use when:** The week had many announcements that are hard to separate from hype.
**Length:** 8–12 turns
**Label:** `[SEGMENT_BREAK: Signal vs Noise]`

For 3–5 items from the week: HOST names the item, GUEST classifies it as Signal (real shift)
or Noise (hype/distraction) with a specific reason.

```
[HOST] Phân loại nhanh. [Item from this week's news]: Signal hay Noise?
[GUEST] Signal. Vì [specific reason with evidence].
  / Noise. Vì [specific reason — usually missing: numbers, production evidence, clear use case].
  / Cần thêm thời gian. Trigger cần theo dõi: [specific event].
[HOST] [Optional: 1-line reinforcement or "tại sao nhiều người nhầm" note]
```

---

### MODULE: Decision Playbook

**Use when:** Decision-dense week with clear 2-week horizon actions.
**Length:** 10–14 turns
**Label:** `[SEGMENT_BREAK: Sổ tay quyết định]`

5 decisions to make + 5 "đừng làm" for both managers and builders.

```
[HOST] Nếu trong 2 tuần tới team chỉ được phép đưa ra năm quyết định?
[GUEST] Quyết định [N]: [decision]. [Why this window]. [How to know it's done].
...
[HOST] Và năm "đừng làm"?
[GUEST] Đừng [X]. Đừng [Y]. Đừng [Z]. Đừng [A]. Đừng [B].
[HOST] Với manager riêng, còn năm "đừng làm" nào?
[GUEST] [manager-specific don'ts]
```

---

## PACING RULES

**Turn length variety (required):**
```
[SHORT]  1 sentence — fact, transition, or HOST question
[MEDIUM] 2–3 sentences — explanation or competitive signal
[LONG]   4–6 sentences — analyst take or pattern analysis
```

Never 4+ consecutive turns of the same length.
Alternate: LONG → SHORT → MEDIUM → SHORT → LONG

**Dialogue rhythm for HOST:**
- HOST turns should average shorter than GUEST turns
- HOST's role is to drive the frame, not fill the analysis
- A HOST turn over 4 sentences is a red flag — it's stealing GUEST airtime

**Segment rhythm:**
- Cold open: 6–10 turns
- Each story: 6–10 turns
- Pattern analysis: 8–12 turns (the intellectual center)
- Optional modules: 8–16 turns each (see above)
- Forward look: 4–6 turns
- Closing: 6–9 turns

**Turn balance check:**
- GUEST turns must be ≥ 40% of all turns
- HOST turns must be ≤ 55% of all turns
- No speaker should have 8+ consecutive turns without the other speaking

---

## SPOKEN TEXT RULES

TTS reads every character. No exceptions.

| Rule | Wrong | Right |
|------|-------|-------|
| No dashes as pause | `điều này — theo tôi —` | `điều này, theo tôi,` |
| No em-dash | `chúng ta sẽ—` | `chúng ta sẽ... à,` |
| No ISO dates | `2026-04-03` | `ngày 3 tháng 4 năm 2026` |
| No hyphenated tech terms | `open-source`, `fine-tuning` | `mã nguồn mở`, `điều chỉnh tinh` |
| No bullet lists in speech | `gồm: - A - B` | `gồm A, B, và C` |
| No markdown bold | `**quan trọng**` | `quan trọng` |
| Expand currencies | `2.5B USD` | `hai tỷ rưỡi đô la Mỹ` |
| Expand percentages | `44%` | `44 phần trăm` |
| Spoken date form | `Q1 2026` | `quý 1 năm 2026` |

Allowed punctuation: `,` `.` `?` `!` `...`

---

## FULL SCRIPT TEMPLATE

```
TITLE: AI Weekly Radar — [natural Vietnamese date range]
SUBTITLE: [one sentence — the angle that makes this week worth 40 minutes]
EPISODE: #[N] | [DATE] | Host: Trung & An (AI Market & Product Strategist)

[INTRO_MUSIC]

[HOST] [Cold open — number or claim — no greeting]
[GUEST] [First take]
[HOST] [Thread framing — "three things this week that look unrelated but point at the same thing"]
[GUEST] [What we're doing today — naturally, not a list]
[HOST] [Time window statement]
[GUEST] [The week's defining angle — sets up what follows]

[SEGMENT_BREAK: Tuần qua — [Story 1 title]]

[HOST] [What happened — key number]
[GUEST] [Why it matters technically]
[HOST] [Audience question or pushback]
[GUEST] [Competitive signal]
[GUEST] [Analyst take for managers/builders]
[HOST] [Bridge to story 2]

[SEGMENT_BREAK: Tuần qua — [Story 2 title]]

[HOST] ...
[GUEST] ...

[SEGMENT_BREAK: Tuần qua — [Story 3 title]]  [add more if needed]

[HOST] ...
[GUEST] ...

[SEGMENT_BREAK: Phân tích — [Theme name]]

[HOST] [Name the pattern]
[GUEST] [Evidence from this week's news]
[HOST] [Historical analog or challenge]
[GUEST] [Defend or qualify]
[GUEST] [Implication timeline — 30/60/90 days]
[HOST] [Manager decision frame]
[GUEST] [Builder decision frame]
[HOST or GUEST] [Uncertainty acknowledgment]

[--- 2-3 OPTIONAL MODULES HERE ---]
[SEGMENT_BREAK: [Module name]]
... module turns ...

[SEGMENT_BREAK: Tín hiệu tuần tới]

[HOST] [Intro to forward look]
[GUEST] [Signal 1 — what to watch, trigger, implication]
[HOST] [Signal 2 prompt]
[GUEST] [Signal 2]
[HOST] [Signal 3 prompt]
[GUEST] [Signal 3 or honest uncertainty]

[SEGMENT_BREAK: Kết]

[HOST] [Week summary — 1–2 sentences, what this week established]
[GUEST] [Guest's final synthesis]
[HOST] Trước khi kết thúc, ba câu hỏi mở mà anh em mang vào cuộc họp tuần sau.
[HOST] Câu một: [unresolved question 1]
[HOST] Câu hai: [unresolved question 2]
[HOST] Câu ba: [unresolved question 3]
[GUEST] [Send-off — warm, no sign-off phrase]
[HOST] [Final resonant line — a frame for the week, not a summary]

[OUTRO_MUSIC]

SOURCES:
1. [Source] — [URL] — [date] — cited for [fact]
```
