# Cadence 0.5.0 beta - release note

What changed since the 0.4.0 alpha you have been running. This is the first
build we call a **beta** rather than an alpha, and the name is meant literally:
most of this round is crashes, stalls and data loss rather than new surface.
Mac and Windows both move this time.

## Which zip to take

There is one Mac build now.

- **Cadence-macOS-arm64.zip** is the full app, Apple Silicon only, and it needs
  **macOS 14 (Sonoma)** or newer. That floor is the stem separation runtime it
  bundles.
- **Cadence-Windows-Setup.exe** is the Windows installer.

**The universal build is gone.** 0.4.0 shipped a second Mac zip that ran on
Intel and had no stem separation at all, because nobody publishes an Intel or
universal build of the inference runtime any more. It was the smaller, weaker
half of a confusing pair, no Intel tester ever appeared, and keeping it meant
every install note had to explain which of two apps you had. If you are on an
Intel Mac, this beta has nothing for you, and we would rather say so plainly
than hand you a build with a hole in it.

If you host **Cell** inside Cadence, take the Cell from the plugin bundle as
well. The looping-note fix from 0.4.0 was a fix on both sides.

## First launch

The beta is ad-hoc signed, not notarized, so macOS still asks once. Unzip, drag
Cadence.app to Applications or run it in place, then right-click the app and
choose **Open**, then **Open** again. If macOS refuses anyway, use System
Settings, Privacy & Security, **Open Anyway**. Windows shows "Windows protected
your PC": click **More info**, then **Run anyway**. Full steps are in the
bundled INSTALL.txt.

You should see "unidentified developer" and never "damaged". The damaged wall
was a packaging bug we fixed for 0.4.0, and the packaging step that fixes it is
now checked on every build rather than remembered.

Your settings, library and session state survive the update, so 0.5.0 opens on
the library and the set you left.

## The point of this build: it should stop breaking

**Crashes and audio dropouts on the audio thread.** A handful of things the
audio callback should never do, it was doing. Clearing a clip freed a large
buffer inside the callback, and freeing memory in there is a stall you hear as
a dropout. The reverb tank could take a NaN and stay poisoned, so a channel went
to silence or noise and stayed there until you reloaded. MIDI clock was being
generated on the callback behind a condition variable. Those are moved off,
guarded or self-healing now, and the GUI stopped taking the realtime lock
fifteen times a second just to draw marks. If you have been hearing occasional
clicks with nothing obviously wrong, this is the build to tell us about it on.

**Analysing a long track ate memory by the gigabyte.** Full-file analysis held
the whole decoded file. A twenty minute track peaked at 1.40 GiB, and on a
laptop that is where the beachball came from. It streams now: the same track
peaks at 222 MiB.

**Your curated beatgrids survive a rescan.** If you had corrected a grid by hand
and then rescanned the track, the scan overwrote your work. Both writers now ask
the same question before they touch a grid, so a hand-set grid stays hand-set.

**A corrupt session file no longer costs you the session.** Session, arrangement
and plugin XML are read through a recovery path. If a file will not parse,
Cadence keeps the unreadable one beside it as `.corrupt-<date>`, falls back to
the `.bak`, and refuses to write that file for the rest of the run. That last
part is the real fix: before, a file Cadence could not read at startup was
cheerfully overwritten with an empty one at quit, which turned a bad read into
permanent loss.

**Importing a big library no longer freezes the window.** Probing files ran on
the message thread. Three thousand files blocked the UI for 112 ms at a time.
It runs on a pool now and posts rows back in chunks, and the same import blocks
the message thread for about 0.5 ms.

**A controller unplugged mid-set comes back with its map.** Pull the USB and
plug it in again and Cadence reconnects it and keeps your mapping, instead of
leaving a dead controller that needed a restart to notice.

## The first session on a normal laptop

Several people's first ten minutes went badly for reasons that had nothing to do
with the app being hard.

**On a two-output laptop, the cue controls are greyed out and say why.** Cadence
wants four or more output channels so master and cue can go to different places.
On built-in stereo audio there is nowhere for the cue to go. It used to look
broken and silent. Now the controls it cannot honour are visibly disabled with
the reason attached.

