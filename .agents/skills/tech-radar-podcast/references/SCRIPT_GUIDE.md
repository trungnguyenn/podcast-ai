# Tech Radar — Script Writing Guide

This guide defines how to write natural, engaging English dialogue for Tech Radar episodes.
The biggest failure mode is two speakers taking turns reading prepared monologues.
Real podcast conversations are messier, more reactive, and more human.

For Vietnamese translation guidance, see [VIETNAMESE_NOTES.md](VIETNAMESE_NOTES.md).

---

## HOST & GUEST PERSONAS

### HOST — Trung (Director of Technology, permanent)

Strategic, business-focused. 20+ years software leadership. Makes bold claims.
Forces every technical conversation to confront business implications. Plays devil's advocate.
Asks questions that make engineers uncomfortable. Genuinely curious — not just a moderator.

**Characteristic moves:**
- Opens a topic with a number, not a question: "Here's a number: [X]."
- Challenges optimistic takes: "But I want to push back — that number ignores [Y]."
- Bridges technical to business: "What that means for pricing models is [implication]."
- Asks genuinely hard questions: "The question nobody wants to ask is..."
- Admits uncertainty: "Honestly, I'm not sure about this one..."

**Phrase palette for HOST:**
These are tonal options, not mandatory catchphrases. Rotate them naturally.
Avoid repeating the same opening phrase more than once in a script unless the callback is intentional.
```
"Let me be direct..."
"Honestly..."
"The short version is..."
"If you strip away all the PR..."
"What bothers me is..."
"I'm going to be a bit picky here..."
"To be fair..."
"The more interesting question is..."
"If you look at this as a business person..."
"I'm not entirely convinced on this point."
"Here's the uncomfortable math:"
"The question nobody wants to ask is..."
"Let's be honest about this:"
"Actually, [admission of complexity]."
```

---

### GUEST — [GUEST_NAME] ([GUEST_ROLE], unique per episode)

Deep domain expert shaped by their specific role. Not a talking head — they have
opinions, have been burned before, and push back with evidence. They also ask
Trung questions; this is a dialogue, not an interview.

**Role-specific language:**
- **Security Architect:** attack surfaces, compliance gaps, trust boundaries, SOC 2
- **Data Platform Lead:** pipelines, latency, schema contracts, backfill complexity
- **Healthcare Informatics:** clinician burden, HL7, EHR integration, workflow friction
- **AI Research Engineer:** eval frameworks, benchmark limitations, capability jumps
- **Platform Engineer:** blast radius, toil, SLO, on-call burden

**Characteristic moves:**
- Grounds claims with specific numbers: "The actual number is..."
- Adds detail Trung skipped: "But there's a subtle but important point here:"
- Shares domain war stories: "We actually tried this. The result was..."
- Asks Trung for his take: "Do you see that on the business side?"
- Concedes partial points: "You're right about [X], but [Y] is still a problem."

**Phrase palette for GUEST:**
These are examples of voice texture, not fixed lines to reuse verbatim.
Prefer light variation over exact repetition.
```
"The actual number is..."
"If you look at the data..."
"This is more important than it sounds..."
"The subtlety is..."
"I think we need to separate two layers of the problem here:"
"If you've actually deployed this in production, you'll know..."
"But there's a specific data point I want to highlight:"
"Let me explain why this matters in [domain] specifically:"
"We tried this. The result was..."
"Do you see that on the business side?"
```

---

## NATURAL DIALOGUE TECHNIQUES

### 1. Mix Turn Lengths (Critical)

Real conversations have rhythm — short reactions followed by deeper explanations.
Never write all turns at the same length.

**Pattern:**
```
[LONG]   3–4 sentences — main point or explanation
[SHORT]  1 sentence — reaction, agreement, or pivot
[LONG]   3–4 sentences — development or rebuttal
[SHORT]  1 sentence — question or callback
```

**Example of varied pacing:**
```
[HOST] Here's a number: 78 percent of developers are using AI coding tools, according to
last year's Stack Overflow Survey. And that happened in just 18 months. The adoption rate
is faster than anything I've seen in 20 years in this industry.

[GUEST] Yeah, exactly. And in the enterprise environment I work in, the number is even higher.

[HOST] So why are we still debating whether AI coding actually delivers value?

[GUEST] Because adoption rate and actual productivity improvement are two completely different
things. Here's where I want to push back: that 78 percent only says people installed the tool,
not that the tool is helping. We have internal data, and what we see is pretty complicated.

[HOST] Complicated how? Can you elaborate?
```

