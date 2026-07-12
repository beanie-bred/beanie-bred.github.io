# KNOWN BUGS / RISKS
- No blocking bugs open after the 2026-07-11 regression (zero console errors;
  12-hop + Percy + Garden + finale run passes with the real skinned Beanie
  avatar driving the whole journey).
- Investigated (2026-07-12), turned out to be a false alarm: the "wide
  sideways arm swing" reported earlier was a debug-camera parallax artifact
  (framePoint() viewed close-up from behind/above), not a real pose problem.
  Direct comparison confirmed Idle and Walk have nearly identical UpperArmL/R
  rotation (x≈-0.31 both), and from the normal in-game camera angle both read
  as a natural relaxed stance. Do NOT re-attempt "fixing" this by rotating
  UpperArmL/R without visually confirming from the standard follow-camera
  angle first, not framePoint() — three attempts (+22°, +8°, -10° extra
  rotation about local X) all produced a broken crossed-arm look, reverted.
  If arm feel is ever revisited, verify the local-X axis assumption first
  (decompose the bone's actual world-space axes) rather than trial-and-error.
- Missing: no sitting/talking pose for the real Beanie model — sit(true)
  currently just holds the Idle pose (title screen, Percy-mount). Bred,
  Percy, and Chippy on the finale couch stand rather than sit for the same
  reason (none of the three has a rig).
- Risk: game pauses when tab is hidden (by design — rAF). Not a player issue.
- Risk: first audio requires a user gesture (SPACE on title handles it).
- Watch: if character geometry is edited, re-check face-feature z clearance
  (see ART_BIBLE) and feet-to-ground contact.
- Watch: Blender's glTF exporter bakes the *edit-bone rest pose* when no
  action is assigned to an armature at export time — it does NOT use a
  manually-posed-but-unkeyed pose_bone state. Any new rigged-character export
  needs its intended "default" pose baked into a real (even 1-frame) action
  first, or it will export as a rough T-pose. See ART_BIBLE.md pipeline notes.