**A missing interface does not leave you with no sound at all.** If the device
your session was saved with is not there, Cadence falls back to a device that at
least has outputs and tells you in a banner what it did, rather than opening
onto silence.

**Dialogs stopped being modal.** The blocking dialogs are gone. A prompt can no
longer trap you in a set, and a dialog that opens behind the window can no
longer look like a freeze.

**A quit during a live set asks first**, and the window comes back where and how
you left it.

## Smaller things you will notice

**MIDI Start lands on the bar.** Cadence armed Start on the play edge and sent
it immediately, so hardware following the clock could come in mid-bar. Start now
goes out on the next bar line with tick zero on the downbeat, and seek and nudge
send Song Position and Continue properly. Free-run is exempt, so it does not go
quiet for a bar.

**Recorded takes can be nudged onto the grid, and SNAP proposes the number.**
A take that landed a few milliseconds off can be slid. The offset lives on the
take, so it travels with the recording rather than belonging to the deck. **SNAP**
reads the first onset and proposes an offset for you, landing within about 6 ms
in our tests. It gets adopted at the next lap wrap or launch, never mid-lap, so
the correction does not click. TRIM and the nudge add, and both use the same
sign: positive pulls the take earlier.

**A lane fed by an instrument or a live input still draws its waveform, and its
TRIM is now capped rather than dangerous.** The lanes themselves arrived in
0.4.0. What is new is the safety: the trim now runs into a cap in front of the
pre-fader limiter, worked out from the channel's own recent peak with about a
thirty second memory. A limiter your gain stage can simply walk past is not a
limiter, and the cue is taken pre-fader, so your headphones were the thing at
risk. When MATCH asks for more than the cap allows, it says **Clamped** instead
of quietly giving you less than it promised.

**Assist says when it is stuck.** If Assist could not do the thing it announced,
it used to sit there looking busy. It now reports the stall in the Monitor and
retries in stages.

**The phone remote is off by default.** It used to start on, bound to every
interface, with no token. It is off until you turn it on, then binds to
localhost, puts a per-session token in the QR code and checks the Host header.
Turn it on once and it stays on.

**Ableton Link is gone, on every platform.** Link is GPLv2, and a closed
commercial binary cannot ship it without a written grant from Ableton. Windows
and Linux never had it compiled in, so this only removes something macOS had.
**MIDI clock out is the sync path now**, and it is the path we have put the work
into: sample-accurate, phase-locked to the audio clock, and Start on the bar as
above. If you were syncing Ableton Live to Cadence over Link, use MIDI clock
instead. If Link turns out to be the thing you actually need, say so and it goes
back on the list, with a licence behind it.

## Licensing

Cadence is built on JUCE 8.0.12, which has no splash screen at all. This build
shows none and is not suppressing one. The twenty-nine
`JUCE_DISPLAY_SPLASH_SCREEN=0` flags the build used to carry did nothing except
raise a compiler warning, and have been removed.

## Still rough

It is a beta and it has edges. TESTERS.md has the full list. Carried over from
0.4.0 and still true:

- Take recording is single-pass. No overdub, no comping, no punch-in.
- An audio take can land early or late until you set TRIM or use SNAP. Please
  tell us your interface and the number that fixed it.
- Separation quality is the model's. Busy mixes bleed between stems.
- CoreML acceleration for stems should stay off. On the machine we can measure,
  CoreML refuses this model and Cadence separates on the CPU anyway.
- Time-stretched playback can sound grainy at large tempo differences.
- Hosted plugins run as plain stereo. Mono or sidechain layouts may fail
  silently.
- Meters read block peaks, not true peaks.
- Re-importing the same Rekordbox or Airwave library can create duplicate
  playlists.
- Cadence wants four or more output channels. On built-in stereo the cue is
  silent, and now says so.

Known and deliberately left for the next cycle, so you do not need to report
them:

- The Track Editor still decodes on the message thread when it opens, so a long
  track pauses the UI as the editor appears.
- Dragging a Composer lane does not hand back cleanly, and overlapping clips are
  not tinted.