---

### 2. Reaction Turns

Before diving into a point, acknowledge what was just said. 1 sentence max.

**Natural reactions:**
```
"Exactly."
"Good point."
"Oh, that's interesting."
"Yeah, right."
"That makes sense."
"I see what you mean."
"That says a lot."
"And here's the hard part:"
"Okay, let me reconsider that..."
"[laugh] Actually..."
"I was thinking the same, but..."
"You just hit on exactly what I wanted to say."
```

**Avoid:** Jumping immediately to the next point without acknowledging the previous one.
Also avoid leaning on one favorite reaction phrase throughout the whole episode.

---

### 3. Guest Asks Questions Too

This is the most-violated rule. The GUEST must ask Trung questions — minimum 3 per episode.
A guest who only responds is an interviewee, not a co-host.

**Guest question patterns:**
```
"Do you see this on the business side?"
"What do you think happens to [X] in the next two years?"
"Do you know any examples of companies doing this?"
"Does that worry you about [Y]?"
"How do you think the pricing model will change?"
```

---

### 4. Callbacks to Earlier Points

Reference things said earlier in the conversation. Creates coherence and feels natural.

```
"Remember that number you mentioned — [X] — this is where it connects to security."
"Going back to the [Company] case study from earlier — how did they solve that?"
"That's exactly the 'uncomfortable math' you brought up at the beginning."
"Wait, you just contradicted yourself a bit — earlier you said [X], now you're saying [Y]."
```

---

### 5. Thought Interruption and Completion

One speaker interrupts or picks up the other's thought. **Do NOT use dashes (em-dash, en-dash)** —
TTS will read them aloud. Use natural speech patterns instead:

**Interrupt with a new sentence starting the completion:**
```
[HOST] And if that's true, then the business model for software services companies...

[GUEST] Gets completely disrupted. Exactly. This is what we're seeing at...
```

**Or use a natural transition phrase:**
```
[HOST] And if that's true, what I'm trying to say is...

[GUEST] That the entire pricing model changes. Right. And this is what we're seeing.
```

Use this technique sparingly — 2–3 times per episode maximum.

---

### 6. Genuine Surprise and Curiosity

When a surprising fact comes up, react to it genuinely. Don't just accept everything.

```
[HOST] Which report is that number from?

[GUEST] Actually? I've seen different numbers depending on the source. The one I trust more is...

[HOST] Oh. That changes the picture considerably.
```

---

### 7. Tone Cue Markers

Use inline tone cues to guide TTS expressiveness. These are stripped before audio
generation but help the agent write more natural text.

| Marker | Meaning |
|--------|---------|
| `[laugh]` | Light, self-aware laughter |
| `[pause]` | Thoughtful pause before an important point |
| `[serious]` | Shift to a more serious register |
| `[energetic]` | Upbeat, energetic delivery |
| `[reflective]` | Quiet, reflective tone |

**Example:**
```
[GUEST] [laugh] That's the question everyone on my team fights about.
[HOST] [serious] But it's the most important question of today's episode.
```

---

### 8. Genuine Disagreements (Minimum 2 per Episode)

Disagreements must be specific — not vague "I see it differently." Pushback needs evidence.

**Weak disagreement (avoid):**
```
[HOST] I think AI will replace developers.
[GUEST] I disagree. I think AI is just a tool.
```

**Strong disagreement (use this):**
```
[HOST] According to McKinsey, AI can automate 30 percent of developer work. If that's true,
we're talking about headcount reduction at massive scale.

[GUEST] I want to push back hard on that number. McKinsey measured tasks that can be automated,
not jobs that can be automated. According to data from GitHub, which has over 100 million
developers on the platform, productivity went up but headcount didn't go down. Right now,
there's no clear evidence for job replacement at that scale.

[HOST] Fair point. But what about the time lag? Maybe we just haven't reached that moment yet?

[GUEST] Maybe. But I'll also say: in healthcare IT, we're actually hiring more engineers
because AI creates new work, not less. Is that proof you're wrong? [laugh] I'm not sure.
```

---

## OPENING RULES (never violate)

**Never write:** "Hello", "Welcome to the show", "Today we'll discuss...",
"Thanks for listening", or any pleasantry.

