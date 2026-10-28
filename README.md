# Vinyl Zoetrope Designer

Design zoetrope animation strips for vinyl records. Drop GIFs or images onto the ring list, preview the strobe illusion, and export a print-ready PNG.

## Zoetrope timing explained

| Record | RPM | Revolution time | Frames/ring | Actual fps |
|--------|-----|-----------------|-------------|------------|
| 12"    | 33⅓ | **1.80 s**      | **45**      | 25.0       |
| 7"     | 45  | **1.33 s**      | **33**      | 24.75 ≈ 25 |

The math: `frames_needed = round(target_fps / rps)` where `rps = rpm / 60`.  
A strobe light firing at 25 Hz illuminates the disc once per frame slot per revolution, making the animation appear frozen.

## Running from source

```bash
pip install PyQt6 Pillow
python main.py
```

## Building a standalone executable

A standalone app bundles Python + all dependencies into a single folder you can copy to any machine. **You must build on the target OS** — you cannot cross-compile.

### Windows (.exe)

```
build.bat
```
Output: `dist\VinylZoetrope\VinylZoetrope.exe`  
Distribute: zip the entire `dist\VinylZoetrope\` folder.

### macOS (.app)

```bash
chmod +x build.sh && ./build.sh
```
Output: `dist/VinylZoetrope.app`  
Distribute: zip `dist/VinylZoetrope.app`.

> **macOS Gatekeeper note:** The first time you open the app, right-click → Open (or go to System Settings → Privacy & Security → Open Anyway) because the bundle is not code-signed.

### Linux

```bash
chmod +x build.sh && ./build.sh
```
Output: `dist/VinylZoetrope/VinylZoetrope`  
Distribute: zip the entire `dist/VinylZoetrope/` folder.

## Usage

1. **Add rings** — drop a GIF or image onto the left panel, or click the drop zone to browse.  
   - GIF: each frame becomes one slot around the ring.  
   - Static image (PNG/JPG): the same image fills every slot.  
   - Rings fill the playable area equally, outermost first.  
   - The disc alerts you when full.

2. **Reorder** — drag rows in the ring list, or use ▲ / ▼ buttons.

3. **Preview modes**
   - **▶ Spin** — continuous rotation at the correct RPM.  
   - **❄ Freeze** — advances exactly 1/N rotation per 25 Hz tick; looks frozen, like under a real strobe.  
   - **⚡ Blink** — spins continuously but flashes black at 25 Hz so you can see the raw strobe effect.  
   - Speed slider: 0.1× – 3.0× for slow-motion inspection.

4. **Settings (right panel)**
   - Toggle 12" 33⅓ / 7" 45 RPM (clears rings).  
   - Show/hide groove guides and frame numbers.  
   - Label colour picker.

5. **Export** — choose 150 / 300 / 600 DPI and save a PNG.  
   A 12" disc at 300 DPI exports as 3600 × 3600 px.  
   Print on paper, cut to a circle, and place on your turntable.