- ArrangeView refetches section data every frame.
- Library undo snapshots are held in memory, so a very long session of library
  edits grows.
- A library scan is not aborted on quit, so quitting mid-scan can hang briefly.
- The Sampler's region write can fail silently.
- The first-run card's footer text ellipsizes.

**No ASIO on Windows.** This build is WASAPI only, and that is a decision rather
than an omission: nothing ships in Cadence that cannot be legally included in a
commercial product, and the ASIO SDK cannot. Pick **Windows Audio (Exclusive
Mode)** for anything played live, which gets you roughly 8 to 15 ms. A
low-latency Windows path written in house is a job for after the beta.

**Nothing is notarized or code-signed yet.** That is the next packaging job.

## Reporting

Bugs and impressions to **shlabs.contact@gmail.com**. Most useful: what you did,
what you expected, what happened instead, and the log. Click the **CADENCE**
wordmark top right, then About, then **Show log file**. On macOS the log is at
`~/Library/SHLabs/Cadence/cadence.log`, on Windows at
`%APPDATA%\SHLabs\Cadence\cadence.log`. The About dialog also has **Copy version
info**. For audio glitches, note your interface, sample rate and buffer size.

# Cadence 0.4.0 alpha - release note

What changed since the 0.3.0 build you have been running. macOS only this
round: Windows and Linux stay on the previous drop.

Every feature named here is written up properly in **TESTERS.md**, which was
rewritten for 0.4.0. This page is the short version, plus the few things that
will catch you on the first launch.

## Which zip to take

The two Mac builds are not the same app.

- **Cadence-macOS-arm64.zip** is the full app, Apple Silicon only. Take this
  one if your Mac is M1 or newer.
- **Cadence-macOS-universal.zip** runs on Intel and Apple Silicon and has **no
  stem separation at all**: no model download, no *Separate stems*, no deck
  STEMS row. No universal or Intel Mac build of the inference runtime has been
  published since ORT 1.24, so the build drops the feature rather than failing
  to link. That is why this zip is the smaller of the two. Take it only on an
  Intel Mac.

Install steps are identical for both.

**Neither zip needs macOS 26, and the two do not need the same macOS.**

- **Cadence-macOS-arm64.zip** needs **macOS 14 (Sonoma)** or newer. That floor
  is the stem separation runtime it bundles: the library is built for macOS 14
  and will not load on anything older, so the app cannot either.
- **Cadence-macOS-universal.zip** bundles no such runtime, so it reaches much
  further back. On an Intel Mac it needs **macOS 10.13 (High Sierra)** or newer.
  On Apple Silicon it needs **macOS 11 (Big Sur)**, which is simply the oldest
  macOS Apple Silicon has ever run.

Both floors are now set at build time and stamped into the binaries, instead of
being inherited from whatever machine built them. We build on macOS 26 and have
no older Mac here, so those numbers are what the bundled library and the
compiler say rather than something we have launched on a 10.13 machine
ourselves. If a zip refuses to start on a Mac at or above its number, that is a
bug and we want to hear about it.

## First launch

The alpha is still unsigned, so macOS blocks it once. The steps have not
changed since 0.3.0 and are in the bundled **INSTALL.txt** and in TESTERS.md:
unzip, drag Cadence.app to Applications or run it in place, then right-click
the app and choose **Open**, then **Open** again. If macOS still refuses, use
System Settings, Privacy & Security, **Open Anyway**. Grant Microphone access
only if you pick a live input in Audio Settings.

Earlier zips of this alpha could make macOS say Cadence is **damaged** instead,
which is the one refusal right-click Open cannot clear. That was our packaging,
not your download, and the current zip fixes it. If you still have an old copy,
`xattr -cr` on the app recovers it; see INSTALL.txt.

Your settings, library and session state are stored per user and survive the
update, so 0.4.0 opens on the library and the set you left. Two upgrade effects
are worth knowing before you file a bug.

**Cadence comes up in the new Index look.** 0.3.0 predates the theme setting
entirely, so your saved session carries no theme and 0.4.0 opens in Index.
**SETTINGS, Appearance, Theme** puts Classic back exactly as it was, with no
restart and nothing dropping out of the mix. Once you pick a theme, Cadence
keeps your pick.

