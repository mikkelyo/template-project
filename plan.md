# recipe-swipe — plan

## The idea (thought stream)
Tinder for dinner. Same bones as `shopping-list-maker`, but instead of "suggest me a
recipe" you swipe. Random dish pops up, yes/no. When everyone currently swiping has
said yes to the same dish, it pops up on everyone's screen — that's dinner.

No accounts, no login, no passwords, no room codes. Me, my girlfriend, and whoever is
over for dinner — any number of people. One HF Space, one shared round that is the
whole deployment. You open the page, you get a temp uuid in localStorage, and you are
swiping. You see how many others are swiping.

Scoped to a *round*, not a calendar day: it starts when one of us opens the app and
ends when we accept a dish.

Recipes come from the same HF dataset as the shopping list maker
(`mikkelyo/shopping-list-recipes`, `recipes.jsonl`) — one source of truth. That app
writes it; this one only reads it. Schema confirmed against the live file:

```json
{"name": "Green curry", "ambition": "low",
 "ingredients": ["red onion", "garlic", "2x coconut milk", "frozen asian veggies", "broth", "rice"]}
```

`ambition` is `low | medium | high`. Ingredients are already written shopping-list style
— `"2x coconut milk"`, `"3x mutti tomatoes"` — so they need no processing to become the
list you shop from. **25 recipes as of today**, and that number matters — see **Running
out is real**.

## Base: clone `template-project`, not `shopping-list-maker`
Start from `/c/Users/mikke/GitHub/template-project` — the ports-and-adapters one — and
run its rename script first:

```bash
uv run python scripts/rename_project.py recipe_swipe
uv lock && uv run pytest
```

Then delete the `example_client` / `example_api_config` scaffolding (it's referenced
from `app.py`, `config.py`, `di_container.py` and two test modules).

`shopping-list-maker` is the *behaviour* reference — I copy ideas and UI from it, not
its flat layout. Anything I lift from there gets re-homed into a layer.

### Layer map for this app
```
domain/           Recipe, Swipe, MatchResult, Round — pure Pydantic
application/
  ports/          RecipeRepositoryPort, SwipeStorePort
  swipe_service.py       record a swipe, decide a match
  deck_service.py        next card for a uuid
infrastructure/
  huggingface/    HfDatasetRecipeAdapter  (huggingface-hub, recipes.jsonl)
  memory/         InMemorySwipeStoreAdapter (dict, round-scoped)
presentation/
  api/v1/         swipe/deck/events endpoints
  static/         index.html
```
Ports stay `@runtime_checkable` Protocols, adapters conform structurally, and every new
provider gets a case in `tests/unit/test_di_container.py` — same rules as the template.

## Hugging Face only — this app does not generate recipes
- **HF** is the store of record. Same dataset, `mikkelyo/shopping-list-recipes`,
  `recipes.jsonl`, same `hf_token`. Port it behind `RecipeRepositoryPort` so the deck
  doesn't know where dishes come from. Load once at startup, cache in memory
  (`RecipeLoader`'s trick), `reload()` on demand.
- **No LLM. No Anthropic. No generation.** recipe-swipe reads the dataset and swipes it;
  it never authors a dish. `shopping-list-maker` is the app that writes recipes, into the
  same file, and it already does it well — duplicating that here would mean a second
  port, adapter, prompt, write path and API key for a button we'd press a few times a
  year. Ran out of dishes? Generate over there, hit `POST /v1/reload` here.
- Delete the template's `AnthropicCompletionAdapter`, `anthropic_config` and
  `completion_config` along with the `example_*` scaffolding. No Anthropic dependency
  ships in this app.
- Secrets: `.secrets.json` locally, `DYNACONF_*` Space secrets on HF. `hf_token` is the
  only one, and it is required — fail loudly at startup.

## Shape
- Ship as Docker on HF Spaces, port 7860 — copy the other app's `Dockerfile` and the
  YAML front-matter block in `README.md`. Template's `app.py` binds 8080 locally.
- **The HF dataset is the only durable store, and this app only reads it.** Recipes live
  there; everything else is container-local and disposable by design. A redeploy costs a
  round, never a recipe.
- All swipe state in a single in-memory singleton behind `SwipeStorePort`. No DB.
  `{round_id: {recipe_name: set[uuid]}}` plus the round's participant set. No timestamps.
- Strip the template's bearer-token auth off these routes (`SERVICE_API_KEY`,
  `AUTH_AND_CONTEXT`). No callers but us, and she isn't pasting a token on a phone.
  Keep the exception handlers and error DTOs — those are free and good.

