# 3 Update

## Role

Apply the decisions from stage `2-validate` back into `.evenbetter/<project-name>/evenbetter-analyze-report.html`. Rewrite the JS literal in place when anything changed; emit a single "OK" line when nothing did.

## Process

1. Compute the validation tally:
   - `kept` — count of `keep` decisions.
   - `adjusted` — count of `adjust` decisions.
   - `removed` — count of `remove` decisions.
2. If `adjusted == 0` and `removed == 0`, do not touch the file. Emit one line and stop:

   ```
   OK — <kept> findings validated, no changes needed
   ```

   Use the absolute path of the report on its own line beneath the OK line so the user can still click through if they want to.
3. Otherwise, build the new `report` object from the surviving findings:
   - Drop every `remove` finding from `report.issues`.
   - Replace every `adjust` finding with its updated object, in the original list position.
   - Recompute `report.summary` from scratch:
     - `summary.total === report.issues.length`.
     - `summary.critical`, `summary.high`, `summary.medium`, `summary.low` are the counts of each severity in `report.issues`.
   - Update `report.scan_date` to the current local time formatted as `YYYY-MM-DD HH:MM:SS`.
   - Leave `report.project_name`, `report.project_path`, `report.framework`, `report.wcag_level`, and `report.scan_context` unchanged. Validation does not re-detect frameworks or recompute the original scan stats.
4. Sanity-check the new object before serialization:
   - `summary.total === issues.length`.
   - Every `severity` is one of `critical`, `high`, `medium`, `low`.
   - Every `hig_reference_url` is a non-empty string starting with `https://developer.apple.com/`.
   - Every `id` is unique within `issues`.
   - Every `code_snippet`, `minimal_fix`, and `recommended_fix` is non-empty.
   - Every `ai_fix_prompt` is non-empty and under ~1,500 characters.

   If any check fails, do not write. Surface the failing finding's `id` and field to the user and stop.
5. Serialize the object to a JSON literal. The template's loader expects valid JavaScript, and JSON is valid JavaScript here, so use a deterministic JSON serialization with a stable key order matching the schema. Do not pretty-print with line breaks unless the previous report was pretty-printed; mirror the original formatting style of the slice between `prefix_index` and `suffix_index` to keep diffs minimal.
6. Splice the serialized literal into `html`:
   - Replace the substring from `prefix_index` (inclusive) through `suffix_index` (inclusive) with the new literal.
   - The character immediately after the splice must remain `;`. Do not add or remove the trailing semicolon.
   - Do not modify any other byte of `html`. Markup, styles, Alpine bindings, CDN references, and the surrounding `<script>` block must stay byte-identical.
7. Write the modified `html` to the same absolute path that stage `1-load` read from. Overwrite the existing file in place. Do not create a backup or sibling file unless the user explicitly requested one.

## After writing

Surface a short status to the user, then stop. Two formats only:

Clean pass (no rewrite):

```
OK — <kept> findings validated, no changes needed
file:///<absolute-path-to-report>
```

Rewritten report:

```
Validated <total>: <kept> kept, <adjusted> adjusted, <removed> removed
file:///<absolute-path-to-report>
```

Do not summarize the adjusted or removed findings inline. The HTML is the deliverable; the user opens it to read the diff between runs. If the user explicitly asked for a list of changes, append a single bulleted list of `id — short reason` lines beneath the status.

## Recovery

If serialization or splice fails after stage 2 succeeded:

- Do not write a partially-modified file. Discard the in-memory `html` mutation.
- Report the failing step (serialization, splice anchor mismatch, post-write validation) and the finding `id` involved when applicable.
- Leave the original report untouched on disk.
