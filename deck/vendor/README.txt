vendor/ — LOCAL, OFFLINE assets only (no CDN, ever)

This directory is the in-repo home for any fonts or libraries the
four-deck season needs at runtime. The deck must run fully offline
from file:// on a HAL presenter laptop, so nothing here may be
fetched from a network.

Currently EMPTY by design — the design system ships with system
font stacks (see --disp / --sans / --mono in system.css) and pure
vanilla JS (system.js), so no vendored assets are required yet.

If/when an "expensive" geometric-grotesk display face is vendored
to replace the Segoe UI fallback (see design_system_changes), drop
the .woff2 here and @font-face it locally in system.css. Do NOT
add a Google Fonts <link> or any external script.