## Endpoints
Under `/v1` per the template's router layout; `/` and `/health` stay at the root.

- `GET /` — the swipe UI (`static/index.html`).
- `GET /health`
- `GET /v1/round` → `{round_id, deck, roster, winner}` — the open round, created on the
  fly if there isn't one. Read-only: calling it makes you a spectator, not a participant.
  Creation is **first-write-wins under the store's lock**: you and she both opening the
  app at 17:00 must not mint two rounds, or nothing can ever match.
- `POST /v1/swipe` `{uuid, round_id, liked: [names], position}` → the client's full
  liked set. First call is what joins you. Returns `{matches: [Recipe], roster}`, where
  `matches` is every dish the whole participant set has liked.
- `POST /v1/reload` → re-read `recipes.jsonl` from HF, so dishes authored in
  `shopping-list-maker` appear without a redeploy. It changes the deck, so it *is* a
  reset: new round, new seed, empty roster, broadcast as `round_reset`. Anything gentler
  would leave people holding positions into a deck that no longer matches them.
- `GET /v1/events?round_id=&uuid=` — SSE: roster (uuid, emoji, position, deck size),
  match events, round-failed, round_reset. Polling every 2s is the boring fallback if
  SSE on Spaces annoys me.
- `POST /v1/round/end` — Accept a match; ends the round for everyone.
- `POST /v1/round/reset` — the panic button: new round_id, new deck, empty roster.
  Behind one "sure?" tap.

Any request with a stale `round_id` gets `409` and the current round in the body.

## Matching — why presence doesn't hold
The first sketch — "everyone who swiped in the last 5 minutes must have liked it" —
breaks in ordinary use:

- **Decks don't overlap.** Independent shuffles mean I can burn 20 cards she has never
  seen. Matches become a coincidence.
- **It demands simultaneity.** Me at 17:00, her on the bus at 17:30 — should still
  match, and under that rule never does.
- **Timeouts are the wrong tool.** Any window is wrong in both directions: too short and
  someone drops out for pocketing their phone mid-round, too long and it doesn't clean
  anything up anyway. A timer also makes the match rule non-deterministic — the same
  swipes match or don't depending on the clock, which is impossible to reason about
  when we're standing in the kitchen wondering why nothing popped.
- **The Space sleeps.** In-memory state dies mid-round and takes the evening with it.

## Matching — the model that does hold
**No clocks anywhere.** Nothing expires, nothing times out, nothing is "active". A
participant is in the round until someone hits reset. That is the whole lifecycle.

1. **Round, not day.** A round is created by the first person to open the app and dies
   only by Accept or by the reset button. No midnight rollover, no idle sweep.
2. **Zero friction to join.** Open the URL and you are in — no name, no login, no room
   code. A uuid is minted into localStorage on first load and you become a participant
   the moment you swipe your first card — opening the URL alone makes you a spectator,
   not a veto (see **Joining**). An auto-assigned emoji, derived from the uuid,
   is all the identity there is, and it exists only for the chip.
3. **Any number of swipers.** Two of us on a Tuesday, five when people are over. The
   deck and the match rule don't care about the count.
4. **One shared, seeded deck per round — the whole dataset, every round.** No sampling,
   no deck size: every recipe is in every round, shuffled with the round's seed, same
   order for everyone. Each uuid stores only its position. Overlap by construction, so
   matches come fast, and someone joining late lands on the same cards we already voted
   on. With 25 recipes in the dataset today, reaching the end of the deck is a normal
   evening rather than an edge case — see **Running out is real**.
5. **Unanimity, no quorum.** A match is a dish that **every** participant in the round
   has swiped yes on. Not a majority, not "most", not a threshold — all of them. One no
   means that dish is out for this round.
