# AI Weekly Radar — Vietnamese Translation Notes

Two-host dialogue format. Every spoken line belongs to either `[HOST]` or `[GUEST]`.
Both voices speak natural Southern Vietnamese, but with distinct registers.

**Core principle:** Translate for spoken delivery by two professionals having a real conversation.
Trung sounds like a sharp anchor who grew up in the Mekong Delta. An sounds like a
senior analyst who is warm, precise, and occasionally willing to say the uncomfortable truth.
Neither sounds like they are reading a script.

---

## THE TWO VOICES IN VIETNAMESE

### Trung (HOST) — Anchor register

- Short questions: "Em nghĩ sao?", "Thật không?", "Tại sao vậy?", "Nói thêm đi."
- Names the frame first: "Cái này có nghĩa là...", "Vấn đề thực sự là..."
- Deploys miền Tây metaphors at the right moment — not every sentence, but when they land:
  - "Nghe như mình đang vét mương trước mùa mưa"
  - "Chơi chợ thì coi màu cá, mở vựa thì coi kho lạnh"
  - "Đừng ham cá rẻ mà quên tiền đá lạnh"
  - "Ghe máy tốt mà xăng không đều, ra giữa sông là giật cục"
  - "Nước có lớn cỡ nào thì xuồng nào buộc dây chắc vẫn đi xa"
- Signals disagreement warmly: "Anh không chắc lắm với điểm đó.", "Có người sẽ phản biện rằng..."
- Closes with decision frame: "Vậy anh em manager cần làm gì với thông tin này?"

### An (GUEST) — Analyst register

- Opens with agreement signal before extending: "Chuẩn.", "Đúng.", "Đúng bài luôn."
- Leads with evidence: "Con số em thấy là...", "Theo [source], thì..."
- Layers analysis: "Có hai lớp ở đây. Lớp đầu là... Lớp thứ hai, quan trọng hơn, là..."
- Names winners and losers explicitly: "Ai được lợi từ đây:", "Ai phải lo:"
- Gives direct advice: "Với builder đang build X:", "Nếu bạn là manager đang cân nhắc Y:"
- Signals honest uncertainty: "Dữ liệu chưa đủ để kết luận, nhưng tín hiệu cho thấy..."
- Avoids hedging to be polite: says "sai" or "không đúng" when something is clearly wrong,
  then explains why without softening the core claim

---

## HOST PHRASE PALETTE (weekly dialogue mode)

Rotate — never use the same opener twice in the same episode.

**Opening a story:**
```
"Con số của tuần này:"
"Tin đầu tiên, và theo anh là quan trọng nhất:"
"Thành thật mà nói về tin này:"
"Nếu bỏ qua tất cả PR đi, điều đang thực sự xảy ra là:"
"Đây là điều mà nhiều người bỏ lỡ trong tin này:"
```

**Pushing back:**
```
"Nhưng câu hỏi thực sự là:"
"Có người sẽ phản biện rằng [X]. Em nghĩ sao?"
"Bạn có chắc không, hay là đang lạc quan hơi nhiều?"
"Nghe thuyết phục, nhưng anh muốn challenge một điểm:"
"Vậy tại sao nhiều người vẫn chưa làm điều này?"
```

**Transitions between stories:**
```
"Và điều đó dẫn thẳng vào tin tiếp theo."
"Tin thứ [N], và nó liên quan đến điều vừa nói:"
"Bây giờ sang góc độ khác của cùng làn sóng:"
"Chuyển qua tin số [N]:"
```

**Opening analysis segment:**
```
"Nhìn lại [N] tin tuần này, có một mẫu chung:"
"Cái anh thấy xuyên suốt tuần này là:"
"Nếu phải đặt tên cho tuần này, anh sẽ gọi là: [theme]."
"Ba tin, ba công ty khác nhau, nhưng một tín hiệu:"
```

**Decision framing:**
```
"Câu hỏi cho manager tuần này là:"
"Với người đang build:"
"Nếu bạn là engineering manager đang cân nhắc [X], đây là cách anh nhìn nhận:"
"Điều này không trừu tượng. Nó nghĩa là:"
```

