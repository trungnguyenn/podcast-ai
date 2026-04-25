# Tech Radar — Vietnamese Translation Notes

Reference for translating the English script (`script_en.txt`) into natural spoken
Vietnamese (`script_vi.txt`). This is NOT a word-for-word translation guide. The goal
is a script that sounds like two Vietnamese professionals having a real conversation,
not a dubbed English podcast.

**CRITICAL: All Vietnamese text MUST use proper diacritical marks (có dấu).
TTS engines require full diacritics to pronounce Vietnamese correctly.
Never write "khong dau" (unaccented) Vietnamese — it will produce gibberish audio.**

---

## CORE PRINCIPLE

Translate for **spoken Vietnamese**, not written Vietnamese. Every line will be read
aloud by a TTS engine. If it would sound unnatural when spoken by a real person in a
Vietnamese podcast, rewrite it.

---

## HOST PHRASE PALETTE (Trung)

These are natural Vietnamese equivalents for the HOST's characteristic moves.
Rotate them — never repeat the same opener more than once per script.

```
"Tôi muốn nói thẳng..."
"Thành thật mà nói..."
"Nói ngắn gọn thì..."
"Nếu bóc hết lớp PR ra thì..."
"Điều làm tôi lăn tăn là..."
"Chỗ này tôi hơi khó tính một chút..."
"Nói công bằng thì..."
"Điều đáng bàn hơn là..."
"Nếu nhìn như một người làm business thì..."
"Tôi không hoàn toàn bị thuyết phục ở điểm này."
"Đây là phép tính khó chịu:"
"Câu hỏi không ai muốn hỏi là..."
"Hãy thành thật về điều này:"
"Thật ra, [admission of complexity]."
```

**Opening patterns:**
- Fact: "Một con số: [X từ research]. Hãy dừng lại và nghĩ về điều đó."
- Claim: "Tập này khác với mọi tập trước. [Specific reason why]."
- Scene: "Tuần này, [specific company or event] đã [specific action]. Đó là điểm xuất phát."
- Question: "Câu hỏi tôi muốn đặt ngay từ đầu: [question with no easy answer]."

---

## GUEST PHRASE PALETTE

Natural Vietnamese phrasing for the GUEST persona. Adapt based on guest role.

```
"Con số thực tế là..."
"Nếu nhìn từ dữ liệu thì..."
"Điểm này quan trọng hơn nó nghe có vẻ..."
"Cái tinh tế nằm ở chỗ..."
"Tôi nghĩ cần tách hai lớp vấn đề ở đây:"
"Nếu đã từng triển khai thực tế, mọi người sẽ thấy..."
"Nhưng có số liệu cụ thể tôi muốn nhấn mạnh:"
"Để tôi giải thích tại sao điều này quan trọng trong lĩnh vực [domain] thực tế:"
"Chúng tôi đã thử rồi. Kết quả là..."
"Anh thấy điều đó ở phía business không?"
```

**Guest question patterns (minimum 3 per episode):**
```
"Anh thấy điều này ở phía business không?"
"Theo anh, cái gì sẽ xảy ra với [X] trong 2 năm tới?"
"Anh có biết ví dụ nào của company làm điều này không?"
"Điều đó có làm anh lo lắng về [Y] không?"
"Anh nghĩ pricing model sẽ thay đổi như thế nào?"
```

---

## REACTION PHRASES

Short acknowledgement turns before developing a point. 1 sentence max.

```
"Đúng vậy."
"Hay đó."
"Ồ, thú vị đấy."
"Uh, chính xác."
"Hợp lý."
"Tôi hiểu ý anh."
"Chỗ này đang nói lên rất nhiều điều."
"Và đây là điều khó xử:"
"Okay, để tôi nhìn nhận lại điều này..."
"[cười nhẹ] Thật ra..."
"Tôi cũng nghĩ vậy, nhưng..."
"Anh vừa chạm đúng điểm tôi muốn nói."
```