6. **Likes accumulate and never expire.** Order and timing are irrelevant: the fifth
   person can seal a match on a card the rest of us voted on an hour earlier.
7. **The client owns its likes.** localStorage keeps my liked set; every swipe POSTs the
   whole set and the server just intersects. Server state loss is self-healing — the
   next swipe rebuilds it — which makes Space naps and restarts a non-event.
8. **Reset is the only cleanup mechanism.** Someone left a tab open, a phantom uuid is
   blocking unanimity, we just want a fresh deck — one tap wipes participants, likes,
   positions and matches for everyone. Because reset is always one tap away, nothing
   else in the system needs to expire, prune, or guess.
9. **Fires once per dish per round**, broadcast to everyone. Overlay offers **Accept**
   (ends the round) or **Keep swiping**. It can carry *several* dishes at once: a client
   that buffered swipes offline posts them in one go and can complete more than one
   intersection, so the overlay takes a list.
10. **A round of one cannot conclude.** Matches only fire once there are **two or more**
   participants. With a single participant "everyone agreed" is trivially true on the
   first Yes, and whoever opens the app first would get a dinner overlay before anyone
   else has opened it. Likes still accumulate while you're alone — the dish just fires
   later, when someone agrees. This is about who *counts*, not hesitation: once a match
   fires, it's a match, no confirmation dance.

## Failure is a real outcome
The deck runs out and nothing was unanimous. Don't hide it, don't soften it, don't
quietly drop the unanimity rule to manufacture a result — just say so:

> **No dinner. 😔**
> 30 dishes, nothing all 3 of you wanted.

But name which of the two ways the round died, because they mean different things:

- **Everyone finished, nothing was unanimous.** A real no.
- **Someone stopped swiping and the rest of us are done.** Not a no — an absence. Name
  them so we know why nothing landed: *"Waiting on 🦊 (4/30)"*.

There is a third end-of-deck state that is neither of those: **you are through the deck
and you are the only participant.** Nothing was rejected and nobody is late — the round
just hasn't got a second person yet. Its own copy: *"Through the deck. 6 liked —
waiting for someone to swipe."*

All three offer the same button — **Reset**. The sad message is the honest answer, and
reset is what makes it cheap to be wrong. If we've truly swiped every dish we own, the
fix is to go author some in `shopping-list-maker` and reload — not to bolt a generator
onto this app.

Reaching the end at all is rare now that the deck is the whole dataset. Keep the screen,
don't design around it.

## Running out is real
I earlier assumed the deck was long enough that a match always fires first. At 25 recipes
that is not true, and the arithmetic is worth writing down. If each person says yes to
roughly a third of the deck:

| Swiping | Expected unanimous dishes in 25 |
|---|---|
| 2 people | ~2.8 |
| 3 people | ~0.9 |
| 4 people | ~0.3 |

The two of us usually match. Three of us scrape by. A dinner party mostly fails. That is
not a flaw in unanimity — it's a small dataset, and the fix is more recipes, not a weaker
rule. **The recourse is to go author dishes in `shopping-list-maker` and hit
`POST /v1/reload`.** Every recipe added there makes every future round here more likely
to land.

So: don't add a quorum the first time a dinner party fails. Add recipes.

## Joining — the whole lifecycle
Under unanimity, *when* someone becomes a participant is the highest-stakes decision in
the app: every participant is a veto. So the rule has to be dull and predictable.

### You join by swiping, not by looking
Opening the URL makes you a **spectator**: you get the round, the deck and the roster,
and you count for nothing. Your first swipe is what puts you in the participant set and
on the roster.

This one rule kills most of the failure modes for free:
- A tab someone opened and forgot never enters the denominator, so it can't block
  dinner. The thing that blocks is the thing that swiped, which is also the thing with
  a human attached.
- I can open the app on the laptop to see what's going on without becoming a third veto.
- Nothing needs a heartbeat, a timeout, or a leave button to undo a phantom join,
  because the phantom never joined.

### Identity
- `uuid` minted into localStorage on first load, reused forever. Not an account, not
  tied to a person — it's a browser.
- Emoji is derived from the uuid — hash into a fixed palette of **animals** (🦊 🐻 🦉 🐢
  🦆 🐙 🦡 🐝 🦭 🐐 …), with a collision bump against the current roster so two people are
  never both 🦊. Animals because they're instantly distinguishable at chip size and nobody
  reads anything into being the badger.
