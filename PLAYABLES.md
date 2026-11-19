# Sunken Sanctum on YouTube Playables: plan

Researched 2026-11-19 from Google's own Playables documentation. Every platform claim below cites its page. Claims marked UNVERIFIED could not be confirmed from a Google source. Pages with no "Last updated" footer in the fetched copy are noted as undated.

## Summary

- **Plain HTML5 is the native format.** Playables are web games built on standard Web APIs (JavaScript, Canvas, WebGL). There is no wrapper or native app. A single `index.html` is the expected entry point. [Overview][overview], [Stability][stability], [Getting started][start]
- **But the SDK is mandatory.** The game must load `https://www.youtube.com/game_api/v1` before any game code and call the required SDK functions, or it will not pass review. So the current page cannot be uploaded as-is; it needs a small Playables build. [Getting started][start], [Integration][integration]
- **Access is by invitation.** Developer access is "early access". You apply with an interest form; the Developer Portal is in "Private Preview", "by invitation only", and "may require additional agreements". [Overview][overview] (updated 2026-11-03), [Developer Portal][portal]
- **Money is unlikely for now.** Revenue sharing is a pilot "with a select number of Playable creators". Ads show only in the YouTube Android and iOS apps, and only to a subset of users. No rates, payout thresholds, YPP, AdSense or tax terms are published. [Monetization reference][monref], [FAQ][faq]
- **Build work is small.** The game is turn-based and event-driven (no game loop, no timers, no audio), which makes pause/resume and audio rules nearly free. The real work is cloud save, self-hosted fonts, removing external links and the clipboard save code, and checking layout at extreme aspect ratios. Estimate: about 3 hours of Claude session time, plus about 1 hour of Marika's time to review and test on her phone.

## What changed recently

From the [revision history][revs] (undated page; newest entry 2026-10-16):

- **2026-10-16:** Monetization requirements tightened. Breaking them can get monetization switched off. New rules for real-world rewards, rewarded ads, interstitial ads and advertiser-friendly content.
- **2026-08-25:** Duplicate-content policy added. Content must be original, authorized or licensed, and not "substantially identical" to other Playables.
- **2026-08-24:** Accessibility tags (Accessible Gaming Initiative) added for listings.
- No entries between 2024-07-11 and 2026-08-24. The 250 MiB total bundle limit dates from 2024-06-24.

## Eligibility

| Question | Answer | Source |
|---|---|---|
| Can an individual apply? | The form invites a "game or company". Nothing says individuals are excluded. UNVERIFIED: whether solo developers are accepted in practice. | [Overview][overview] |
| What account is needed? | A YouTube channel that has been onboarded to Playables, with Manager permission for whoever uploads. | [Developer Portal][portal] |
| Is YPP needed? | Not stated on any Playables page. UNVERIFIED. | — |
| Review | Every game and every update (including metadata) is reviewed. Review also weighs "the creator's overall history on YouTube". At most 10 games in review per channel. | [Requirements][reqs], [FAQ][faq], [Developer Portal][portal] |
| Age rating | An IARC rating is required before submitting for review. The questionnaire is done inside the portal. | [Developer Portal][portal] |
| Audience | Must not target kids or be "made for kids"; must suit a general 13+ audience. | [Trust and safety][trust] |
| Licensed material | Must be original or properly licensed. The SRD 5.1 material is CC BY 4.0, which qualifies as licensed, provided the attribution stays in the game. | [Trust and safety][trust] |

## Requirements and how the game measures up

Audit of `index.html` at commit `b5a7fec` (120,676 bytes, one file).

### Must fix

