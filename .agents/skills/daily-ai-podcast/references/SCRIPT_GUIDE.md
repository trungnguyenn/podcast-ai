# AI Daily — Script Writing Guide

Solo monologue format for a 20-minute daily AI briefing. The biggest failure mode
is a host who just reports facts. A daily briefing is useful only when it tells
the listener what to think and what to decide — not just what happened.

---

## HOST PERSONA — Trung (Daily Anchor)

Same permanent host as Tech Radar, different mode. In daily briefing mode, Trung is:

- **Fast and sharp.** No warm-up. No "good morning everyone."
- **Analytically opinionated.** Every story gets a take, not just a summary.
- **Decision-oriented.** Ends each story segment with an implication for the listener.
- **Honest about uncertainty.** Willing to say "we don't know yet, but here's what to watch."

**Characteristic moves:**
- Opens with a number: "Một con số mở đầu ngày hôm nay:"
- Delivers the story in one sentence, then pivots to analysis
- Names who wins and who loses from each development
- Ends segments with a direct recommendation: "Nếu bạn đang build X, đây là điều cần chú ý:"
- Signals uncertainty: "Dữ liệu chưa đủ để kết luận, nhưng tín hiệu cho thấy..."

**HOST phrase palette (rotate, never repeat same opener twice):**
```
"Một con số mở đầu ngày hôm nay:"
"Tin đầu tiên, và theo tôi là quan trọng nhất:"
"Thành thật mà nói về tin này:"
"Nếu bỏ qua tất cả PR đi, điều đang thực sự xảy ra là:"
"Đây là điều mà nhiều người bỏ lỡ trong tin này:"
"Câu hỏi thực sự ở đây là:"
"Tác động trực tiếp đối với manager/builder:"
"Tôi muốn đưa ra một góc nhìn ngược lại:"
"Đây là tín hiệu, không phải sự kiện:"
"Trong 30 ngày tới, điều này nghĩa là:"
```

---

## STORY SEGMENT STRUCTURE (4–6 turns per story)

Each story follows this exact pattern. Never skip the analyst take.

```
Turn 1 — WHAT HAPPENED
  One sentence. Lead with the key number.
  "Google vừa ra mắt Gemma 4 hôm qua, với hơn 400 triệu lượt tải tích lũy và
   tuyên bố vượt trội hơn model lớn gấp 20 lần."

Turn 2 — WHY IT MATTERS TECHNICALLY
  2–3 sentences on the mechanism: why this is a real shift, not just a PR release.
  Name the technical constraint being broken or the capability being unlocked.

Turn 3 — COMPETITIVE SIGNAL
  1–2 sentences: who gains, who is threatened. Be specific about companies or categories.

Turn 4 — ANALYST TAKE FOR MANAGERS
  Direct recommendation framed as a decision:
  "Nếu bạn là engineering manager đang cân nhắc hạ tầng model cho 2026, câu hỏi
   bây giờ không còn là 'dùng API nào' mà là 'tự host hay mua API' — và Gemma 4
   vừa làm cho lựa chọn tự host trở nên khả thi hơn đáng kể."

Turn 5 (optional) — BUILDER SIGNAL
  If the story has a specific implication for people building AI solutions:
  "Với developer đang build sản phẩm AI cho doanh nghiệp Việt Nam: Apache 2.0
   nghĩa là bạn có thể deploy Gemma 4 trên infra của khách hàng mà không cần
   lo ngại về licensing hay data residency."

Turn 6 (optional) — BRIDGE
  1 sentence connecting this story to the next: "Và điều đó dẫn thẳng vào tin tiếp theo..."
```

---

## ANALYSIS SEGMENT — Cross-Story Pattern

After the 3 top stories, the "Phân tích chủ đề" segment is the highest-value part of the episode.

**Purpose:** Surface the pattern connecting the day's news. What does today collectively signal about where AI is heading in the next 30–90 days?

**Structure (5–7 turns):**

```
Turn 1 — NAME THE PATTERN
  "Nhìn lại ba tin hôm nay, có một mẫu chung:"
  State the cross-story theme in one sentence.

Turn 2 — EVIDENCE FROM TODAY'S NEWS
  Connect 2–3 specific facts from the stories to this pattern.
  "Microsoft ra MAI models, Google mã nguồn mở Gemma 4, và OpenAI giảm giá Codex
   20 phần trăm — ba bước đi hoàn toàn khác nhau, nhưng cùng hướng về một điều:
   AI infrastructure đang bị commoditize."

Turn 3 — HISTORICAL ANALOG (optional but powerful)
  1–2 sentences: what does this remind us of from tech history?
  "Đây giống với giai đoạn 2014–2015 của cloud, khi AWS và Google Cloud bắt đầu
   cuộc chiến giảm giá storage và compute."

Turn 4 — IMPLICATION TIMELINE
  What to expect in the next 30, 60, 90 days based on this pattern.

Turn 5 — MANAGER DECISION FRAME
  "Câu hỏi cho manager tuần này:"
  Pose the decision each listener should be thinking about. Not a rhetorical question —
  give them the framework to answer it for their own context.

Turn 6 — BUILDER DECISION FRAME
  "Với người đang build:"
  Specific go/no-go or build/buy/wait signal based on today's pattern.

Turn 7 — UNCERTAINTY ACKNOWLEDGMENT
  What remains unknown. Be honest: "Điều chúng ta chưa biết là..."
```

