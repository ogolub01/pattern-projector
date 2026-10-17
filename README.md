# Pattern Projector

A sewing pattern projector: calibrate a projector to your cutting mat, open a pattern PDF, put print-at-home pages together, mark pieces and tick them off as you cut.

- The whole app is `index.html` (plain HTML, CSS and JavaScript, no build step).
- Hosted on Cloudflare Pages; every change pushed to `main` goes live automatically.
- Each pattern's PDF and work is saved in the browser on the device you use (IndexedDB); nothing is sent to a server.
- On iPad: open the site in Safari → Share → Add to Home Screen to run it full screen.