| # | Requirement | Current game | Fix |
|---|---|---|---|
| 1 | Load the SDK script before any game code. [Integration][integration] | Not loaded. | Add `<script src="https://www.youtube.com/game_api/v1"></script>` as the first script. |
| 2 | Call `firstFrameReady()` while a loading screen shows, then `gameReady()` only once the player can interact. [SDK][sdk] | Neither is called. | Show a short loading panel, call `firstFrameReady()`, await `loadData()`, render the title screen, then call `gameReady()`. |
| 3 | Save progress only through `saveData()`; "MUST NOT use any other mechanism to save user progress"; await `loadData()` first; handle saves from older versions. Save must be well-formed UTF-16 and under 3 MiB (should be under 500 KiB). [Integration][integration], [Stability][stability] | Saves to `localStorage` (`save()`, `loadSave()`). | Inside Playables, route `save()` and `loadSave()` to the SDK; keep `localStorage` outside it, following Google's own pattern with `ytgame.IN_PLAYABLES_ENV`. [SDK][sdk] Add a save-format version and tolerate missing fields. Measure save size after a long game. |
| 4 | No external calls except Google/YouTube APIs. [Privacy and data][privacy], [Certification FAQ][certfaq] | Loads two fonts from `fonts.googleapis.com`. | Bundle the two fonts (IM Fell English SC, Alegreya Sans; both SIL Open Font License, UNVERIFIED until the files are checked) as local `.woff2` files. The test CSP does allow Google Fonts, which conflicts with the written rule, so self-hosting avoids the question. [Test suite guide][testguide] |
| 5 | No clickable links to external sites. [Design][design] | Credits link to dnd.wizards.com and creativecommons.org. | Keep the full attribution text and URLs as plain, unlinked text (CC BY 4.0 still satisfied). |
| 6 | No clipboard access except on the player's explicit paste. [Privacy and data][privacy] | "Copy save code" calls `navigator.clipboard.writeText`. | Hide the save code section inside Playables. Cloud save makes it unnecessary, and loading a pasted code would be a second save mechanism (see 3). |
| 7 | Pause all execution on `onPause`, resume on `onResume`; must not use the Page Visibility API. [Integration][integration] | No loop, timers or audio; nothing runs between inputs. Visibility API not used. | Register both callbacks: ignore input while paused, and call `saveData()` on pause. |
| 8 | Use `isAudioEnabled()` / `onAudioEnabledChange()`. [Integration][integration] | The game has no sound. | Register the callback as a no-op so the required call is present. UNVERIFIED: whether a silent game is exempt. |
| 9 | Playable at every aspect ratio from 9:16 to 32:9, adjusting on resize without losing state; no orientation lock. [Design][design] | Responsive grid that stacks under 820px; 4:3 canvas view. Never tested at very wide, short viewports (21:9, 32:9 phone landscape). | Test each ratio in the browser; if the view overflows a short viewport, cap the canvas by height. Also handle a zero-height first load. [Certification FAQ][certfaq] |
| 10 | Touch and mouse for every interaction. [Design][design] | On-screen buttons under the view; all actions are buttons. | Confirm on a phone. No change expected. |
| 11 | Tell the player when there is no more content. [Design][design] | No end-of-content message found in the code search. | Check what happens after the campaign's last level and the random dungeon's fifth level; add a closing message if missing. |
| 12 | Text renders sharp at every resolution and density. [Design][design] | Canvas is fixed 640×480 and 320×320, scaled by CSS; it will look soft on high-density phones. | Size the canvas backing store by `devicePixelRatio`. |
| 13 | Must not use `navigator.language`. Must support English. [i18n][i18n] | Neither used; English only. | None. |
| 14 | Relative paths only; file names alphanumeric plus `_ - .`; Single Page Application. [Stability][stability], [Privacy and data][privacy] | One page, no other files yet. | Keep the font files to safe names. |

### Should fix

- Esc should close modals, and the game must not `preventDefault()` Esc. [Design][design] The keydown handler only acts in the dungeon, so Esc is not blocked; add Esc to close Settings and the character sheet.
- Best effort at WCAG AA, and add accessibility tags in the portal that are accurate. [Accessibility][a11y]
- Load and become interactive in under 5 seconds. [Stability][stability] At about 120 KB plus two fonts this is easily met.

### Already fine

- Size: about 0.2 MiB total against a 30 MiB initial / 250 MiB total limit. [Stability][stability]
- No `eval`, Web Workers or WebAssembly, which reviewers may decline. [Privacy and data][privacy]
- Personal data: the game asks only for character names. The rule bans prompting for real names, ages, usernames and the like. [Privacy and data][privacy] UNVERIFIED: that a fictional character name is acceptable; it is standard in RPGs.
- No sharing prompts, user agreement, exit button or login.
- Ads: optional ("MAY"). [Monetization requirements][monreq] No ad calls are planned; the portal's pre-roll ad cannot be turned off and plays without any code. [Developer Portal][portal]

### Not to ship in the Playables build

- The `<meta name="claude:viewport-fit-sides">` tag left from the authoring tool.
- The file has no `<!doctype html>`; add one.

## Build result (2026-11-19, branch `playables`)

The bundle is `dist/sunken-sanctum-playables.zip`, made by `python build-playables.py`. It holds 8 files, 286 KB unpacked and 197 KB zipped: `index.html`, five `.woff2` fonts and their two SIL Open Font License texts. Upload it as is and pick `index.html` as the entry point.

What changed in `index.html`:

