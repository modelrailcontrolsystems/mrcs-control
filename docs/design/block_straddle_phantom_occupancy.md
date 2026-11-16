# Block detection: straddling MPUs and "phantom" occupancy (Roco 10808)

Design discussion, 14 Nov 2026. No code has been written yet.

Relevant code at the time:
- `mrcs-control/src/mrcs_control/operations/track/track_node.py`: `TrackNode.__handle_control_router_message`
- `mrcs-control/src/mrcs_control/operations/track/detector_filter.py`: `DetectorFilter`, a per-block stub
- `mrcs-control/src/mrcs_control/equipment/block/block_persistence.py`: `block_occupants_v1 (block_label, mpu_address, face)`
- `mrcs-core/src/mrcs_core/layout/block/block.py`: `Block.adjacent_blocks()`
- `mrcs-control/src/mrcs_control/operations/motive_power_unit/mpu_node.py`: `MPUNode`, which has speed data

---

## Part 1: Summary of the agreed design

### Terminology and physical constraints
- **Boundary** is the join between two adjacent blocks. Don't use "gap", which suggests a distance between the blocks.
- Detectors are on **single track**. This gives three constraints:
  - Only **one MPU can straddle a boundary** at a time.
  - MPUs **cannot overtake**, so their order along the track never changes.
  - **Every block is longer than every MPU**, so an MPU spans at most two blocks and at most one boundary.
- A straddling MPU electrically bridges its two blocks. Both detectors then report the *union* of the occupants of both blocks. Chains of straddled boundaries carry this further.
- Timing:
  - Related detector reports arrive less than 0.01s apart.
  - Crossing a block always takes more than 0.5s.
  - The order in which reports arrive isn't guaranteed.

### Architecture: three layers
1. **Coalescer.** Batches reports using a quiet-period timer of about 30–50ms. Within a batch, the latest report per block wins. This also fixes the TODO for reports with more than one occupant group (`is_empty_tail`). Startup uses a different rule: the batch ends when every known detector has reported, or on a timeout.
2. **Reconciler.** A pure function with no I/O, so it can be unit-tested from traces:
   `(previous belief, batch of observations, topology, [position source]) → (new belief, alerts)`.
   It replaces the per-block contract of `DetectorFilter`, because the problem involves several blocks at once.
3. **Belief store.** Persisted state; see the data structures below.

### Data structures
1. **Boundaries** (static, in memory): unordered pairs of adjacent blocks taken from `Block.adjacent_blocks()`, stored in a fixed (alphabetical) order.
2. **Occupant table v2** (persisted): adds an `attribution` column with the values **CONFIRMED / PHANTOM / AMBIGUOUS**.
   - Attribution is **always persisted**, so there's no cold start except straight after `populate()`.
   - The table is also the record of what each detector last reported: a block's last observed set is all of its rows, whatever their attribution. That's the reason PHANTOM rows are kept.
3. **Straddle table** (persisted): the "winner" structure.
   - `(block_a, block_b)` is the PRIMARY KEY: one straddler per boundary.
   - `mpu_address` is UNIQUE and NOT NULL: one boundary per MPU.
   - "First to straddle wins" is enforced by the database itself.
   - Only confirmed winners are stored. Uncertainty is carried by AMBIGUOUS occupant rows.
   - Straddle rows and occupant rows are written in one transaction.

### Per-batch algorithm
1. **Build the observations:** for each block, its set of MPUs, taken from the batch where present and otherwise from the stored rows.
2. **Keep or clear straddles (first wins):** the straddler of {A, B} keeps the boundary if it's still observed in both A and B. Otherwise the straddle row is deleted.
3. **Establish new straddles:** for each boundary with no straddler, the candidates are MPUs that are observed in both A and B, previously CONFIRMED in A or B, and not holding another boundary.
   - One candidate: it wins.
   - None: no straddle.
   - **More than one (a tie):** both second rows become AMBIGUOUS and no straddle row is written. Ask the position source to break the tie. **TODO:** the position source answers "unknown" until realtime position exists.