**Your plugin menu will read differently, and a rescan may be worth it.**
Cadence does not rewrite your scanned plugin list on upgrade: same file, same
place, same format. What changed is which build it reaches for. Hosting an
AudioUnit editor at a UI zoom other than 100% could drive the editor window off
screen, so Cadence now prefers the VST3 build of a plugin everywhere it loads
one: the plugin menu, the plugin manager, session restore and Assist's Cell
layer. Favourites and use counts follow the swap. The all-plugins menu now
hides an AU entry when a VST3 of the same plugin is scanned, so a menu you knew
will look shorter. If you have only ever scanned AU folders, nothing moves,
your plugins keep loading as AU, and Cadence warns you once when the zoom is
not 100%. To get onto the VST3 path, open **Plugin manager / scan...** and scan
your VST3 folders.

## What is new

**Stems.** Cadence splits a track into drums, bass, other and vocals and plays
a deck from those four parts. Separation is offline, before you play, on a
background thread, and it needs a one-time 316 MB model download from SETTINGS.
A separated track grows a **STEMS | DRM | BSS | OTH | VOC** row on its deck:
click a chip to mute, right-click to solo. The chips are quantized, so a click
lands on the next boundary rather than under your finger, and with STEMS off
they act as a preset you dial in before you switch over. All five are
MIDI-mappable. How many decks may carry stems at once is a setting, and the
default reads your installed RAM. Arm64 zip only, as above.

**The Index look, and it is the default now.** A darker sheet, square corners,
no gradients or drop shadows, structure drawn as rules instead of boxes, and
type set by role. Classic is not a reconstruction and is not going away: it is
the original code path, kept byte for byte and verified on every build. The
switch is instant either way.

**The Composer**, which was called Arrange in 0.3.0. Press 2. One lane per
channel, audio clips and MIDI blocks on the lanes, automation curves under
them, and its PLAY is the master transport for the arrangement. The piano roll
now edits in bulk: marquee drag on empty space, shift to add, Cmd+A for
everything, Delete to remove, drag to move the group rigidly, and drag a
selected note's right edge to set the same length on every member. Rows
belonging to the current key light up. Zoom runs from a 2h40 set on one screen
to a 1/16 note at 40 px. COMPOSITIONS saves and loads whole arrangements, and a
loaded one lands fully in view. The four stem levels are drawable lanes like
VOL and FILT.

**The Sampler has its own listening voice.** A MONITOR group with PLAY, STOP,
LOOP, CUE, MAIN and a VOL fader. It plays straight out of memory, owns no deck
and cannot take one away from you mid-set. CUE and MAIN are two independent
switches, and CUE is on with MAIN off by default, so pressing PLAY can never
surprise a dance floor. This replaces the old AUDITION button, which rendered
the region to a temp WAV and loaded it onto a deck that could be live on the
master.

**Assist and AutoDJ reworked.** HOLD now means what it says during a mix: press
it mid-crossfade and the faders, the EQ bass swap, the filter sweeps and the
stem moves all freeze on the same beat, and release carries on from there. With
stem transitions on, Assist runs a mix through the stems: a true bass
hand-over, the incoming vocal held out until the outgoing track has dropped
away, and a full staged hand-over every fourth eligible mix. Assist can enter
inside a breakdown, and it hears where a track actually sings instead of
guessing. The status strip stopped spending its space on a percentage and now
names the move, how long, and why that track is next. The selector that picks
the next track is pinned down by a 200-check test now, so a pick that still
looks strange to you is worth reporting.

**Recording into a channel, MIDI and audio.** Each deck has its own REC chip in
the deck header. It is not the master REC in the top right, which still records
the whole mix. Click to arm; the count-in starts at the next bar line, you get
the loop length you chose, it auto-stops, and the target starts looping in the
phase you played it. MIDI takes get QUANT as a sensitivity rather than a switch
and an optional snap to key; audio takes are latency-compensated with a TRIM
dial for when your driver misreports. Loop lengths are 1, 2, 4 and 8 bars.
Audio takes are written as 24-bit WAVs the instant the take commits.