- The SDK script loads in `<head>`, before the game code. Added a doctype, charset and viewport. Removed the authoring-tool meta tag.
- Fonts are served from `fonts/`. Nothing loads from Google Fonts any more. Both fonts are under the SIL Open Font License, confirmed from each font's licence file.
- A loading panel shows, then `firstFrameReady()`, `loadData()`, the title screen, and `gameReady()`.
- Inside Playables, progress saves only through `saveData()`. Saves are grouped to at most one per second, plus one on pause. Outside Playables the game still uses `localStorage`.
- `onPause` saves and stops all input. `onResume` lets input through again. The audio callbacks are registered; the game has no sound.
- Settings shows no save code inside Playables.
- The SRD credit is plain text with the URLs written out. There are no links.
- Esc closes Settings and the character sheet.
- Canvases draw at the screen's pixel density. On short, wide windows the view shrinks so the controls stay on screen.
- The game now says when the player reaches the last level: on arrival and at the blocked stair, in both the campaign and the random dungeon.

What the checks showed:

| Check | How | Result |
|---|---|---|
| Bundle limits, file names, no outside URLs except the SDK, SDK before game code | `build-playables.py` | Pass |
| No outside requests | Served with the Playables CSP from the [test suite guide][testguide], with the Google Fonts allowances removed; listed every resource the page loaded | Pass: only same-origin files |
| SDK call order and save rules | A local stand-in for the SDK that records calls and rejects `saveData` before `loadData` | Pass: `firstFrameReady` → `loadData` → title shown → `gameReady`; no rejected saves; a new game plus moves made one save of about 2.5 KB |
| Pause | Fired pause, then tried keys and clicks | Pass: no movement while paused; state saved on pause |
| Continue after reload | Reloaded with the stand-in's stored cloud save | Pass: Continue returned to the same square |
| Aspect ratios | 360×640 (9:16), 600×600, 1280×720 (16:9), 1260×540 (21:9), 1600×450 (32:9) | Pass: no sideways scrolling, movement buttons on screen, game state kept through each resize |
| Esc, settings, credits | Opened Settings, pressed Esc | Pass |
| Last level message | Took the stairs to the last level in both modes | Pass |
| Plain web version | Loaded `index.html` locally: the real SDK reports it is not in Playables | Pass: title screen, `localStorage` path |

Not yet checked:

- **The real SDK.** It does nothing outside YouTube, so the real calls can only be checked in the [SDK Test Suite][testsuite] or the portal's test step. That needs portal access.
- **Real phones.** The YouTube Android and iOS apps, and a high-density screen, are covered by the portal's test step.

## Build plan (after Marika says go)

Done; see Build result above.

Branch `playables`. The GitHub Pages version on `main` keeps working unchanged.

1. One code path: detect `ytgame.IN_PLAYABLES_ENV`; outside it, keep today's behavior.
2. SDK script, loading panel, `firstFrameReady` / `gameReady`, cloud save, pause, audio callback (items 1-3, 7-8).
3. Self-host fonts (item 4). **Needs Marika's OK to download** two font files from Google Fonts (about 100-200 KB total).
4. Plain-text credits, hide save code in Playables, Esc closes modals, doctype, drop the tool meta tag (items 5-6).
5. Canvas density, aspect-ratio pass, end-of-content message (items 9, 11, 12).
6. Test locally with the Playables CSP applied through Chrome DevTools header overrides, as the guide describes, and in every aspect ratio. [Test suite guide][testguide] The SDK is a no-op when served locally, so the full SDK check happens in the [SDK Test Suite][testsuite]. UNVERIFIED: whether the test suite works without portal access.
7. Package `sunken-sanctum-playables.zip` with `index.html` at its root, check it with Google's [bundle analyzer][analyzer], commit and push the branch.

| Who | Work | Real hours |
|---|---|---|
| Claude | Steps 1-7 | about 3 |
| Marika | Review the build, play it on phone and desktop | about 1 |
| Marika | Interest form | 15 minutes, then a wait of unknown length (UNVERIFIED: third-party guides say weeks to months) |
| Marika | Portal submission: metadata, thumbnails, IARC questionnaire, device tests | 2-3 |

## Only Marika can do these

