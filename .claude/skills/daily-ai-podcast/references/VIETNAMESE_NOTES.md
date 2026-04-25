# AI Daily — Vietnamese Translation Notes

Solo monologue format. Every spoken line belongs to `[HOST]` only.
Adapts from Tech Radar's Vietnamese guide for the daily briefing context.

**Core principle:** Translate for spoken delivery by a solo anchor who is sharp,
analytical, and treats the listener as a busy professional who needs to act,
not just to know.

---

## HOST PHRASE PALETTE (Daily Anchor Mode)

Rotate — never use the same opener twice in the same episode.

**Opening patterns:**
```
"Một con số: [X]. Đây là cách ngày [DATE] bắt đầu trong ngành AI."
"Có ba thứ xảy ra trong 24 giờ qua mà bạn cần biết."
"Tin đầu tiên, và theo tôi là quan trọng nhất:"
"Hôm nay là một trong những ngày bận rộn nhất ngành AI từ đầu năm."
"Thành thật mà nói về những tin này:"
"Nếu bỏ qua tất cả PR đi, điều đang thực sự xảy ra là:"
"Đây là điều mà nhiều người bỏ lỡ trong tin này:"
"Câu hỏi thực sự ở đây là:"
"Tác động trực tiếp đối với manager và builder:"
"Tôi muốn đưa ra một góc nhìn ngược lại:"
"Đây là tín hiệu, không phải sự kiện:"
"Trong 30 ngày tới, điều này nghĩa là:"
"Dữ liệu chưa đủ để kết luận, nhưng tín hiệu cho thấy:"
"Nếu bạn đang [situation], câu hỏi không còn là [X] mà là [Y]."
```

**Transition phrases between stories:**
```
"Và điều đó dẫn thẳng vào tin tiếp theo."
"Tin thứ hai, và nó liên quan đến điều vừa nói:"
"Bây giờ sang góc độ khác của cùng một làn sóng:"
"Chuyển qua tin số [N]:"
```

**Pattern-naming openers (for analysis segment):**
```
"Nhìn lại ba tin hôm nay, có một mẫu chung:"
"Cái tôi thấy xuyên suốt ngày hôm nay là:"
"Nếu phải đặt tên cho ngày hôm nay, tôi sẽ gọi nó là: [theme]."
"Ba tin, ba công ty khác nhau, nhưng một tín hiệu:"
```

**Decision-framing openers:**
```
"Câu hỏi cho manager tuần này là:"
"Với người đang build:"
"Nếu bạn là engineering manager đang cân nhắc [X], đây là cách tôi nhìn nhận:"
"Điều này không trừu tượng. Nó nghĩa là:"
```

