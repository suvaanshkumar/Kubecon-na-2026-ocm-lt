# Talk track

Slot: Mon Nov 9, 2026, 12:06-12:11 pm, Hyatt Regency Level 4, Regency Ballroom B-D.
Target: 4:30 spoken, 30 seconds of buffer. One speaker, own laptop, HDMI.

| Slide | Starts at | Say |
|---|---|---|
| 1 Title | 0:00 | "I'm Suvaansh, a software engineer at Guidewire and an Open Cluster Management maintainer. Five minutes on one question: did my workload land?" |
| 2 Use case (2 clicks) | 0:20 | Open: "At Guidewire we run one OCM hub cluster and managed clusters in several regions." Click 1: "Teams apply a workload on the hub cluster and OCM sends it to every region." Click 2: "The hub cluster knows the workload was accepted. It can't tell us how long it took to land in us-west or ap-south, or whether it reached eu-west at all. Until recently OCM had no signal from the managed cluster for this." |
| 3 Flow (5 clicks) | 0:55 | Click 1: "A user applies a workload/ManifestWork on the hub cluster." Click 2: "The hub cluster's webhook sends a log with the workload/ManifestWork name, generation and a UTC timestamp. That's T1. Both sides log in UTC, so we can compare them directly." Click 3: "The work agent on the managed cluster picks it up over its watch." Click 4: "It applies the workload and sends the same kind of log, with its own timestamp. That's T2. This managed cluster log ships in OCM 1.4; we contributed it upstream." Click 5: "Your observability tool matches the two logs and subtracts. Nothing on the clusters does the math." |
| 4 Output | 1:50 | "One workload on one managed cluster, ap-south. The hub cluster log and the managed cluster log carry the same workload name, managed cluster and generation. Generation 1, the first rollout, took 912 milliseconds. Generation 2 was a smaller change and took 434. Generation 3 has a T1 but no T2: it never arrived." |
| 5 Never arrived (2 clicks) | 2:35 | Open: "Here's a workload for eu-west. The hub cluster logged its T1." Click 1: "But no T2. We give it a timeout." Click 2: "Timeout passes, still no T2. That workload never arrived. That's the whole check: a T1 with no T2." |
| 6 Any observability tool | 3:25 | "None of this is tied to a vendor. Find the two logs, match them on managed cluster name, workload/ManifestWork name and generation, subtract. And catch the missing T2: none after a timeout means it never arrived. Any observability tool can do that." |
| 7 Thank you | 4:00 | "If you run into any issues, reach us in #open-cluster-mgmt on Kubernetes Slack. Thank you." |

## Before the review with August and Mike

- Replace the example numbers on slide 4 with real measurements, or keep the "example output" label.
- Confirm they're comfortable with the "contributed by Guidewire" line on slide 3.

Regions on slide 2 are illustrative. Swap them for the real ones if you're comfortable sharing them.

Q&A backup for slide 5: no T2 can also mean the managed cluster's logs aren't reaching your observability tool, so check the workload/ManifestWork status on the hub cluster to confirm. A T2 that says "apply failed" means it arrived but didn't apply.
