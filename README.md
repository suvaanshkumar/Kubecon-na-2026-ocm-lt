# Deploy with OCM with confidence: hub-to-managed-cluster ManifestWork latency in OCM

OCM Project Lightning Talk, KubeCon + CloudNativeCon North America 2026, Salt Lake City.

The idea: the hub records **T1** when it admits a ManifestWork write, the work agent records
**T2** when it starts applying that generation, and any observability tool matches the two on
`{mw_namespace, mw_name, generation}`. A T1 with no T2 means the work never arrived.

T2 ships in OCM v1.4 behind the alpha feature gates `ManifestWorkApplyLogs` and
`ManifestWorkApplyMetrics` (ocm #1633, #1658, #1696, #1711, #1448, #1721).

## Live links

| What | Link |
|---|---|
| Slides (open in a browser, press F for fullscreen) | https://suvaanshkumar.github.io/Kubecon-na-2026-ocm-lt/deck/ |
| Closing slide with the LinkedIn QR code | https://suvaanshkumar.github.io/Kubecon-na-2026-ocm-lt/deck/#10 |
| KubeCon conference planner (booth shifts, talk, sessions, videos) | https://suvaanshkumar.github.io/kubecon-na-2026-planner/ |
| Planner source | https://github.com/suvaanshkumar/kubecon-na-2026-planner |

## Layout

| Path | What it is |
|---|---|
| `deck/index.html` | The slides. Self-contained, works offline. |
| `deck/deploy-with-ocm-with-confidence.pptx` | PowerPoint build on the official CNCF template. Native shapes, click builds on slides 2, 3 and 5, talk track in the speaker notes. |
| `deck/deploy-with-ocm-with-confidence.pdf` | PDF export of the HTML deck. |
| `deck/assets/` | Logo lockup and artwork from the official CNCF KubeCon NA 2026 template. |
| `docs/talk-track.md` | What to say on each slide, with timings. |
| `hack/build-pptx.py` | Rebuilds `deck/deploy-with-ocm-with-confidence.pptx` from the CNCF template. Standard library only. |
| `hack/latency.sh` | Matches T1/T2 JSON log lines and prints latency, or NEVER ARRIVED. |
| `hack/stale-works.sh` | Lists ManifestWorks whose current generation the agent hasn't applied. |
| `examples/` | Sample hub and managed cluster logs and a saved ManifestWork list. |

## Presenting

Open `deck/index.html` in a browser and press `F` for fullscreen. Arrow keys, Space,
PageUp/PageDown (clickers) and mouse clicks change slides. `#3` in the URL opens slide 3.

## Rebuild the PowerPoint

The CNCF template (`KubeCon CloudNativeCon North America 2026 - Branded PowerPoint.pptx`,
not committed) must sit in the repo root.

```bash
python3 hack/build-pptx.py "KubeCon CloudNativeCon North America 2026 - Branded PowerPoint.pptx" deck/deploy-with-ocm-with-confidence.pptx
```

## Re-export the PDF

```bash
npm install --registry https://registry.npmjs.org
npx playwright install chromium
npm run pdf        # writes deck/deploy-with-ocm-with-confidence.pdf and deck/png/slide-N.png
```

## Try the scripts on the sample data

```bash
NOW_MS=1793002400000 hack/latency.sh          # sample logs, "now" fixed so the timeout fires
hack/stale-works.sh examples/manifestworks.json
hack/stale-works.sh                            # against your current hub context
```

`latency.sh` accepts any files of JSON log lines, so you can point it at
`kubectl logs` output from the hub stamper and the work agents. `TIMEOUT_MS`
(default 120000) controls when a missing T2 becomes NEVER ARRIVED.