**Uncertainty signals:**
```
"Dữ liệu chưa đủ để kết luận, nhưng tín hiệu cho thấy:"
"Điều chúng ta chưa biết là:"
"Anh không chắc về [X], nhưng về [Y] anh khá tự tin:"
```

---

## TECHNICAL TERM ADAPTATION

| English | Vietnamese (spoken) |
|---------|---------------------|
| open source / open-source | mã nguồn mở |
| fine-tuning / fine-tune | điều chỉnh tinh |
| inference | suy luận |
| model weights | trọng số mô hình |
| benchmark | bài kiểm thử / chuẩn đánh giá |
| deployment | triển khai |
| vendor lock-in | bị khóa vào nhà cung cấp |
| workflow | luồng công việc |
| use case | trường hợp sử dụng |
| trade-off | đánh đổi |
| bottleneck | nút thắt cổ chai |
| self-hosted | tự host / tự triển khai |
| API pricing | giá API |
| data residency | lưu trữ dữ liệu nội địa |
| enterprise | doanh nghiệp lớn |
| funding round | vòng gọi vốn |
| commoditize | trở thành hàng hóa phổ thông |
| build vs buy | tự xây hay mua |
| shadow agent | agent ngầm / agent không được kiểm soát |
| agentic identity | danh tính agent |
| governance | quản trị |
| audit trail | nhật ký kiểm toán |
| least privilege | quyền hạn tối thiểu |
| instruction hierarchy | thứ bậc chỉ dẫn |
| context compaction | nén ngữ cảnh |
| verification gate | cổng kiểm chứng |
| fallback provider | nhà cung cấp dự phòng |
| human-in-the-loop | có sự tham gia của con người |
| cost per deliverable | chi phí theo kết quả bàn giao |
| rework rate | tỷ lệ làm lại |

**Proper nouns — keep English as-is:**
Company names, product names, model names, acronyms (LLM, API, MCP, SOC 2, GPU, IAM, CI, DevOps).

**First mention of acronyms:** spell out in full, then use the acronym.
"Identity and Access Management, gọi tắt là IAM"

---

## SPOKEN TEXT RULES (CRITICAL for TTS)

TTS reads every character literally. These rules are non-negotiable for both HOST and GUEST lines.

| Rule | Wrong | Right |
|------|-------|-------|
| No dashes as pause | `điều này — theo tôi —` | `điều này, theo tôi,` |
| No em-dash | `chúng ta sẽ—` | `chúng ta sẽ... à,` |
| No ISO dates | `2026-04-06` | `ngày 6 tháng 4 năm 2026` |
| No hyphenated tech terms | `open-source`, `fine-tuning`, `low-code` | `mã nguồn mở`, `điều chỉnh tinh`, `low code` |
| No bullet lists in speech | `gồm: - A - B` | `gồm A, B, và C` |
| No markdown bold | `**quan trọng**` | `quan trọng` |
| No parenthetical asides | `(và đây là điểm mấu chốt)` | write as a full sentence |
| No slash alternatives | `startup/SMB` | `startup hay SMB` |
| Expand currencies | `2.5B USD` | `hai tỷ rưỡi đô la Mỹ` |
| Expand percentages | `44%` | `44 phần trăm` |
| Spoken date form | `Q2 2026` | `quý 2 năm 2026` |
| No colons before lists | `ba lý do: một, hai, ba` | `có ba lý do. Thứ nhất...` |

**Allowed punctuation:** `,` `.` `?` `!` `...`

---

## DIALOGUE FLOW TECHNIQUES

Since there are two speakers, use these techniques to create natural rhythm:

**Confirmation before extension (An's signature move):**
```
"Chuẩn. Và điều em muốn thêm là..."
"Đúng bài luôn. Còn một góc nữa là..."
"Đúng. Và đây là tại sao điều đó quan trọng hơn nhiều người nghĩ:"
```

**Self-questioning (Trung's thinking-aloud style):**
```
"Câu hỏi là: tại sao bây giờ? Câu trả lời nằm ở..."
"Bạn có thể hỏi: có phải chỉ là marketing không? Câu trả lời ngắn gọn là không."
```

**Rhetorical contrast (either speaker):**
```
"Tuần trước, câu hỏi là [X]. Tuần này, câu trả lời bắt đầu hiện ra."
"Nhìn bề mặt thì đây là [X]. Nhưng nếu đào sâu hơn một chút:"
```

**Layered analysis (An's signature move):**
```
"Có hai lớp vấn đề ở đây. Lớp đầu tiên là [technical/immediate]. Lớp thứ hai, và quan trọng hơn, là [strategic/structural]."
```

**Warm disagreement between hosts:**
```
[HOST]: "Anh không hoàn toàn đồng ý điểm đó. Vì..."
[GUEST]: "Anh nói có lý ở điểm [X]. Nhưng em giữ rằng [Y] vì..."
```

---

## OPENING AND CLOSING (Vietnamese)

**Never write:**
- "Xin chào các bạn"
- "Chào mừng đến với AI Weekly Radar"
- "Hôm nay chúng ta sẽ nói về"
- "Cảm ơn đã lắng nghe"
- "Hẹn gặp lại tuần sau"
- Any version of "see you next week" or a sign-off

**Good cold opens (HOST line, before any GUEST line):**
```
"Con số của tuần này: [X]. Đây là cách tuần từ [date] tới [date] bắt đầu trong ngành AI."

"Tuần này không phải tuần yên tĩnh. Và điều làm anh chú ý không phải là cái ồn ào nhất."

"Nếu phải chọn một từ để mô tả tuần AI vừa qua, anh sẽ chọn: [word]. Em có đồng ý không?"

"Ba thứ xảy ra tuần này. Nhìn riêng lẻ thì không đáng kể. Nhìn chung thì là tín hiệu lớn."
```

**Good closing questions (3 consecutive HOST lines):**
```
"Câu một: khi lớp model AI trở thành hàng hóa, ai nắm giữ thực sự giá trị của ngành?"
"Câu hai: nếu tốc độ thay đổi trong 90 ngày tới bằng tốc độ 90 ngày vừa qua, bài toán nào sẽ buộc các công ty phải giải quyết mà họ chưa chuẩn bị?"
"Câu ba: open models và proprietary APIs đang hội tụ. Câu hỏi là hội tụ ở đâu, và ai kiểm soát điểm đó?"
```

**Good final HOST lines (resonant close, no sign-off):**
```
"Tuần tới sẽ có thêm tin mới. Nhưng câu hỏi từ tuần này sẽ không biến mất."

"Tốc độ thay đổi nhanh hơn tốc độ ra quyết định. Nhiệm vụ của bạn là thu hẹp khoảng cách đó."

"Trong AI, kẻ thắng không phải người đi nhanh nhất. Mà là người biết dừng đúng lúc để nhìn bản đồ."

"Nước có lớn cỡ nào thì xuồng nào buộc dây chắc, biết coi con nước, xuồng đó đi xa."
```

---

## TRANSLATION WORKFLOW

1. Read `script_en.txt` segment by segment.
2. Translate meaning, not words. Ask: what would Trung and An actually say in Vietnamese?
3. Apply the two-voice registers: Trung's warm-anchor style, An's evidence-anchored analyst style.
4. Apply Vietnamese phrase palettes where they fit naturally.
5. Adapt technical terms per the table above.
6. Convert all dates, currencies, and percentages to spoken Vietnamese form.
7. Preserve all structural markers (`[INTRO_MUSIC]`, `[SEGMENT_BREAK: ...]`, `[OUTRO_MUSIC]`) exactly.
8. Keep the same number of `[HOST]` and `[GUEST]` turns as the English original.
9. Run TTS safety check: no dashes, no bold, no markdown in spoken lines.
10. Verify: spoken words ≥ 8,500 and GUEST share ≥ 40% before finalizing.

**Important:** Vietnamese naturally expands vs English by 10–20% in word count.
This expansion is desirable — it fills the 40-45 min audio target. Do not compress.