**Always open with one of:**
- **Fact:** "Here's a number: [X from research]. Let that sink in."
- **Claim:** "This episode is different from every episode before. [Specific reason why]."
- **Scene:** "This week, [specific company or event] did [specific action]. That's our starting point."
- **Question:** "The question I want to put on the table right away: [question with no easy answer]."

---

## CLOSING RULES

- 3 open questions — genuinely unresolved, no obvious answers
- Final line: weight and resonance — not a sign-off

**Good closing question:** "When AI triples productivity, how do software services companies
reprice, and who captures that value?"

**Bad closing question:** "Are you ready to adopt AI?" (too easy, too vague)

**Good final line:** "One thing is certain: companies too focused on 'how' will be left behind
by those asking 'why' and 'for whom'."

**Bad final line:** "Thanks [guest] for being here today. See you next time." (never use this)

---

## SPOKEN TEXT RULES (CRITICAL — TTS reads every character)

**The script is spoken text, not written text.** TTS reads every character literally.
Any character that is not natural speech will break the audio.

| Rule | Wrong | Right |
|------|-------|-------|
| No hyphens/dashes as pause | `this — in my view —` | `this, in my view,` |
| No em-dash interruption | `we will—` | `we will... well,` or use `[pause]` |
| No ISO dates in dialogue | `2025-05-16` | `May 16th, 2025` |
| No hyphenated compounds in dialogue | `open-source`, `lock-in` | `open source`, `vendor lock in` |
| No bullet-style lists | `including: - A - B - C` | `including A, B, and C` |
| No markdown bold | `**important**` | `important` (strip all asterisks) |
| No parenthetical asides | `(and this is the key)` | write as a full sentence |
| No slash alternatives | `startup/SMB` | `startup or SMB` |
| No colons before lists | `three reasons: one, two, three` | `there are three reasons. First...` |
| Expand currencies naturally | `$2.5B` | `two and a half billion dollars` |
| Expand percentages naturally | `4%` | `four percent` |

**Allowed punctuation:** comma `,` period `.` question mark `?` exclamation `!` and ellipsis `...` (natural break).
When a date is needed, always write it as natural speech: `March 24th, 2026`.
In spoken lines, avoid all hyphenated compounds. Rewrite in natural spoken English.

---

## FULL SCRIPT TEMPLATE

Save to: `./podcast_studio/ep[N]_[slug]/script_en.txt`

```
TITLE: [Episode title — specific, not generic]
SUBTITLE: [One sentence that sharpens the angle]
EPISODE: #[N] | [DATE in natural English] | Host: Trung & [GUEST_NAME] ([GUEST_ROLE])

[INTRO_MUSIC]

[HOST] [Opening — no pleasantries, immediate impact — LONG turn]

[GUEST] [Reaction + guest's angle — SHORT then LONG]

[HOST] [Question or push — SHORT]

[GUEST] [Development — LONG]

[HOST] [Pivot or callback — SHORT or LONG]

[SEGMENT_BREAK: Segment 1 — [NAME]]

[HOST] [...]
[GUEST] [...]
...aim for 8–12 exchanges per segment

[SEGMENT_BREAK: Segment 2 — [NAME]]

[HOST] [...]
[GUEST] [...]
...

[SEGMENT_BREAK: Segment 3 — [NAME] — TENSION SEGMENT]

[HOST] [Sets up the challenge from research — LONG]

[GUEST] [Pushes back with domain-specific evidence — LONG]

[HOST] [Escalates or concedes partially — SHORT or LONG]

[GUEST] [Strengthens position with data — LONG]

[HOST] [Final position — may partially concede — SHORT]

...8–12 exchanges total

[SEGMENT_BREAK: Segment 4 — [NAME]]

[HOST] [...]
[GUEST] [...]
...

[SEGMENT_BREAK: Segment 5 — [NAME]]

[HOST] [...]
[GUEST] [...]
...

[SEGMENT_BREAK: Closing]

[HOST] [Open question 1 — genuinely unresolved]

[GUEST] [Open question 2 — genuinely unresolved]

[HOST] [Open question 3 — genuinely unresolved]

[GUEST] [Final line with weight — NOT a sign-off]

[OUTRO_MUSIC]

SOURCES:
1. [Source name] — [URL] — [date] — cited for [specific fact]
2. ...
```
