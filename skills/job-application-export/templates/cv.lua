-- pandoc Lua filter for the Lebenslauf layout (LaTeX output only).
--
-- It changes the presentation, not the content: every word of the Markdown source stays in the output.
-- It maps the entry shapes of spec/job-application/lebenslauf/en.md to the macros of document.tex:
--   LB-4.1  "Name · Anschrift · Telefon · E-Mail"     -> \cvheader{Titel}{Name}{Label}{Kontakt}
--   LB-5.1  "### Zeitraum | Position | Arbeitgeber"    -> \cvstation{Zeitraum}{Position}{Arbeitgeber}
--   LB-5.1  "### Zeitraum | Elternzeit" (gap entry)     -> \cvstation{Zeitraum}{Elternzeit}{}
--   LB-6.1  "- Zeitraum: Inhalt" (education lists)     -> \cvrow{Zeitraum}{Inhalt}
--   LB-7    "- Gruppe: Einträge" (skills, languages)   -> the label in bold
-- A block that does not match its shape is left unchanged. The last two words of a bullet are bound with a
-- no-break space (LB-11.9); in the row and label sections this applies to the text after the label only, so
-- the binding never crosses the column or the colon.

-- Product names must not break across lines (a no-break space replaces the space). Two rules:
--   1. Heuristic: two consecutive words that both start with a capital letter, and at least one of them
--      carries an inner capital or a digit ("VMware Tanzu", "Argo CD", "GitLab CI", "Windows 11").
--   2. The document's frontmatter key `keep_together` (a list of phrases) adds names the heuristic misses,
--      for example `keep_together: [Docker Compose, Jenkins Groovy]`.
local KEEP_TOGETHER = {}
local NBSP = "\u{00A0}"

-- Sections whose list items have the shape "- Zeitraum: Inhalt" (LB-6.1) and become \cvrow lines.
local ROW_SECTIONS = {
  ["Ausbildung und Studium"] = true, ["Schulbildung"] = true,
  ["Weiterbildung und Zertifikate"] = true, ["Ehrenamt"] = true,
  ["Praktika"] = true, ["Relevante Projekte"] = true,
}
-- Sections whose list items have the shape "- Gruppe: Einträge" (LB-7); matched by prefix, so a heading
-- with a qualifier such as "Sprachkenntnisse (GER-Niveau)" is included (CG-11.2a).
local LABEL_SECTIONS = { "IT- und Fachkenntnisse", "Sprachkenntnisse" }

