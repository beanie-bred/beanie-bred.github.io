# ART BIBLE

## Style
Animal Crossing: rounded, pastel, soft shadows, readable silhouettes, warm light.
Background space: dark pastel navy 0x2b3a5e. Garden sky: light pastel blue 0xbcd8ee.

## Characters (source of truth: turnaround sheet in character designs/)
Proportions: feet y=0, head top ≈2.1, head ≈46% of height, long legs, thin arms
hanging nearly straight. Skeleton (makeChibi): hip pivot y0.62, shoulder y1.2,
head center y1.6 (r0.5, scale 1.06/0.98/1.0).
- Beanie: skin 0xfcd9be; near-black hair 0x241a14 — center part, hairline band,
  front locks to waist (sway groups), wavy back mass; thin brows; big brown eyes
  0x3a2014 with 2 glints; round blush 0xf5a2ac (hers only); orange nose 0xe8794a;
  coral cardigan 0xf0917c + 3 buttons + gold necklace; denim skirt 0x27334f;
  white socks; chunky white sneakers.
- Bred: skin 0xf8c9a2; hair 0x33251a feathery fringe + top tufts; THICK brows;
  closed happy eyes ∩; small smile; no blush; black tee 0x232329; brown belt
  0x6a4426 + silver buckle; black baggy jeans 0x17171c; brown loafers 0x5c3a24;
  crossbody strap + hip pouch + brown puppy charm (purple bow, white tag).

## Hard-won rules
- Face features must sit proud of the head ellipsoid: z ≥ 0.44 with the r0.5
  head, or they vanish inside the skin. Verify per-feature when moving them.
- Hair shells must keep front extent < 0.42 at feature heights.
- Both characters cast a blob shadow (dotTex-mapped plane, opacity 0.32).

## Creatures
Jellycat-plush pigeons (Percy: teal head, purple ring, wing stripes), Chippy
(cream bean + tweed flat cap + corduroy legs), pastel whales/fish/seahorses.

## Lighting
Hemisphere 0xe8eeff/0x8a7a9e @1.45, sun 0xfff6e8 @1.4, camera fill point light,
ACES tone mapping exposure 1.14. Garden bumps hemi 1.7 / sun 1.7.