**A large UI pass.** Settings is six groups in two columns. The waveform band
gained a diagnostics column and says how loud each lane is. The FX rows, the
master and the deck splits collapse and drag. The compressor is three groups
instead of ten dials, and the FX window uses the console's own bars. Perform
gained a MACROS section, a TRACKS band of full-track lanes that takes a loop
drag, and a per-deck clip grid of eight quantized slots. A channel's MIDI and
OSC sends read as marks.

**A channel's plugin chain is sixteen slots deep, and the count is yours.** Four
slots was never a decision, it was the first number that fit. Storage is sixteen
now, and how many of those a channel offers you is a setting in SETTINGS, AUDIO,
beside the Plugin Manager. Cadence suggests a number from your machine's core
count and you can override it. Empty slots cost nothing you can measure: the
render loop walks the count rather than the array, and the engine benchmark did
not move. Two rules keep the count safe to change mid-session. Lowering it below
a loaded plugin is refused, and Cadence names the blocker, so a plugin can never
end up in a slot you can neither hear nor reach. Loading a session that uses a
slot above your count raises the count and says so, rather than dropping your
chain in silence. Past four slots the strip's PLUGINS section pages, one row
reading 5-8/16; at four it never appears and the strip lays out exactly as it
did.

**Per-track TRIM, and a MATCH that works one out for you.** The waveform band's
diagnostics column gained a third line. TRIM is your own offset on top of the
loudness scan's auto-gain: drag the readout, step it with the - and + chips, or
double-click it back to zero. It is clamped to plus or minus 12 dB, it lights up
whenever it is not zero, and it is saved per track, so it survives an eject and
follows the tune onto a second deck. MATCH reads the loudest deck that is
actually playing to the main out, works out the offset that would put this deck
level with it, and writes that number into the readout where you can see it,
nudge it or undo it. It is a one-shot write, not an automatic gain rider, and it
leaves the fader out of the sum on purpose, since a match that moved every time
a hand moved would be true only for that instant. A deck that has not been
scanned can neither be matched nor be the reference, and says so.

**A lane that makes its own sound gets a waveform.** A channel fed by a hosted
instrument over MIDI, or by a live input, drew nothing in the WAVEFORM band and
had its TRIM and MATCH greyed out. Every test for whether a lane had content was
asking about a file or a stored clip, so a synth being jammed had no lane to
draw in. The lane now keys on a loudness measurement instead: play, and it
appears; stop for a few seconds, and it closes. It is marked LIVE where a clip
lane puts its countdown. MATCH works on these lanes too, reasoning from what
they are playing rather than from a scan, and a lane that has been silent for
the window is a no-op that says why instead of asking for the full plus 12 dB.
Under the feature sits a real fix: the trim is applied at the channel input and
an instrument's audio was summed in after it, so a trim on an instrument lane
was a control that did nothing at all. Radio lanes were in the same greyed
bucket and inherit the trim as well. The TRACKS band gets the same lanes.

## Fixes you may have hit on 0.3.0

**A channel could get stuck in radio mode.** The SRC button derived the next
source from its own two-state face over a three-state model, and only a 20 Hz
poll kept the two honest. Radio entered from the engine side left the face a
tick stale, so a click in that window stored the wrong mode: leaving RAD landed
on IN with every clip control dark, which reads as a dead deck, or the click
was swallowed. A face knocked out of step without a source change never healed
at all. The click is now a step of the source machine, and the poll re-syncs
the face every tick.

**Loops and loop cues behind the playhead did not engage.** The engine declines
a region whose out-point is behind the playhead, which is right for the wrap,
but three gestures were answering to that rather than to the region. Halving
and doubling ignored a passed-by region entirely, and recalling a saved loop
cue could land you inside a loop that had just been switched off. All four
paths are fixed, and a bare LOOP press now loops at the playhead with the
length of the region you last shaped.

