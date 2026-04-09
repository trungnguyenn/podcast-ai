# Tech Radar — Vietnamese Translation Notes

Reference for translating the English script (`script_en.txt`) into natural spoken
Vietnamese (`script_vi.txt`). This is NOT a word-for-word translation guide. The goal
is a script that sounds like two Vietnamese professionals having a real conversation,
not a dubbed English podcast.

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
"Toi muon noi thang..."
"Thanh that ma noi..."
"Noi ngan gon thi..."
"Neu boc het lop PR ra thi..."
"Dieu lam toi lan tan la..."
"Cho nay toi hoi kho tinh mot chut..."
"Noi cong bang thi..."
"Dieu dang ban hon la..."
"Neu nhin nhu mot nguoi lam business thi..."
"Toi khong hoan toan bi thuyet phuc o diem nay."
"Day la phep tinh kho chiu:"
"Cau hoi khong ai muon hoi la..."
"Hay thanh that ve dieu nay:"
"That ra, [admission of complexity]."
```

**Opening patterns:**
- Fact: "Mot con so: [X tu research]. Hay dung lai va nghi ve dieu do."
- Claim: "Tap nay khac voi moi tap truoc. [Specific reason why]."
- Scene: "Tuan nay, [specific company or event] da [specific action]. Do la diem xuat phat."
- Question: "Cau hoi toi muon dat ngay tu dau: [question with no easy answer]."

---

## GUEST PHRASE PALETTE

Natural Vietnamese phrasing for the GUEST persona. Adapt based on guest role.

```
"Con so thuc te la..."
"Neu nhin tu du lieu thi..."
"Diem nay quan trong hon no nghe co ve..."
"Cai tinh te nam o cho..."
"Toi nghi can tach hai lop van de o day:"
"Neu da tung trien khai thuc te, moi nguoi se thay..."
"Nhung co so lieu cu the toi muon nhan manh:"
"De toi giai thich tai sao dieu nay quan trong trong linh vuc [domain] thuc te:"
"Chung toi da thu roi. Ket qua la..."
"Anh thay dieu do o phia business khong?"
```

**Guest question patterns (minimum 3 per episode):**
```
"Anh thay dieu nay o phia business khong?"
"Theo anh, cai gi se xay ra voi [X] trong 2 nam toi?"
"Anh co biet vi du nao cua company lam dieu nay khong?"
"Dieu do co lam anh lo lang ve [Y] khong?"
"Anh nghi pricing model se thay doi nhu the nao?"
```

---

## REACTION PHRASES

Short acknowledgement turns before developing a point. 1 sentence max.

```
"Dung vay."
"Hay do."
"O, thu vi day."
"Uh, chinh xac."
"Hop ly."
"Toi hieu y anh."
"Cho nay dang noi len rat nhieu dieu."
"Va day la dieu kho xu:"
"Okay, de toi nhin nhan lai dieu nay..."
"[cuoi nhe] That ra..."
"Toi cung nghi vay, nhung..."
"Anh vua cham dung diem toi muon noi."
```

---

## CALLBACK PATTERNS

Reference earlier points to create conversational coherence.

```
"Nho cai so lieu anh vua noi, [X], day la noi no lien ket voi security."
"Quay lai cai case study [Company] luc nay, ho da giai quyet van de do nhu the nao?"
"Day chinh xac la cai 'phep tinh kho chiu' anh noi o dau tap."
"Ay, ma anh vua tu mau thuan mot chut, luc truoc anh noi [X], gio anh noi [Y]."
```

---

## TONE CUE MARKERS (Vietnamese equivalents)

When translating tone cues from the English script, use these Vietnamese markers:

| English marker | Vietnamese marker | Meaning |
|---------------|-------------------|---------|
| `[laugh]` | `[cuoi nhe]` | Light, self-aware laughter |
| `[pause]` | `[dung lai]` | Thoughtful pause before important point |
| `[serious]` | `[nghiem tuc]` | Shift to serious register |
| `[energetic]` | `[nang dong]` | Upbeat, energetic delivery |
| `[reflective]` | `[khe gat dau]` | Quiet, reflective tone |

---

## TECHNICAL TERM ADAPTATION

Vietnamese podcast dialogue should prioritize speakable Vietnamese. Only keep English
when the term is a proper noun, widely-known acronym, or has no natural Vietnamese
equivalent.

| Category | Rule | Example |
|----------|------|---------|
| Primary language | Vietnamese | all dialogue |
| Technical terms | Prefer speakable Vietnamese; keep English only for proper nouns or common acronyms | "luong cong viec cua agent", "MCP server", "SOC 2" |
| Company/product names | Keep English | "Anthropic", "Claude Code", "GitHub" |
| Monetary amounts | Write as spoken Vietnamese | "1 ty do la My", not "1 billion USD" |
| Acronyms (first mention) | Spell out or convert to spoken form | "MCP", "SOC 2", "API" |
| Numbers | Prefer spoken form | "78 phan tram" is better than "78%" |

**Common adaptations:**

| English | Vietnamese (spoken) |
|---------|-------------------|
| open source | ma nguon mo |
| vendor lock-in | bi khoa vao nha cung cap |
| non-developer | nguoi khong chuyen code |
| workflow | luong cong viec |
| monthly downloads | luot tai moi thang |
| tool poisoning | dau doc cong cu |
| workflow coherence | do lien mach cua luong cong viec |
| use case | truong hop su dung |
| trade-off | danh doi |
| bottleneck | nut that co chai |
| stakeholder | ben lien quan |

---

## SPOKEN TEXT RULES (CRITICAL for TTS)

Vietnamese script is spoken text. TTS reads every character literally.

| Rule | Wrong | Right |
|------|-------|-------|
| No hyphens/dashes as pause | `dieu nay — theo toi —` | `dieu nay, theo toi,` |
| No em-dash interruption | `chung ta se—` | `chung ta se... a,` or use `[dung lai]` |
| No ISO dates | `2025-05-16` | `ngay 16 thang 5 nam 2025` |
| No hyphenated compounds | `open-source`, `lock-in` | `ma nguon mo`, `bi khoa vao` |
| No bullet-style lists | `gom: - A - B - C` | `gom A, B, va C` |
| No markdown bold | `**dieu quan trong**` | `dieu quan trong` |
| No parenthetical asides | `(va day la diem mau chot)` | write as full sentence |
| No slash alternatives | `startup/SMB` | `startup hay SMB` |
| No colons before lists | `ba ly do: mot, hai, ba` | `co ba ly do. Thu nhat...` |
| Expand currencies | `2.5 ty USD` | `2.5 ty do la My` |
| Expand percentages | `4%` | `4 phan tram` |

**Allowed punctuation:** comma `,` period `.` question mark `?` exclamation `!` and
ellipsis `...` (natural break).

Dates must use spoken Vietnamese form: `ngay 24 thang 3 nam 2026`.

---

## THOUGHT INTERRUPTION (Vietnamese style)

Do NOT use dashes. TTS will read them as "gach ngang". Use natural speech instead:

```
[HOST] Va neu dieu do dung, thi mo hinh kinh doanh cua cac cong ty dich vu phan mem...