4. **Find bridged zones:** blocks are nodes and straddled boundaries are edges; each connected group is one zone.
5. **Attribute each observed (block, MPU) pair:**
   - **CONFIRMED** if the block is in the MPU's span: the blocks of its straddled boundary, or otherwise (previous span ∩ observed now).
   - **PHANTOM** if the block is outside the span but in the same bridged zone.
   - **New MPU, no history** (it has just been placed on the track): CONFIRMED in an unbridged block. In a bridged zone, AMBIGUOUS in every block of the zone, plus a local alert.
   - **Anything else** breaks an invariant and raises a global alert.
- If a report that physics requires is missing from a batch, wait one more window before raising an alert.

### Worked cases
- **Original trace.** MPU5 straddles BS04/BS05 and MPU3 enters BS04 from BS03. MPU5 keeps its boundary. MPU3 becomes the straddler of BS03/BS04, because MPU5 is excluded from that boundary. MPU3's BS05 row is PHANTOM.
- **Head-on.** MPU3 comes from BS03 and MPU6 from BS05, both into BS04. Each straddles a different boundary.

  | | BS03 | BS04 (shared) | BS05 |
  |---|---|---|---|
  | **MPU3** (straddling BS03/BS04) | CONFIRMED | CONFIRMED | PHANTOM |
  | **MPU6** (straddling BS04/BS05) | PHANTOM | CONFIRMED | CONFIRMED |

  Both phantoms appear in the same batch, when the second straddle forms. They disappear one at a time as each MPU moves fully into BS04.
- **Tie.** MPU3 is fully in BS04 and MPU6 is fully in BS05; one of them moves onto the free boundary. This can't be decided from detectors alone, so it's AMBIGUOUS plus a TODO. If both MPUs are moving towards the boundary, they're on a collision course and that needs its own alert.
- **Startup.** Reconcile against the persisted rows. Where they agree, keep them (the stored straddler keeps its boundary). Where they disagree, an MPU was moved while the system was down: raise an alert.
- **MPU placed on a bridged zone.** AMBIGUOUS plus a local alert. It resolves when the MPU leaves the zone through its own side, or when the user confirms its block.

### Alerts
- A new **Alert** message topic, consumed by a CLU for now.
- Fields: id, severity, category, subject (MPU / block / boundary), text, raised_at, resolved_at.
- Lifecycle: raised → (acknowledged) → resolved. The reconciler resolves an alert automatically when the ambiguity clears; a user resolves one with a CLU command such as "MPU7 is in BS04".
- Active alerts can be queried (same pattern as `FIND_ALL_TURNOUTS`) and are persisted.
- **Local** alerts (placement ambiguity, ties) are already covered by fail-safe occupancy.
- **Global** alerts (broken invariant, a detector missing at startup, a badly inconsistent persisted state) suspend operations until a user acknowledges them.
- TrackNode **raises** alerts; something else **enforces** suspension (a future dispatcher or safety node, or the router).

### Principles
- **Fail-safe:** AMBIGUOUS is published as occupied in every candidate block. Suppress a phantom only when confident.
- **Speed and position:** TrackNode stays independent of `MPUNode` for now.

### The future link with realtime position (agreed at the end of the discussion)
- The **realtime position system** uses boundary crossings as checkpoints to correct accumulated position error.
- The **block detection system** uses realtime position to decide between AMBIGUOUS, PHANTOM and CONFIRMED (ties, placement, and possibly more).
- **The dependency loop must be broken:** the position system should only use **unambiguous** boundary crossings (CONFIRMED straddle established or cleared) as checkpoints. Detection should only consult position where the detectors themselves are ambiguous. Otherwise errors feed back on themselves.
- The CLU "MPU7 is in BS04" confirmation can double as the **precise starting point** that the position system needs when an MPU is placed.
- In the long term, detectors may *correct* dead reckoning rather than being the main source of truth.

### Next steps (user), before resuming
1. Complete the realtime position system. Development constraint: never more than one MPU in a block.
2. Build the alerting facility.
3. Then return to this design to implement the coalescer, reconciler, occupant table v2 and straddle table, and to wire in the position source and alerts.

---

## Part 2: The conversation

### User
I want to discuss a software design problem on the subject of block detection and the inhibiting or removal of "phantom" block occupancy reports from the Roco 10808 detector.