---

## ACTIONABLE TAKEAWAYS SEGMENT

5-minute segment, tight. Every sentence is either a signal or a recommendation.

**Format per takeaway:**
```
[SEGMENT_BREAK: Tín hiệu & Quyết định]

[HOST] Trước khi kết thúc, ba điều cần mang theo từ hôm nay.

[HOST] Thứ nhất, [signal]. Điều này có nghĩa là [implication].
       Nếu bạn đang [situation], bây giờ là lúc [action].

[HOST] Thứ hai, [signal]. [Implication]. [Action].

[HOST] Thứ ba, [signal]. [Implication]. [Action].
```

Never more than 3 takeaways. Better to say 2 things well than 5 things vaguely.

---

## OPENING RULES

**Never write:**
- "Xin chào các bạn" / "Chào mừng đến với AI Daily"
- "Hôm nay chúng ta sẽ nói về..."
- Any warm-up or pleasantry

**Always open with one of:**
- **Number:** "Một con số: [X]. Đây là cách ngày [DATE] bắt đầu trong ngành AI."
- **Claim:** "Hôm nay là một trong những ngày bận rộn nhất ngành AI từ đầu năm. [Specific reason]."
- **Contrast:** "Tuần trước, câu hỏi là [X]. Hôm nay, câu trả lời bắt đầu hiện ra."
- **Urgency:** "Có ba thứ xảy ra trong 24 giờ qua mà bạn cần biết trước khi đưa ra bất kỳ quyết định nào về AI tuần này."

---

## CLOSING RULES

2 unresolved questions + a resonant final line. No sign-off.

**Good closing questions:**
- Questions about timing: "Khi nào thì open models thực sự thay thế được API của big labs trong production?"
- Questions about who captures value: "Khi infrastructure AI trở thành commodity, ai thực sự kiếm tiền từ nó?"
- Questions about second-order effects: "Nếu 40% nhân sự trong nhiều công ty bị ảnh hưởng bởi AI, câu hỏi chính sách nào sẽ buộc các công ty phải trả lời?"

**Good final line:**
Something that gives the listener a frame to carry into their day, not a summary.
"Thứ duy nhất chắc chắn hôm nay: tốc độ thay đổi đang nhanh hơn tốc độ ra quyết định. Nhiệm vụ của bạn là thu hẹp khoảng cách đó."

**Bad final line:** Any version of "Hẹn gặp lại ngày mai" or "Cảm ơn đã lắng nghe."

---

## PACING RULES

**Turn length variety (required):**
```
[SHORT]  1 sentence — fact or transition
[MEDIUM] 2–3 sentences — explanation or signal
[LONG]   4–6 sentences — analyst take or pattern analysis
```

Never 4+ consecutive [HOST] turns of the same length.
Alternate: LONG → SHORT → MEDIUM → SHORT → LONG

**Segment rhythm:**
- Story segments: 4–6 turns each
- Analysis segment: 5–7 turns (the longest, most valuable)
- Takeaways: 3–4 turns (tight, no padding)
- Close: 2–3 turns

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

Allowed punctuation: `,` `.` `?` `!` `...`

---

## FULL SCRIPT TEMPLATE

```
TITLE: AI Daily — [natural Vietnamese date]
SUBTITLE: [one sentence — the angle that makes today worth 20 minutes]
EPISODE: #[N] | [DATE] | Host: Trung

[INTRO_MUSIC]

[HOST] [Opening — number or claim — no greeting]

[HOST] [Setup: today has 3 stories, here's the thread connecting them]

[SEGMENT_BREAK: Tin số 1 — [Story title]]

[HOST] [What happened — key number]
[HOST] [Why it matters technically]
[HOST] [Competitive signal]
[HOST] [Analyst take for managers]
[HOST] [Builder signal if applicable]

[SEGMENT_BREAK: Tin số 2 — [Story title]]

[HOST] ...

[SEGMENT_BREAK: Tin số 3 — [Story title]]

[HOST] ...

[SEGMENT_BREAK: Phân tích — [Theme name]]

[HOST] [Name the pattern]
[HOST] [Evidence from today's news]
[HOST] [Historical analog]
[HOST] [Implication timeline — 30/60/90 days]
[HOST] [Manager decision frame]
[HOST] [Builder decision frame]
[HOST] [Uncertainty acknowledgment]

[SEGMENT_BREAK: Tín hiệu & Quyết định]

[HOST] [Intro — 3 things to take from today]
[HOST] [Takeaway 1 — signal + implication + action]
[HOST] [Takeaway 2 — signal + implication + action]
[HOST] [Takeaway 3 — signal + implication + action]

[SEGMENT_BREAK: Kết]

[HOST] [Unresolved question 1]
[HOST] [Unresolved question 2]
[HOST] [Final line with weight — no sign-off]

[OUTRO_MUSIC]

SOURCES:
1. [Source] — [URL] — [date] — cited for [fact]
```