1. **Decide which YouTube channel** will publish the game. Review weighs the channel's history. [Requirements][reqs]
2. **Done 2026-11-19:** submitted the Playables interest form, giving the GitHub Pages link (https://xerafinatalesedrin.github.io/sunken-sanctum/). Now waiting for an invitation; Google gives no timeline. The form: <https://docs.google.com/forms/d/e/1FAIpQLSdvdQ0lgIq2369aemj1O6w8R8FwGn9O5ARRGODDDUbVINCRJQ/viewform> (linked from the [Overview][overview]).
3. **If invited:** accept whatever agreements the portal requires, and sign in to the Developer Portal at <https://www.youtube.com/playables_portal>. [Developer Portal][portal]
4. **In the portal:** upload the ZIP and pick `index.html` as the entry point; enter title, description, genre, publisher and developer; upload thumbnails in each required aspect ratio (sizes are shown only in the portal; no logos or branding in them, per [Design][design]); choose accessibility tags; set ad settings; run the device tests (desktop web, mobile web, YouTube for Android, YouTube for iOS); complete the IARC questionnaire with a contact email; submit for review. [Developer Portal][portal]
5. **Tax and payment:** nothing to set up now. Revenue sharing is a closed pilot. If YouTube invites her into it, the terms will come with the invitation. [Monetization reference][monref]
6. **Do not share dev or staging links** outside certification testing. [Trust and safety][trust]

## Store description draft

For the portal's description field. Plain register, English only.

> Sunken Sanctum is a turn-based, first-person dungeon crawler. Build a party of one to four adventurers from five guilds and six races, then descend from the town into flooded stone halls beneath a drowned forest. Play the written campaign or a new five-level random dungeon each game. Search for hidden doors, open trapped chests, identify treasure, and carry fallen companions home to be raised at the temple. Your progress saves automatically.

## Sources

[overview]: https://developers.google.com/youtube/gaming/playables
[portal]: https://developers.google.com/youtube/gaming/playables/developer_portal
[start]: https://developers.google.com/youtube/gaming/playables/reference/getting_started
[sdk]: https://developers.google.com/youtube/gaming/playables/reference/sdk
[reqs]: https://developers.google.com/youtube/gaming/playables/certification/requirements
[integration]: https://developers.google.com/youtube/gaming/playables/certification/requirements_integration
[stability]: https://developers.google.com/youtube/gaming/playables/certification/requirements_stability
[design]: https://developers.google.com/youtube/gaming/playables/certification/requirements_design
[privacy]: https://developers.google.com/youtube/gaming/playables/certification/requirements_privacydata
[a11y]: https://developers.google.com/youtube/gaming/playables/certification/requirements_accessibility
[i18n]: https://developers.google.com/youtube/gaming/playables/certification/requirements_i18n_l10n
[trust]: https://developers.google.com/youtube/gaming/playables/certification/requirements_trustsafety
[monreq]: https://developers.google.com/youtube/gaming/playables/certification/requirements_monetization
[monref]: https://developers.google.com/youtube/gaming/playables/reference/monetization
[revs]: https://developers.google.com/youtube/gaming/playables/certification/revisionhistory
[faq]: https://developers.google.com/youtube/gaming/playables/support/faq
[certfaq]: https://developers.google.com/youtube/gaming/playables/support/certification_faq
[testguide]: https://developers.google.com/youtube/gaming/playables/reference/test_suite_guide
[testsuite]: https://developers.google.com/youtube/gaming/playables/test_suite
[analyzer]: https://developers.google.com/youtube/gaming/playables/samples/bundle_analyzer

- Overview: https://developers.google.com/youtube/gaming/playables (updated 2026-11-03)
- Developer Portal: https://developers.google.com/youtube/gaming/playables/developer_portal
- Getting started: https://developers.google.com/youtube/gaming/playables/reference/getting_started
- SDK reference: https://developers.google.com/youtube/gaming/playables/reference/sdk
- Review and certification: https://developers.google.com/youtube/gaming/playables/certification/requirements
- Integration: https://developers.google.com/youtube/gaming/playables/certification/requirements_integration
- Stability and performance: https://developers.google.com/youtube/gaming/playables/certification/requirements_stability
- Design: https://developers.google.com/youtube/gaming/playables/certification/requirements_design
- Privacy and data: https://developers.google.com/youtube/gaming/playables/certification/requirements_privacydata
- Accessibility: https://developers.google.com/youtube/gaming/playables/certification/requirements_accessibility
- i18n and l10n: https://developers.google.com/youtube/gaming/playables/certification/requirements_i18n_l10n
- Trust and safety: https://developers.google.com/youtube/gaming/playables/certification/requirements_trustsafety
- Monetization requirements: https://developers.google.com/youtube/gaming/playables/certification/requirements_monetization
- Monetization reference: https://developers.google.com/youtube/gaming/playables/reference/monetization
- Revision history: https://developers.google.com/youtube/gaming/playables/certification/revisionhistory
- FAQ: https://developers.google.com/youtube/gaming/playables/support/faq
- Certification FAQ: https://developers.google.com/youtube/gaming/playables/support/certification_faq
- Test suite guide: https://developers.google.com/youtube/gaming/playables/reference/test_suite_guide
- Test suite: https://developers.google.com/youtube/gaming/playables/test_suite (not read)
- Bundle analyzer: https://developers.google.com/youtube/gaming/playables/samples/bundle_analyzer (not read)