**Uncertainty signals:**
```
"Dữ liệu chưa đủ để kết luận, nhưng tín hiệu cho thấy:"
"Điều chúng ta chưa biết là:"
"Cần thêm vài tuần để thấy rõ hơn, nhưng hiện tại:"
"Tôi không chắc về [X], nhưng về [Y] tôi khá tự tin:"
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
| stakeholder | bên liên quan |
| self-hosted | tự host / tự triển khai |
| API pricing | giá API |
| data residency | lưu trữ dữ liệu nội địa |
| enterprise | doanh nghiệp lớn |
| startup ecosystem | hệ sinh thái startup |
| funding round | vòng gọi vốn |
| Series A/B/C | Series A / Series B / Series C |
| commoditize | trở thành hàng hóa phổ thông |
| go-to-market | chiến lược tiếp cận thị trường |
| build vs buy | tự xây hay mua |

**Proper nouns — keep English as-is:**
Company names, product names, model names, acronyms (LLM, API, MCP, SOC 2, GPU).

**First mention of acronyms:** spell out in full, then use the acronym.
"Large Language Model, gọi tắt là LLM"

---

## SPOKEN TEXT RULES (CRITICAL for TTS)

TTS reads every character literally. These rules are non-negotiable.

| Rule | Wrong | Right |
|------|-------|-------|
| No dashes as pause | `điều này — theo tôi —` | `điều này, theo tôi,` |
| No em-dash | `chúng ta sẽ—` | `chúng ta sẽ... à,` |
| No ISO dates | `2026-04-03` | `ngày 3 tháng 4 năm 2026` |
| No hyphenated tech terms | `open-source`, `fine-tuning` | `mã nguồn mở`, `điều chỉnh tinh` |
| No bullet lists in speech | `gồm: - A - B` | `gồm A, B, và C` |
| No markdown bold | `**quan trọng**` | `quan trọng` |
| No parenthetical asides | `(và đây là điểm mấu chốt)` | write as full sentence |
| No slash alternatives | `startup/SMB` | `startup hay SMB` |
| Expand currencies | `2.5B USD` | `hai tỷ rưỡi đô la Mỹ` |
| Expand percentages | `44%` | `44 phần trăm` |
| Spoken date form | `Q1 2026` | `quý 1 năm 2026` |
| No colons before lists | `ba lý do: một, hai, ba` | `có ba lý do. Thứ nhất...` |

**Allowed punctuation:** `,` `.` `?` `!` `...`

---

## MONOLOGUE FLOW TECHNIQUES

Since there is no guest, vary rhythm by these techniques:

**Self-questioning:**
```
"Câu hỏi là: tại sao bây giờ? Câu trả lời nằm ở..."
"Bạn có thể hỏi: có phải đây chỉ là marketing không? Câu trả lời ngắn gọn là không."
```

**Rhetorical contrast:**
```
"Tuần trước, câu hỏi là [X]. Hôm nay, câu trả lời bắt đầu hiện ra."
"Nhìn bề mặt thì đây là [X]. Nhưng nếu đào sâu hơn một chút:"
```

**Layered analysis:**
```
"Có hai lớp vấn đề ở đây. Lớp đầu tiên là [technical]. Lớp thứ hai, và quan trọng hơn, là [strategic]."
```

**Forward-reference:**
```
"Tôi sẽ quay lại điểm này trong phần phân tích, nhưng trước tiên:"
"Giữ con số đó trong đầu, chúng ta sẽ cần nó."
```

---

## OPENING AND CLOSING (Vietnamese)

**Never write:**
- "Xin chào các bạn"
- "Chào mừng đến với AI Daily"
- "Hôm nay chúng ta sẽ nói về"
- "Cảm ơn đã lắng nghe"
- "Hẹn gặp lại ngày mai"

**Good opening examples:**
```
"Một con số: 400 triệu lượt tải. Google công bố con số đó cho Gemma hôm qua. Hãy dừng lại và nghĩ về điều đó."

"Ngày hôm nay có ba tin mà nếu bỏ qua, bạn sẽ mất một tuần để bắt kịp."

"Tuần này, Microsoft, Google, và OpenAI đồng loạt đưa ra những bước đi mà... chúng không chỉ là cạnh tranh. Đây là tái định hình ngành."
```

**Good closing questions:**
```
"Khi infrastructure AI trở thành commodity, ai thực sự nắm giữ giá trị?"
"Nếu 40 phần trăm tác vụ kỹ thuật có thể được tự động hóa vào cuối năm 2026, bài toán nhân lực nào sẽ buộc các công ty phải giải quyết ngay bây giờ?"
"Open models và proprietary APIs đang hội tụ về cùng một điểm. Câu hỏi là: hội tụ ở đâu, và ai kiểm soát điểm đó?"
```

**Good final lines (resonant close, no sign-off):**
```
"Thứ duy nhất chắc chắn hôm nay: tốc độ thay đổi đang nhanh hơn tốc độ ra quyết định. Nhiệm vụ của bạn là thu hẹp khoảng cách đó."

"Trong AI, người hành động sớm và sai ít thiệt hại hơn người chờ đợi hoàn hảo. Đó là bài học từ 24 giờ vừa qua."

"Ngày mai sẽ có thêm tin mới. Nhưng câu hỏi từ hôm nay sẽ không biến mất."
```

---

## TRANSLATION WORKFLOW

1. Read `script_en.txt` segment by segment.
2. Translate meaning, not words. Aim for what a Vietnamese anchor would actually say.
3. Apply Vietnamese phrase palettes where they fit naturally.
4. Adapt technical terms per the table above.
5. Convert all dates, currencies, and percentages to spoken Vietnamese form.
6. Preserve all structural markers (`[INTRO_MUSIC]`, `[SEGMENT_BREAK: ...]`, `[OUTRO_MUSIC]`) exactly.
7. Keep the same number of `[HOST]` turns as the English original.
8. Run TTS safety check: no dashes, no bold, no markdown in spoken lines.
9. Verify word count ≥ 3,600 before finalizing.