---

## CALLBACK PATTERNS

Reference earlier points to create conversational coherence.

```
"Nhớ cái số liệu anh vừa nói, [X], đây là nơi nó liên kết với security."
"Quay lại cái case study [Company] lúc nãy, họ đã giải quyết vấn đề đó như thế nào?"
"Đây chính xác là cái 'phép tính khó chịu' anh nói ở đầu tập."
"Ấy, mà anh vừa tự mâu thuẫn một chút, lúc trước anh nói [X], giờ anh nói [Y]."
```

---

## TONE CUE MARKERS (Vietnamese equivalents)

When translating tone cues from the English script, use these Vietnamese markers:

| English marker | Vietnamese marker | Meaning |
|---------------|-------------------|---------|
| `[laugh]` | `[cười nhẹ]` | Light, self-aware laughter |
| `[pause]` | `[dừng lại]` | Thoughtful pause before important point |
| `[serious]` | `[nghiêm túc]` | Shift to serious register |
| `[energetic]` | `[năng động]` | Upbeat, energetic delivery |
| `[reflective]` | `[khẽ gật đầu]` | Quiet, reflective tone |

---

## TECHNICAL TERM ADAPTATION

Vietnamese podcast dialogue should prioritize speakable Vietnamese. Only keep English
when the term is a proper noun, widely-known acronym, or has no natural Vietnamese
equivalent.

| Category | Rule | Example |
|----------|------|---------|
| Primary language | Vietnamese | all dialogue |
| Technical terms | Prefer speakable Vietnamese; keep English only for proper nouns or common acronyms | "luồng công việc của agent", "MCP server", "SOC 2" |
| Company/product names | Keep English | "Anthropic", "Claude Code", "GitHub" |
| Monetary amounts | Write as spoken Vietnamese | "1 tỷ đô la Mỹ", not "1 billion USD" |
| Acronyms (first mention) | Spell out or convert to spoken form | "MCP", "SOC 2", "API" |
| Numbers | Prefer spoken form | "78 phần trăm" is better than "78%" |

**Common adaptations:**

| English | Vietnamese (spoken) |
|---------|-------------------|
| open source | mã nguồn mở |
| vendor lock-in | bị khóa vào nhà cung cấp |
| non-developer | người không chuyên code |
| workflow | luồng công việc |
| monthly downloads | lượt tải mỗi tháng |
| tool poisoning | đầu độc công cụ |
| workflow coherence | độ liền mạch của luồng công việc |
| use case | trường hợp sử dụng |
| trade-off | đánh đổi |
| bottleneck | nút thắt cổ chai |
| stakeholder | bên liên quan |
| fine-tuning | điều chỉnh tinh |
| inference | suy luận |
| deployment | triển khai |
| self-hosted | tự host / tự triển khai |
| enterprise | doanh nghiệp lớn |
| benchmark | bài kiểm thử / chuẩn đánh giá |

---

## SPOKEN TEXT RULES (CRITICAL for TTS)

Vietnamese script is spoken text. TTS reads every character literally.

| Rule | Wrong | Right |
|------|-------|-------|
| No hyphens/dashes as pause | `điều này — theo tôi —` | `điều này, theo tôi,` |
| No em-dash interruption | `chúng ta sẽ—` | `chúng ta sẽ... à,` or use `[dừng lại]` |
| No ISO dates | `2025-05-16` | `ngày 16 tháng 5 năm 2025` |
| No hyphenated compounds | `open-source`, `lock-in` | `mã nguồn mở`, `bị khóa vào` |
| No bullet-style lists | `gồm: - A - B - C` | `gồm A, B, và C` |
| No markdown bold | `**điều quan trọng**` | `điều quan trọng` |
| No parenthetical asides | `(và đây là điểm mấu chốt)` | write as full sentence |
| No slash alternatives | `startup/SMB` | `startup hay SMB` |
| No colons before lists | `ba lý do: một, hai, ba` | `có ba lý do. Thứ nhất...` |
| Expand currencies | `2.5 tỷ USD` | `2,5 tỷ đô la Mỹ` |
| Expand percentages | `4%` | `4 phần trăm` |