[GUEST] Se bi dao lon hoan toan. Chinh xac. Day la dieu chung toi dang thay o...
```

Or with a transition phrase:

```
[HOST] Va neu dieu do dung, y toi muon noi la...

[GUEST] La toan bo pricing model se thay doi. Dung. Va day la dieu chung toi dang thay.
```

---

## DISAGREEMENT PATTERNS (Vietnamese)

Strong disagreements with evidence, adapted for Vietnamese conversational register:

```
[HOST] Theo McKinsey, AI co the tu dong hoa 30 phan tram cong viec cua developers. Neu dieu
do dung, chung ta dang noi den cat giam nhan luc o quy mo lon.

[GUEST] Toi muon phan bien manh vao con so do. McKinsey do luong cac nhiem vu co the tu dong
hoa, khong phai cac vi tri cong viec co the tu dong hoa. Theo du lieu tu GitHub, ho co hon
100 trieu developers tren platform, nang suat tang nhung so nhan vien khong giam. Hien tai,
chua co bang chung ro rang cho viec thay the viec lam o quy mo do.

[HOST] Diem hop ly. Nhung van de la do tre, co le chung ta chua den do thoi diem do?

[GUEST] Co the. Nhung toi cung noi: o healthcare IT, chung toi dang thue them engineers vi
AI tao ra cong viec moi, khong giam bao nhieu. Day co phai la bang chung chung minh anh sai
khong? [cuoi nhe] Toi chua chac.
```

---

## OPENING AND CLOSING (Vietnamese)

**Never use:** "Xin chao", "Chao mung cac ban", "Hom nay chung ta se...",
"Cam on ban da lang nghe", "Cam on va hen gap lai".

**Good closing question:** "Khi AI tang nang suat 3 lan, pricing model cua cac cong ty dich
vu phan mem se thay doi the nao, va ai se nam bat gia tri do?"

**Good final line:** "Co mot thu chac chan: cac cong ty qua tap trung vao 'lam the nao'
se bi de lai phia sau boi nhung cong ty dang hoi 'tai sao' va 'cho ai'."

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
