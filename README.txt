CUTENESS CASINO — FINAL LIVE V7

1. Stop old server with Control+C. Extract entire ZIP to a new folder.
2. In Terminal, cd to that folder and run: python3 server.py
   No pip installation needed. If port 8000 is occupied, stop old server or use: python3 server.py 8001
3. Wait for V7 — READY. Open the newly printed Director URL (private). Click Open projection and drag that window to the external screen. Press F on projection to go fullscreen.
4. Connect all phones and Mac to the same Wi-Fi that allows device-to-device connections. For a rehearsal, a dedicated router or another phone's hotspot may work; some hotspots also isolate devices.
5. Click 2 · QR. Scan with phone or type the exact Player URL in Safari/Chrome, including http:// and port. QR is generated locally from the current server address. If address is wrong, run ipconfig getifaddr en0 on Mac, enter http://<actual IP>:<port>/ in Player access URL, and click Save player URL. Check that macOS firewall allows Python incoming connections (do not disable firewall globally). If local Wi-Fi isolates clients, change network; no HTML fix can bypass that.
6. Join at least five phones. Director Live participants should show 001–005. Click 3 · Casino / lobby then 4 · START 7 MIN. Produce on each phone. Check real rankings. Game ends automatically or use End early for rehearsal.
7. Winner, Speech, then right/left arrow for manual subtitles (no synthetic voice). Archive is the final cue. B blacks out projection without stopping the clock.
8. Reset session for next rehearsal. Do not close Terminal during show. Player data is held in memory. Do not share Director URL.

Angela video: put your file in assets/angela.mp4 and enter assets/angela.mp4 in Director; Save video. Original video was not included.

Tested: five concurrent independent HTTP players joining/producing, sequential IDs, shared ranking, duplicate prevention, recharge, reconnect, QR decoding, MP4 byte-range requests, final freeze and speech cues. Actual mobile/browser/Wi-Fi rehearsal remains necessary. All revenue is simulated. No external AI generation service.

Speech update: 29 Spanish projection cues. Winner phone displays full Spanish script and private acting directions; other players see spoken text only. No speech audio.

V9: soundtrack loops during game; director controls volume, mute, pause, restart. Click projection before show to enable audio. Put final video in assets/angela-outro.mp4 or set its URL in director. After final speech Next plays outro; Next reveals archive on all joined phones. External archive requires internet.