No code should be written at the moment.

The situation: an MPU called MPU5 may straddle two blocks, let's call the blocks BS04 and BS05. This is OK. In this situation, the block detectors for BH and C each report occupancy by MPU5. MPU5 will have two rows in the block-occupants_v1 table. This is done in src/mrcs_control/operations/track/track_node.py

The problem: MPU5 has now electrically connected B and C. Thus when MPU MPU3 moves from block BS03 into block BS04, the detectors report that it has entered both BS04 and BS05. The trace looks like this:

```
mrcs_control_track: *** time since last report:3.963122844696045
mrcs_control_track: *** report:BlockOccupancyReport:{block_id:BlockID:{address:BlockAddress:{detector:5, channel:7}, reporter_id:0xdb78}, occupant_group:1, occupants:[BlockOccupant:{mpu_address:3, face:FACE_FORWARD}, BlockOccupant:{mpu_address:5, face:FACE_FORWARD}]}
mrcs_control_track: *** existing_status:BlockStatus:{label:BS04, address:BlockAddress:{detector:5, channel:7}, heading:UNASSIGNED, voltage:OCCUPIED_WITH_VOLTAGE, occupants:[BlockOccupant:{mpu_address:5, face:FACE_FORWARD}]}
mrcs_control_track: -
mrcs_control_track: *** time since last report:0.0038428306579589844
mrcs_control_track: *** report:BlockOccupancyReport:{block_id:BlockID:{address:BlockAddress:{detector:6, channel:2}, reporter_id:0xd489}, occupant_group:1, occupants:[BlockOccupant:{mpu_address:3, face:FACE_FORWARD}, BlockOccupant:{mpu_address:5, face:FACE_FORWARD}]}
mrcs_control_track: *** existing_status:BlockStatus:{label:BS05, address:BlockAddress:{detector:6, channel:2}, heading:UNASSIGNED, voltage:OCCUPIED_WITH_VOLTAGE, occupants:[BlockOccupant:{mpu_address:5, face:FACE_FORWARD}]}
mrcs_control_track: -
```

The order in which the detectors raise their reports cannot be guaranteed.

We could handle this case because we can check the adjacency of blocks on the layout. For example, BS04 is adjacent to BS03 but BS05 is not. Thus, a report of MPU3 moving from BS03 to BS05 is invalid, and could be marked as such. The time between reports is useful here - multiple detector reports are always less than 0.01 seconds apart, so could be bundled and processed together. The time it takes for an MPU to travel across a block will always be greater than 0.5 seconds.

Unfortunately, there are two other cases that have to be considered:

1. When the TrackNode service starts up, it needs to read all detectors to make sure that the database table is up to date. At this point, the MPUs are typically not moving. We may have to rely on an is_invalid field in the table which would be persisted on the all-block startup case.

2. An MPU may be lifted off the track and set down again in a block that also contains a straddling MPU. Again, there is no movement on the MPU, but this time there is also no record of its occupancy. It may be that this case is insoluble and should result in an alert to the user, requesting that they do not place an MPU on a block with a straddling MPU on it.

What is the shape of the best solution to these problems?

### Assistant
**The core reframe.** While MPU5 straddles the gap, BS04 and BS05 stop being two detection zones. Electrically they are one zone, and both detectors report the union of everything in BS04 ∪ BS05. The reports aren't exactly wrong. They are true about a different zone from the one each detector is labelled with. That leads to three consequences:
1. A bridge has a recognisable signature: two adjacent blocks reporting the same occupant set.
2. Movement inside a bridged zone can't be seen. *(Later largely withdrawn because of the no-overtaking rule.)*
3. The problem fixes itself: when the straddler leaves, the detectors send fresh reports and the ambiguity goes away.

So the right shape isn't "phantom filtering". It's a **state estimator**: detector reports are observations, the occupancy table is a belief derived from them, and topology plus history fill the gap between the two.