**A looping MIDI note could silence a hosted instrument permanently.** A note
longer than the loop it sits inside had its note-off wrapped back by exactly
one lap, which put it past the end of every lap. The note was started on every
lap and never ended. Drop an 8-bar pad into a 4-bar Composer lane and you hit
it. A note-on the host never answers is a voice the instrument can never
reclaim, so after a few minutes the channel goes silent for good while the
plugin's UI still shows the notes arriving. On a monophonic patch it dies at
the first leaked note. The wrap is now folded by however many laps the note
spans. **This was fixed on both sides.** Cadence stops leaking the note, and
Cell stops losing a voice to one. If you use Cell, take the rebuilt Cell as
well as this build.

**Plugin editor windows could blow up.** Hosting an AudioUnit editor at a UI
zoom other than 100% diverged violently, driving the window to 32768 px and off
screen. The editor shell is acyclic now, and Cadence prefers VST3 builds (see
the first-launch note above).

**The main output introduced itself as "M...".** The master section's header read
MAIN OUT open and MAIN collapsed, and the collapsed face is 34 px wide. That
leaves 24 px for the word, MAIN measures 27, and the text was allowed to ellipse.
It reads **OUT** at both faces now. The header sits directly over the master
meters and the master fader, so the shorter word can only mean one thing, and a
name that changed when a section collapsed was a second name for one thing
anyway. Classic fits MAIN with four pixels to spare, which is why this only ever
showed up in Index. Every other MAIN in the app is a button, and buttons squeeze
rather than ellipse, so the CUE/MAIN pairs on the strip, in the Sampler and in
the Track Editor keep their word.

**Swapping an AU for a VST3 could load nothing at all.** Cadence prefers VST3
builds, and that swap trusted the cached plugin list. If the VST3 had been
deleted or moved in Finder since the last scan, the list still named it, so
Cadence traded a working AU for a Plugin Load Failed dialog and hid the AU that
would have loaded. The swap now checks the sibling is still on disk, and a
missing VST3 falls back to a silent, correct AU load. This is what was behind
the Cell load failures we chased: the VST3 bundle had been removed from the
install folder, and every load of the most-used plugin failed on the format
Cadence had just switched to.

## Still rough

This is an alpha and it has edges. TESTERS.md has the full list; the ones most
likely to reach you:

- Take recording is single-pass. No overdub, no comping, no punch-in. A second
  take over the same target replaces the first.
- An audio take can land a few milliseconds early or late until you set TRIM.
  Drivers under- and over-report their latency, and aggregate devices describe
  a path the audio does not take. Please tell us your interface and the trim
  that fixed it.
- Separation quality is the model's, not Cadence's. Busy or heavily processed
  mixes bleed between stems, most audibly on reverb tails and backing vocals.
- CoreML acceleration for stems is offered on Apple Silicon and should stay
  off. On the machine we can measure, CoreML refuses this model and Cadence
  separates on the CPU anyway. It ships because the answer is per-machine.
- Time-stretched playback (SYNC, key-lock) can sound grainy or phasey at large
  tempo differences, most audibly on piano and vocals.
- Hosted plugins run as plain stereo. Mono or sidechain layouts may fail
  silently.
- Meters read block peaks, not true peaks, so inter-sample peaks can still clip
  your interface.
- Re-importing the same Rekordbox or Airwave library can create duplicate
  playlists.
- Cadence wants an audio device with four or more output channels to split
  master and cue. On built-in two-output audio the master plays and the
  headphone cue is silent. That is expected.

## Licensing

Cadence is built on JUCE 8.0.12, which no longer has a splash screen, so this
build shows none and is not suppressing one - the free JUCE tier's condition is
a revenue cap rather than a splash. The twenty-nine
`JUCE_DISPLAY_SPLASH_SCREEN=0` flags the build carried were doing nothing but
raising a compiler warning, and have been removed.

## Reporting

Bugs and impressions via **shlabs.ch**. Most useful: what you did, what you
expected, what happened instead, and the log. Click the **CADENCE** wordmark
top right, then About, then **Show log file**. On macOS the log is at
`~/Library/SHLabs/Cadence/cadence.log`. The About dialog also has **Copy
version info**. For audio glitches, note your interface, sample rate and buffer
size.