- The server stores nothing about you but `uuid -> {emoji, position}`. There is no
  profile to leak because there is no profile.

### Everyone shares one deck, from card zero
The round has a seeded shuffle. A late joiner starts at position 0 like everyone else —
they don't get a personalised deck and they don't skip ahead to where we are. With a
30-card deck, catching up is twenty seconds of tapping, and it means "unanimous" always
means the same thing for every dish.

The nice consequence: **matches can fire retroactively**. Our friend catches up, hits
card 6, taps yes, and card 6 — which the two of us liked ten minutes ago — pops for
everyone at once. That is the app working, not a bug.

### A fired match is final
If a dish matched and *then* someone new swipes in, the match is not retracted. Matches
go into the round's match list and stay. Recomputing history against a changed
participant set would mean a dish could un-win while you're reading the ingredients.

Someone who joins after a match has fired gets the overlay too, mid-deck — Accept ends
the round for everyone, and a late joiner must not be left staring at a dead screen.

Someone who opens the app *after* Accept sees the winner, not a fresh deck: the accepted
dish rides on the round and comes back from `GET /v1/round`, so a phone that was never in
the round still shows tonight's dinner and its shopping list. Reset clears it, for
everyone, and starts the next round.

### Reset is a new round, and everyone finds out
Reset is available to **anyone with the URL**, spectators included — the person who spots
the problem shouldn't have to swipe first to fix it. It works from the fail screen and
from under a match overlay. One confirm tap is the only guard, and that's the whole
threat model.

Reset mints a new `round_id`, a new seed and an empty participant set.
- Live clients get a `round_reset` SSE event carrying the new round, and wipe their
  local like set and position.
- Every request carries `round_id`. A stale one gets `409` plus the current round in the
  body, and the client re-syncs and re-posts. That's the self-heal path for a client
  that was asleep, offline, or behind a napping Space.
- After a reset nobody is a participant — including whoever pressed it. Everyone
  re-enters the same way they did the first time: by swiping.

### Container restarts
All round state lives in the container. A redeploy or a Space wake-up wipes `round_id`,
seed, deck, participants, positions, matches and SSE queues. Only the HF dataset is
durable — a restart costs a round, never a recipe.

In practice this bites *between* rounds, not during one: the Space sleeps on long idle,
so Tuesday's round is long dead by Saturday.

Recovery is the plain 409 re-sync and nothing more. The client's liked set survives
(likes are names, not positions), it re-enters the fresh round and swipes from card zero.
It will re-see dishes it already rejected — accepted, not fixed. Storing a client-side
`seen` set to skip them only pays off during a mid-round redeploy, and buys that with a
second client set plus a server-side "why is this a new round" flag. Not worth the
machinery: a match fires early, so you re-swipe until the first match, not the whole deck.

Two consequences, likewise accepted:

- **The seed does not buy restart recovery.** It isn't persisted, so a restarted server
  rolls a new one. Its only jobs are that everyone in a live round shares an order, and
  that rounds don't all open on the same five cards.
- **"Once per dish per round" is really once per dish per server lifetime.** After a wipe
  the intersection recomputes and an already-fired dish fires again. Harmless — that's
  the self-heal working.

### When someone stops swiping
This is the one real hole in "join by swiping, never leave". She swipes four cards, the
baby cries, phone goes on the counter — and she's now a silent veto on every dish she
never reached. Unanimity plus no clocks means an abandoner can kill a round.

**The reset button is the fix.** Not a timeout, not a kick, not a drop-this-person
affordance — just start over.

Why that's the right call and not a cop-out:
- The deck is ~30 cards and the buttons are huge. Re-swiping is twenty seconds, and it
  happens rarely — someone has to both join *and* wander off mid-round.
- Every alternative is a second way to mutate the participant set, and each one drags in
  its own rules: who may remove whom, what happens to a fired match, what happens when
  the dropped person comes back. All of that machinery, to save twenty seconds of
  tapping.
- Reset is already there, already understood, and can't leave the round in a state
  nobody can explain. One escape hatch that always works beats three that mostly do.
