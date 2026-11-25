CUTENESS CASINO — V10 RENDER

LOCAL REHEARSAL
1. Extract the entire ZIP. Stop the old server (Ctrl+C).
2. In the extracted folder, run python3 server.py (or START_MAC.command).
3. Open the printed private Director URL and use Open projection. Press F for fullscreen. Click the projection once to enable audio; browser autoplay policies may still require a manual play click.
4. New sessions start at Lobby. On phones: choose language, receive player number, explore the panoramic lobby. Use the Director's Video button for Angela's opening and Casino / lobby to return. START starts the 7-minute game.
5. Backup QR can be shown/closed at any point without changing the current cue or timer. Director's QR preview is also available. Share the player URL, never the Director URL.
6. End -> Winner -> Speech -> Angela outro -> Reveal archive. Arrow keys navigate speech/scene cues; B blacks out projection. Reset session clears the players and returns to Lobby.

RENDER UPDATE (EXISTING SERVICE)
Copy all extracted files into the existing Git repository root, preserving its .git folder. Include new assets and lobby.html. Commit and push to the branch Render deploys. Existing environment variables must be retained, particularly ADMIN_TOKEN. Build command: pip install -r requirements.txt. Start command: python3 server.py. Render provides PORT and RENDER_EXTERNAL_URL. Health check: /healthz. After deployment, confirm /api/info reports version 10. Restart/deploy resets all game state; never deploy during a performance.
Player: https://<your-render-host>/
Projection: https://<your-render-host>/screen.html?v=10
Director: https://<your-render-host>/director.html?admin=<existing ADMIN_TOKEN>&v=10

V10 CHANGES
- Reference panoramic lobby with fixed dialogue anchors; original language and player-number gates retained.
- Projection-only looped soundtrack (the supplied MP3 matches the V9 file exactly).
- Angela intro/outro converted from provided MOV to browser-compatible H.264/AAC MP4.
- Four supplied archive videos play silently and loop on the projection finale.
- QR backup overlay independent of cue, player state and timer.
- scrollear correction in screen, phone and printable speech; archive description removed from phone.
- Four animal portraits replaced; original Hybrid and Angela coach preserved. Other is a disabled placeholder until a new asset and recipe data are provided; excluded from reels.
- New sessions start at lobby; existing player credentials can reconnect in the same browser tab. Running game reconnection returns to welcome or recipe creation, not necessarily the exact last transient page.

VALIDATION
Python syntax and JS syntax checked. Local HTTP tests: initial lobby, five player joins/production, rankings, QR overlay and timer preservation, end/winner/speech/outro/archive/reset, and all new assets accessible. Browser automation blocked by environment policy; actual Safari/Chrome audio, video and swipe behavior and 50–100 device capacity need a live rehearsal. Data remains in memory, and revenue is simulated. No external AI generation service.