local function is_label_section(section)
  for _, prefix in ipairs(LABEL_SECTIONS) do
    if section == prefix or section:sub(1, #prefix + 1) == prefix .. " " then return true end
  end
  return false
end

local function starts_capital(word)
  return word:match("^[A-Z]") ~= nil or word:match("^[ÄÖÜ]") ~= nil
end

local function has_inner_capital_or_digit(word)
  return word:sub(2):match("[A-Z%d]") ~= nil
end

local function is_name_word(word)
  return word:match("^[%w%-%.]+$") ~= nil or word:match("^[ÄÖÜäöüß%w%-%.]+$") ~= nil
end

-- Heuristic rule 1 for a pair of words; trailing punctuation of the second word is ignored for the test.
local function looks_like_product_name(first, second)
  local second_core = second:gsub("[,;:.]+$", "")
  if not (is_name_word(first) and is_name_word(second_core)) then return false end
  if not (starts_capital(first) and starts_capital(second_core)) then return false end
  return has_inner_capital_or_digit(first) or has_inner_capital_or_digit(second_core)
end

-- Read `keep_together` from the frontmatter into KEEP_TOGETHER as lists of words.
local function load_keep_together(meta)
  local value = meta and meta.keep_together
  if not value then return end
  -- pandoc 3 passes a MetaList as a plain list of MetaValues (tables or strings), MetaInlines as a list of
  -- Inline elements (userdata), and a MetaString as a Lua string.
  local items = value
  local first = type(value) == "table" and value[1] or nil
  if type(value) ~= "table" or (first ~= nil and type(first) ~= "table" and type(first) ~= "string") then items = { value } end
  for _, item in ipairs(items) do
    local words = {}
    for word in pandoc.utils.stringify(item):gmatch("%S+") do words[#words + 1] = word end
    if #words >= 2 then KEEP_TOGETHER[#KEEP_TOGETHER + 1] = words end
  end
end

local function raw(s) return pandoc.RawInline("latex", s) end

local function is_space(el) return el.t == "Space" or el.t == "SoftBreak" end

local function trim(list)
  local first, last = 1, #list
  while first <= last and is_space(list[first]) do first = first + 1 end
  while last >= first and is_space(list[last]) do last = last - 1 end
  local out = {}
  for i = first, last do out[#out + 1] = list[i] end
  return out
end

-- Split a list of inlines at every Str that equals `sep`.
local function split(list, sep)
  local parts, current = {}, {}
  for _, el in ipairs(list) do
    if el.t == "Str" and el.text == sep then
      parts[#parts + 1] = trim(current)
      current = {}
    else
      current[#current + 1] = el
    end
  end
  parts[#parts + 1] = trim(current)
  return parts
end

local function append(target, list) for _, el in ipairs(list) do target[#target + 1] = el end end

-- Length of a configured phrase that starts at position i of the inline list (Str Space Str ...), or nil.
local function phrase_at(list, i)
  for _, words in ipairs(KEEP_TOGETHER) do
    local ok = true
    for k, word in ipairs(words) do
      local el = list[i + 2 * (k - 1)]
      local sep = list[i + 2 * (k - 1) - 1]
      if not el or el.t ~= "Str" or el.text ~= word or (k > 1 and (not sep or sep.t ~= "Space")) then ok = false; break end
    end
    if ok then return #words end
  end
  return nil
end

-- Replace the space inside product names by a no-break space (frontmatter phrases first, then the heuristic).
local function keep_together(list)
  local out, i = {}, 1
  while i <= #list do
    local el = list[i]
    local count = el.t == "Str" and phrase_at(list, i) or nil
    if count then
      local parts = {}
      for k = 1, count do parts[#parts + 1] = list[i + 2 * (k - 1)].text end
      out[#out + 1] = pandoc.Str(table.concat(parts, NBSP))
      i = i + 2 * count - 1
    elseif el.t == "Str" and list[i + 1] and list[i + 1].t == "Space" and list[i + 2] and list[i + 2].t == "Str"
        and looks_like_product_name(el.text, list[i + 2].text) then
      out[#out + 1] = pandoc.Str(el.text .. NBSP .. list[i + 2].text)
      i = i + 3
    else
      out[#out + 1] = el
      i = i + 1
    end
  end
  return out
end

-- Bind the last two words of a paragraph with a no-break space, so a line never ends in a single word.
local function bind_last_words(list)
  local n = #list
  if n >= 3 and list[n].t == "Str" and list[n - 1].t == "Space" and list[n - 2].t == "Str"
      and #list[n].text <= 12 and #list[n - 2].text + #list[n].text <= 28 then
    list[n - 1] = pandoc.Str(NBSP)
  end
  return list
end

-- Split "label: rest" at the first Str that ends with a colon (within the first eight inlines).
local function label_split(list)
  for i = 1, math.min(#list, 8) do
    local el = list[i]
    if el.t == "Str" and el.text:sub(-1) == ":" then
      local label = {}
      for j = 1, i - 1 do label[#label + 1] = list[j] end
      local word = el.text:sub(1, -2)
      if word ~= "" then label[#label + 1] = pandoc.Str(word) end
      local rest = {}
      for j = i + 1, #list do rest[#rest + 1] = list[j] end
      return trim(label), trim(rest)
    end
  end
  return nil
end

local function plain_text(list) return pandoc.utils.stringify(pandoc.Plain(list)) end

local function header_block(title_inlines, para_inlines)
  local items = split(para_inlines, "·")
  if #items < 2 then return nil end
  local inl = { raw("\\cvheader{") }
  append(inl, title_inlines)
  inl[#inl + 1] = raw("}{")
  append(inl, items[1])
  inl[#inl + 1] = raw("}{Persönliche Daten}{")
  for i = 2, #items do
    if i > 2 then inl[#inl + 1] = raw("\\ {\\color{muted}\\textperiodcentered}\\ ") end
    inl[#inl + 1] = raw("\\mbox{")
    append(inl, items[i])
    inl[#inl + 1] = raw("}")
  end
  inl[#inl + 1] = raw("}")
  return pandoc.Para(inl)
end

-- Two parts (a gap entry, "Zeitraum | Elternzeit") give a station with an empty employer.
local function station_block(content)
  local parts = split(content, "|")
  if #parts < 2 then return nil end
  local employer = {}
  for i = 3, #parts do
    if i > 3 then employer[#employer + 1] = pandoc.Str("|") end
    append(employer, parts[i])
  end
  local inl = { raw("\\cvstation{") }
  append(inl, parts[1]); inl[#inl + 1] = raw("}{")
  append(inl, parts[2]); inl[#inl + 1] = raw("}{")
  append(inl, employer); inl[#inl + 1] = raw("}")
  return pandoc.Para(inl)
end

local function row_block(item_blocks)
  local first = item_blocks[1]
  if not first or (first.t ~= "Plain" and first.t ~= "Para") then return nil end
  local label, rest = label_split(first.content)
  if not label or #label == 0 then return nil end
  local inl = { raw("\\cvrow{") }
  append(inl, label); inl[#inl + 1] = raw("}{")
  append(inl, bind_last_words(rest)); inl[#inl + 1] = raw("}")
  return pandoc.Para(inl)
end

local function bold_label(item_blocks)
  local first = item_blocks[1]
  if not first or (first.t ~= "Plain" and first.t ~= "Para") then return item_blocks end
  local label, rest = label_split(first.content)
  if not label or #label == 0 then return item_blocks end
  local inl = { pandoc.Strong(label), pandoc.Str(":"), pandoc.Space() }
  append(inl, bind_last_words(rest))
  local blocks = { pandoc.Plain(inl) }
  for i = 2, #item_blocks do blocks[#blocks + 1] = item_blocks[i] end
  return blocks
end

-- Bind the last two words of every item of a plain bullet list (the bullets under a station).
local function bind_items(bullet_list)
  for _, item in ipairs(bullet_list.content) do
    for _, inner in ipairs(item) do
      if inner.t == "Para" or inner.t == "Plain" then inner.content = bind_last_words(inner.content) end
    end
  end
end

function Pandoc(doc)
  if FORMAT ~= "latex" then return nil end
  load_keep_together(doc.meta)
  -- 1. no-break product names everywhere. The last two words are bound in step 2, after the label split, so
  --    the no-break space never lands between a label and its text.
  for _, block in ipairs(doc.blocks) do
    if block.t == "Para" or block.t == "Plain" or block.t == "Header" then
      block.content = keep_together(block.content)
    elseif block.t == "BulletList" then
      for _, item in ipairs(block.content) do
        for _, inner in ipairs(item) do
          if inner.t == "Para" or inner.t == "Plain" then inner.content = keep_together(inner.content) end
        end
      end
    end
  end

  -- 2. structure
  local out, section, i = {}, "", 1
  local blocks = doc.blocks
  while i <= #blocks do
    local block = blocks[i]
    local nxt, after = blocks[i + 1], blocks[i + 2]
    if block.t == "Header" and block.level == 1 and nxt and nxt.t == "Header" and nxt.level == 2
        and plain_text(nxt.content) == "Persönliche Daten" and after and after.t == "Para" then
      local header = header_block(block.content, after.content)
      if header then
        out[#out + 1] = header
        section = "Persönliche Daten"
        i = i + 3
        goto continue
      end
    end
    if block.t == "Header" and block.level == 2 then section = plain_text(block.content) end
    if block.t == "Header" and block.level == 3 then
      local station = station_block(block.content)
      if station then out[#out + 1] = station; i = i + 1; goto continue end
    end
    if block.t == "BulletList" and ROW_SECTIONS[section] then
      local rows, ok = {}, true
      for _, item in ipairs(block.content) do
        local row = row_block(item)
        if row then rows[#rows + 1] = row else ok = false; break end
      end
      if ok then
        for _, row in ipairs(rows) do out[#out + 1] = row end
        i = i + 1
        goto continue
      end
    end
    if block.t == "BulletList" then
      if is_label_section(section) then
        for k, item in ipairs(block.content) do block.content[k] = bold_label(item) end
      else
        bind_items(block)
      end
    end
    out[#out + 1] = block
    i = i + 1
    ::continue::
  end
  doc.blocks = out
  return doc
end