- Nobody has to adjudicate anything. "Ah, she's out — reset" is a sentence people say
  out loud in a kitchen; it needs no UI vocabulary.

The fail screen still *names* who's behind — *"Waiting on 🦊 (4/30)"* — because that's
the information that tells you reset is the answer. It's a label, not a control.

A returning abandoner needs no special handling either: after a reset nobody is a
participant, so she re-enters by swiping, exactly like everyone else.

## The roster
Everyone who joined the round is listed and stays listed until reset — no online dot,
no greying out, no "last seen". Joining is the only event; reset is the only removal.

It lives at the **bottom**, on one line under the Yes/Nope buttons, with the participant
count first and Reset on the end:

```
3 swiping · 🦊 142 · 🐻 4 · 🦉 138          Reset
```

The count is the thing you scan for, and it sits next to the cure on purpose — the two
ways a round goes wrong are both read off this line:

- **Count higher than people in the kitchen** → a phantom participant, someone's old tab
  that swiped once. The raw number is what catches this.
- **Count right, one person stalled** → she's at 4 and we're at 140. That needs the
  per-person progress, not the count.

Both diagnoses end in the same tap, which is why Reset is on the same line.

- One emoji chip per participant, in join order, each carrying that person's position in
  the deck. Emoji is the whole identity and it stays — it's what makes *"waiting on 🦊"*
  a sentence you can say out loud in a kitchen.
- You can tell which chip is yours (subtle ring), and that's the extent of identity.
- Fed by the same SSE stream as matches, so a friend opening the URL just appears.
- Spectators are not on it. You appear the moment you cast your first swipe, which is
  also the moment you start counting toward unanimity.
- Tapping a chip does nothing. The roster is a status display; the only control on the
  screen is Reset.

## UI — phone first
Mobile browser is the primary target; desktop is the afterthought. Assume no keyboard.

- Big tappable **Nope** / **Yes** buttons under the card, thumb-reach at the bottom.
  These are the real interaction — always visible, never hidden behind a gesture.
- Swipe-drag on the card is a bonus on top, not the way in. If it's fiddly, cut it.
- Full-screen card: dish name and ingredient list. One card at a time,
  no scrolling needed to reach the buttons.
- Viewport meta + `touch-action` set so the page never pinch-zooms or rubber-bands
  mid-swipe. Buttons >=48px tall, generous gap so a fat thumb can't hit the wrong one.
- Roster line along the bottom edge, under the buttons — see **The roster** above. Top
  of the screen stays clear for the card.
- **Reset** sits at the end of that line, small and deliberately unexciting, behind one
  "sure?" confirm. Resets the round for everyone.
- Match = celebratory overlay with the recipe + ingredients, dismissed by a big tap
  target, keeps a list of the round's matches.
- Arrow keys on desktop as a nicety only.

## The winner screen is the shopping list
The ingredients arrive with the recipe from the dataset, so the shopping list needs no
second lookup and no derivation — it *is* the `ingredients` array, rendered under the
dish name.

**It has to outlive the round.** Accept ends the round; if you then pocket the phone and
reopen it in the shop, the server has no round, you get a fresh one, and the list you
came to buy is gone. So the accepted dish is written to localStorage and the app opens on
it — not on card one — **until someone hits Reset**. Reset keeps its single meaning: it
is what ends dinner and starts the next round, here as everywhere else.

One consequence to know: Reset is for everyone, so if she starts tomorrow's round while
you're still in the aisle, your winner screen goes with it. The copy button is the
escape — once it's in Notes it doesn't depend on the app at all.

## Match overlay: "Import to notes"
Lift the share/copy button from `shopping-list-maker`'s `static/index.html` verbatim.
Same behaviour, same wording:

- `navigator.share({title, text})` first — that's the good path on her phone, drops
  straight into Notes / whatever she picks. Swallow `AbortError` silently.
- Fall back to `navigator.clipboard.writeText`, then to the hidden-textarea +
  `execCommand("copy")` trick for anything ancient.
- Button flips to "Copied!" for 1.5s, then back.
- Payload is the dish name, blank line, then `- ingredient` per line.
- Same button on the persisted winner screen, not just the live overlay — copying at the
  shop is the main use, not copying at the moment of the match.