**Allowed punctuation:** comma `,` period `.` question mark `?` exclamation `!` and
ellipsis `...` (natural break).

Dates must use spoken Vietnamese form: `ngày 24 tháng 3 năm 2026`.

---

## THOUGHT INTERRUPTION (Vietnamese style)

Do NOT use dashes. TTS will read them as "gạch ngang". Use natural speech instead:

```
[HOST] Và nếu điều đó đúng, thì mô hình kinh doanh của các công ty dịch vụ phần mềm...

[GUEST] Sẽ bị đảo lộn hoàn toàn. Chính xác. Đây là điều chúng tôi đang thấy ở...
```

Or with a transition phrase:

```
[HOST] Và nếu điều đó đúng, ý tôi muốn nói là...

[GUEST] Là toàn bộ pricing model sẽ thay đổi. Đúng. Và đây là điều chúng tôi đang thấy.
```

---

## DISAGREEMENT PATTERNS (Vietnamese)

Strong disagreements with evidence, adapted for Vietnamese conversational register:

```
[HOST] Theo McKinsey, AI có thể tự động hóa 30 phần trăm công việc của developers. Nếu điều
đó đúng, chúng ta đang nói đến cắt giảm nhân lực ở quy mô lớn.

[GUEST] Tôi muốn phản biện mạnh vào con số đó. McKinsey đo lường các nhiệm vụ có thể tự động
hóa, không phải các vị trí công việc có thể tự động hóa. Theo dữ liệu từ GitHub, họ có hơn
100 triệu developers trên platform, năng suất tăng nhưng số nhân viên không giảm. Hiện tại,
chưa có bằng chứng rõ ràng cho việc thay thế việc làm ở quy mô đó.

[HOST] Điểm hợp lý. Nhưng vấn đề là độ trễ, có lẽ chúng ta chưa đến đó thời điểm đó?

[GUEST] Có thể. Nhưng tôi cũng nói: ở healthcare IT, chúng tôi đang thuê thêm engineers vì
AI tạo ra công việc mới, không giảm bao nhiêu. Đây có phải là bằng chứng chứng minh anh sai
không? [cười nhẹ] Tôi chưa chắc.
```

---

## OPENING AND CLOSING (Vietnamese)

**Never use:** "Xin chào", "Chào mừng các bạn", "Hôm nay chúng ta sẽ...",
"Cảm ơn bạn đã lắng nghe", "Cảm ơn và hẹn gặp lại".

**Good closing question:** "Khi AI tăng năng suất 3 lần, pricing model của các công ty dịch
vụ phần mềm sẽ thay đổi thế nào, và ai sẽ nắm bắt giá trị đó?"

**Good final line:** "Có một thứ chắc chắn: các công ty quá tập trung vào 'làm thế nào'
sẽ bị để lại phía sau bởi những công ty đang hỏi 'tại sao' và 'cho ai'."

---

## TRANSLATION WORKFLOW

1. Read the English `script_en.txt` segment by segment.
2. For each `[HOST]` or `[GUEST]` line, translate the meaning, not the words.
3. Apply Vietnamese phrase palettes where they fit naturally.
4. Adapt technical terms per the table above.
5. Convert all dates, currencies, and percentages to spoken Vietnamese form.
6. Replace English tone cues with Vietnamese equivalents.
7. Preserve all structural markers (`[INTRO_MUSIC]`, `[SEGMENT_BREAK: ...]`, etc.) exactly.
8. Preserve the same number of turns and same speaker order as the English original.
9. Run the TTS safety check: no dashes, no bold, no markdown in spoken lines.
10. **VERIFY: All Vietnamese text uses proper diacritical marks (có dấu). Zero tolerance for unaccented text.**