**Three layers:**
1. **Coalescer:** quiet-period batching of about 30–50ms (0.01s is tight given LAN/CAN jitter, and still far below the 0.5s block-crossing time). The latest report per block wins. This also fixes the `is_empty_tail` multi-group TODO. Startup ends when every detector has reported, or on a timeout.
2. **Reconciler:** a pure function, `(previous belief, observations, topology incl. turnouts, optional speeds) → (new belief, alerts)`, unit-testable from traces. `DetectorFilter.filter(current_status, report)` works on one block at a time and can't solve a problem that spans several blocks.
3. **Belief store:** an attribution enum replaces `is_invalid`: CONFIRMED, INFERRED, AMBIGUOUS, PHANTOM. Keeping PHANTOM rows lets you rebuild both "what detectors said" and "what we believe".

**Invariants:** span (one block or two adjacent blocks); continuity (only appear in a block adjacent to one you were in, given turnout positions); dwell (at least 0.5s between block entries); stationarity (speed 0 means no change of block). The last one catches the chained-bridge case, where MPU3 crossing BS03/BS04 makes BS03 briefly report MPU5.

**The cases:** moving MPU: adjacency resolves it. Startup: a zone with one occupant is a straddle; with several, persisted belief is needed. Placement: AMBIGUOUS plus an alert, ideally with user confirmation; this is better than a ban.

**Fail-safe principle:** a phantom occupancy is the safe kind of error (a route gets refused); a missed occupancy is the dangerous kind. Publish AMBIGUOUS as occupied.

**Questions:** Is speed available to TrackNode? Can an MPU be longer than a block? Is there a UI channel for confirmations?

### User
Some very good ideas there. Before answering your questions, I should clarify something: detectors are used on single tracks. Thus, if one MPU straddles two blocks, then it is a physical impossibility for another MPU to do so until the first MPU has moved away. This favours a "first to straddle wins" approach.

### Assistant
This gives two invariants:
1. **One straddler per gap ("first to straddle wins").** Model the gap as an entity: fixed topology, with state empty or one MPU. A straddle is established when an MPU appears in both blocks of an unbridged gap. While it lasts, any other MPU seen in both blocks is not straddling. It clears when the two blocks' sets differ again. This resolves the chained case without speed data.
2. **No overtaking.** The order of MPUs along the track never changes. Anything that entered from the BS03 side of a BS04/BS05 straddler must be in BS04. This largely withdraws "movement inside a bridged zone can't be seen."

The reconciler becomes almost deterministic. AMBIGUOUS survives only for "which side of the straddler is the MPU on?": at startup with no persisted state, and on placement. Both resolve when the MPU leaves the zone. Speed is downgraded. MPU length versus block length still matters. New question: how do turnouts inside blocks affect the ordering?

### User
Some responses to your comments:
* Please use "boundary" rather than "gap". Gap suggests that there is some kind of distance between blocks, which there isn't.
* "Startup without persisted state" - the status of the block detector report must always be persisted. For example, it might be "CONFIRMED" for the original straddler, or "PHANTOM" for the second MPU into the block.
* Alerts - there is no UI yet, but it seems reasonable to think about an "Alert" message topic, which could be received by a command-line utility (CLU) for now.

Answers to your questions:
1. Yes, speed data is available, it is processed by the `MPUNode` at the moment. But I am not sure how this is useful - bear in mind that two MPUs could be heading (in different directions) towards the same block. "First wins" still applies.
2. No, every block is longer than an MPU.
3. See alerts. I am not sure whether there would be a class of alerts that caused operations to be suspended until the alert is resolved.

### Assistant
**Persisted attribution:**
- There's no true cold start except straight after `populate()` (which calls `recreate_tables()`).
- Straddles don't need their own table: an MPU with CONFIRMED rows in two adjacent blocks is the straddler. *(Revised later: an explicit straddle table was adopted.)*
- Startup becomes a check against stored state; disagreements raise an alert.
- The enum can shrink to CONFIRMED / PHANTOM / AMBIGUOUS, with an optional separate field recording the source of a confirmation.

**Speed:** drop it. In the head-on example each new straddler is identified by the block it came from, not by timing. "First wins" only governs keeping a straddle that already exists. Two MPUs can't both reach the same boundary without colliding. Leaving speed out keeps TrackNode independent of `MPUNode`. Block length greater than MPU length tightens the invariants; breaking them is a severe alert.