## Open questions — decided
Both of these were open. Closing them, because leaving them open is what makes me
build the wrong thing twice.

**Show live vote progress on the card?** Yes, as a muted `2/3`, never *who* voted — the
count is the only thing that tells you whether the round is still winnable, and
per-person attribution is what would turn it into a pressure device.

But **retrospective only: show the count on a card once every participant has passed
it.** Predictive counts break the staggered case. If I swipe the deck first and she
opens later, a visible `1/2` marks exactly which cards I pre-liked, and she stops voting
and starts shopping my shortlist. A count on a card someone hasn't reached is
information about them, not about the dish.

**Log what we ate?** No. It was going to be a `history.jsonl` append on Accept — no UI,
no read path, no endpoint — accumulating against a "what did we eat in March" screen that
doesn't exist and may never. That's building for a hypothetical.

Dropping it has a second effect worth having: **this app writes nothing at all.** It is a
pure reader of the dataset. No write path, no duplicate handling, no partial-write
failure mode, and `hf_token` only ever needs read scope.

## Domain model
Four Pydantic models, `domain/` only, no I/O:

```python
Recipe(name: str, ambition: str, ingredients: list[str])   # mirrors recipes.jsonl
Round(round_id: str, seed: int, deck: list[str])           # deck = recipe names, ordered
Participant(uuid: str, emoji: str, position: int)
MatchResult(recipe: Recipe, round_id: str, participants: list[str])
```

`Round.deck` holds **names**, not `Recipe` objects — the recipe bodies live in the
repository cache and get joined in at the presentation edge. Keeps the store small and
means a `reload()` of the dataset can't leave stale copies of a dish inside a round.

No `Swipe` model in the end. A swipe isn't a thing that persists; it's a message that
mutates a like set. The wire DTO (`SwipeRequestModel`) is the only shape it needs.

## Deck construction
- At round creation: take **every** recipe name from `RecipeRepositoryPort` and shuffle
  with `random.Random(seed)`. No sampling, no `deck_size`. The full dataset, every round.
- Shuffling matters *more* under a full deck, not less: the content is identical every
  round, so order is the only source of variety.
- A late joiner is not punished by a long deck: matches fire retroactively, so he only
  has to reach the first card the others both liked — usually early — not our position.
- `GET /v1/round` ships the whole deck in one payload. A few hundred recipes is a small
  page load; don't build lazy fetching for it.

**Deferred: images on the cards.** Needs an `image` field in `recipes.jsonl` that both
apps tolerate the absence of. Nothing to build now, but build the card with an image slot
that collapses when empty, so adding art later is a data change and not a redesign.

**Deferred lever:** pseudorandom sampling instead of the full deck, when the dataset gets
big enough that rounds stop reaching a match before people get bored. Practical trigger:
deck over ~100 and we notice we aren't finishing. Written down so it's a decision already
made, not a surprise.

## SwipeStorePort — the whole state
One `Singleton` adapter, one lock, this shape:

```python
round: Round | None
participants: dict[str, Participant]        # uuid -> emoji, position
likes: dict[str, set[str]]                  # uuid -> liked recipe names
matches: list[MatchResult]                  # append-only, fired-once, per round
```

Port methods: `get_round()`, `create_round(recipes)`, `reset()`, `record_swipe(uuid,
liked, position)`, `matches()`, `roster()`. Every mutation is under an
`asyncio.Lock` — SSE fan-out plus concurrent swipes on one process makes the
read-modify-write of `matches` a real race, not a hypothetical.

Match computation, on every swipe: if `len(participants) < 2`, no match can fire.
Otherwise `set.intersection(*likes.values()) - {m.recipe.name for m in matches}` →
anything left is new, gets appended to `matches` and broadcast. It can be more than one
dish when a client posts buffered swipes, so the result is a list all the way to the
overlay.

## SSE
- `asyncio.Queue` per connected client, held in the same singleton. Broadcast = put the
  event on every queue; a full queue drops the event rather than blocking a swipe.
- Events: `roster`, `match`, `round_failed`, `round_reset`. Every event carries
  `round_id` so a client behind a reset can detect it without waiting for a 409.