**Alerts:** need a lifecycle (raised → acknowledged → resolved), automatic resolution by the reconciler, resolution by a user from the CLU, queryable active alerts, and persistence. Separate raising (TrackNode) from enforcing (a future dispatcher or safety node, or the router). **Local** alerts are already covered by fail-safe occupancy; **global** alerts (broken invariant, detector missing, badly inconsistent persisted state) suspend operations until acknowledged.

### User
That's fantastic. I would just say that the head-on example should clarify a lot - both MPUs should have two CONFIRMED occupancy rows, and at least one (the second to arrive in the shared block) will have a phantom row. Am I right on that?

### Assistant
Partly. Both MPUs have two CONFIRMED rows, but **each** of them gets a PHANTOM row, in the outer blocks rather than the shared one:

| | BS03 | BS04 (shared) | BS05 |
|---|---|---|---|
| **MPU3** (straddling BS03/BS04) | CONFIRMED | CONFIRMED | PHANTOM |
| **MPU6** (straddling BS04/BS05) | PHANTOM | CONFIRMED | CONFIRMED |

How it unfolds:
1. MPU3 straddles first: no phantoms yet.
2. MPU6 reaches the boundary: both phantoms appear together, symmetrically.
3. MPU3 moves fully into BS04: its BS03 row and MPU6's BS03 phantom go; MPU3's BS05 phantom remains.
4. MPU6 moves fully into BS04: the last phantom goes.

"First wins" plays no part here, because the two MPUs straddle different boundaries. A useful test: a row outside an MPU's span is PHANTOM if a chain of straddled boundaries explains it; otherwise it breaks an invariant.

### User
You are right. I am now thinking about the data structure and query that would be used when the multiple block occupancy reports are received. This data structure would identify the "winner" or true straddler. I don't think we have exactly that yet.

### Assistant
*(The data structures and algorithm are as recorded in Part 1.)* Points from this answer:
- Boundaries are static, from `Block.adjacent_blocks()`.
- Occupant table v2 has an `attribution` column and also serves as the last raw observation for each block.
- An explicit **straddle table** with PK (block_a, block_b) and UNIQUE mpu_address makes the database enforce the physical rules; "first wins" is an insert that fails if the boundary is taken.
- Load the whole state, reconcile in memory, write the changes in one transaction.
- Five-step algorithm; checked against the original trace and the head-on case.
- **Newly found case, the tie:** two MPUs either side of a free boundary, one moves onto it. It can't be decided from detectors, so: AMBIGUOUS, fail-safe. Speed plus `face` could break the tie (if both are moving towards the boundary, that's a collision course).
- If a report that physics requires is missing, wait one more window before alerting.

### User
Good point. Ultimately, the system will be able to locate every operating MPU precisely using realtime monitoring of MPU speed and a given precise starting point when the MPU was placed on the layout. This will resolve the tie, but it is not available yet. So our solution should mark the tie as ambiguous for now, with a TODO to fix this when realtime position is available.

### Assistant
Agreed. Leave a **tie-breaker hook** in step 3, a "position source" that answers "unknown" for now; the TODO goes there. The reconciler stays pure, with position as just another input. Realtime position will also settle the placement case: the CLU "MPU7 is in BS04" command can double as recording the starting point. Detectors may end up correcting dead reckoning rather than being the main source of truth. Local alerts for ties give evidence of how often they happen.

### User
You have hit on it!
* The realtime position system uses traversal over block boundaries as a checkpoint in order to improve position accuracy
* The block detection system uses the realtime position system to disambiguate AMBIGUOUS / PHANTOM / CONFIRMED occupancies

I will now go on to:
* Complete the realtime position system - the only constraint on its development is that it should never encounter more than one MPU in a block, but this is an easy constraint to uphold for development purposes
* Build an alerting facility

Once I have done this, we must return to this conversation. To help with this, can you:
* Remember the details of the conversation and show me how to pick up the conversation again
* Provide this conversation to me as a .md or .pdf file

### Assistant
This document, plus a persistent project memory (`block-straddle-reconciler-design`). One addition: the two systems depend on each other, so break the loop. Position should only use **unambiguous** boundary crossings as checkpoints, and detection should only consult position where the detectors are ambiguous.