- Heartbeat comment every 15s so Spaces' proxy doesn't kill an idle stream. This is the
  one timer in the app and it is transport-level — it changes no state and no match
  outcome, so it doesn't break "no clocks anywhere".
- On disconnect the queue is dropped. Nothing about the round changes — a closed stream
  is not a leave.
- Phones kill streams on screen lock, so expect this constantly rather than rarely.
  Reconnect on `visibilitychange` as well as on error, with backoff. If it's still flaky
  in the kitchen, the 2s polling fallback is the escape and costs nothing to switch to.
- The client reconnects with backoff and, on connect, re-fetches `GET /v1/round` and
  re-posts its like set. That single path covers reconnect, Space wake-up and reset.

## Config — `settings.json`
The template's `anthropic_config` and `completion_config` blocks are deleted. What's
left:

```json
"recipe_repository_config": {
  "dataset_repo_id": "mikkelyo/shopping-list-recipes",
  "recipes_path": "recipes.jsonl"
}
```

Secrets stay out: `hf_token` comes from `.secrets.json` locally and a `DYNACONF_*` Space
secret on HF. Required at startup — no lazy defaults, no "run without HF" degraded mode.
If it's missing I want the Space to fail on boot, not at the first swipe.

## Tests
Unit only, `pytest`, no live HF calls anywhere.

- `test_swipe_store_adapter.py` — the match rule is the app, so this is the file that
  matters: unanimity with 2/3/5 participants, one no kills a dish, a late joiner fires
  a retroactive match, a fired match survives a new participant joining, reset empties
  everything, a swipe from an unknown uuid joins them, **a solo participant's Yes fires
  nothing**, and one POST completing several intersections returns them all.
- `test_deck_service.py` — the deck is every recipe in the dataset, same seed gives the
  same order, a reload rebuilds it.
- `test_hf_dataset_recipe_adapter.py` — mocked `huggingface-hub`, duplicate-name skip
  on write, vendor exceptions translated to domain ones at the boundary.
- `test_di_container.py` — a case per new provider, `assert isinstance(adapter, Port)`.
  Non-negotiable; it's the only guard against wiring drift.
- Endpoint tests with FastAPI's `TestClient` and the container overridden with fakes:
  the 409-on-stale-round path, swipe joins on first call, reset broadcasts.

## Build order
Each step ends somewhere I could stop.

1. Rename the template, delete the `example_*` scaffolding, green `pytest`.
2. `domain/` models + `SwipeStorePort` + the in-memory adapter + its tests. The match
   rule is correct before any HTTP exists.
3. `RecipeRepositoryPort` + HF adapter, loaded at startup. `GET /v1/round` returns a
   real deck.
4. `POST /v1/swipe`, unanimity end-to-end. Now two curl sessions can match. Ugly but
   done.
5. `static/index.html` — card, two buttons, localStorage uuid and like set, polling.
   First version that works on a phone.
6. SSE, replacing polling. Roster strip, live counts, match overlay + share button.
7. `POST /v1/reload`.
8. Fail screen, the three end states, reset behind a confirm.
9. Dockerfile, README front-matter, deploy to the Space, cook something.

## Not doing
Users, accounts, auth, room codes, a database, persisting swipe history past the round.
Threat model is zero malicious users — anyone with the URL is someone in the kitchen.
Swipes are ephemeral on purpose; only *recipes* are durable, and those live in the HF
dataset both apps share.

Also explicitly not doing, so I don't relitigate at 22:00 on a build night: multiple
concurrent rounds, a leave button, per-person deck filters, ambition-based filtering,
a kick/drop affordance, ingredient search, a "who voted no" reveal, and any form of
expiry, timeout or idle sweep. Also: no deck size, no per-round recipe sampling — the
deck is the dataset until the deferred lever above says otherwise. And **no recipe
generation** — no LLM in this app at all; authoring lives in `shopping-list-maker`.

## Ambition is ignored
The field exists in the dataset but v1 neither shows nor filters on it. I'm the chef —
if I swipe yes I've already accepted the effort, so a separate difficulty signal buys
nothing. Revisit only if we ever want a "quick weeknight" mode.
