# Talk track

Slot: Mon Nov 9, 2026, 12:06-12:11 pm, Hyatt Regency Level 4, Regency Ballroom B-D.
Target: 4:40 spoken, 20 seconds of buffer. One speaker, own laptop, HDMI.

| Slide | Starts at | Say |
|---|---|---|
| 1 Title | 0:00 | "I'm Suvaansh, a software engineer at Guidewire and an Open Cluster Management maintainer. Five minutes on two questions: how long did my workload take to reach the cluster, and did it arrive?" |
| 2 OCM in 20 seconds | 0:15 | "Open Cluster Management is a CNCF Sandbox project, now in its sixth year. It's hub and spoke: one hub gives you a centralized view of your entire fleet and delivers work to every cluster through an agent. Both links are on the slide." |
| 3 Why (4 clicks) | 0:35 | Open: "Before the how, the why." Click 1: "Today our CI/CD pipelines deploy straight to each managed cluster. Those pipelines took years to harden. We know their latency and we know how they fail." Click 2: "Now we're adding a new layer to a pipeline teams already trust." Click 3: "The pipeline applies to an OCM hub cluster and OCM carries the workload to the managed cluster. Same pipeline, one more hop." Click 4: "That hop is the question. How much lag does it add? And did the workload actually arrive? Teams won't move to the hub without the confidence they already have. So we measure the hop and prove every arrival. That's what this talk is about." |
| 4 Use case (2 clicks) | 1:05 | Open: "At Guidewire that hub serves managed clusters in several regions." Click 1: "Teams apply a workload on the hub and OCM sends it everywhere." Click 2: "The hub can't tell us how long it took to land in us-west or ap-south, or whether it reached eu-west at all." |
| 5 Flow (5 clicks) | 1:30 | Click 1: "A user applies a workload/ManifestWork on the hub cluster." Click 2: "The hub cluster's webhook sends a log with the workload/ManifestWork name, generation and a UTC timestamp. That's T1. Both sides log in UTC, so we can compare them directly." Click 3: "The work agent on the managed cluster picks it up over its watch." Click 4: "It applies the workload and sends the same kind of log, with its own timestamp. That's T2. This managed cluster log ships in OCM 1.4; we contributed it upstream." Click 5: "Your observability tool joins the two logs on the key they share: managed cluster, ManifestWork name, generation. Same key means same rollout. Subtract the two UTC timestamps: 434 milliseconds. Same key and no T2 inside the timeout: it never arrived. Nothing on the clusters does the math." |
| 6 Output | 2:20 | "One workload on one managed cluster, ap-south. The hub cluster log and the managed cluster log carry the same workload name, managed cluster and generation. Generation 1, the first rollout, took 912 milliseconds. Generation 2 was a smaller change and took 434. Generation 3 has a T1 but no T2: it never arrived." |
| 7 Never arrived (2 clicks) | 3:00 | Open: "Here's a workload for eu-west. The hub cluster logged its T1." Click 1: "But no T2. We give it a timeout." Click 2: "Timeout passes, still no T2. That workload never arrived. That's the whole check: a T1 with no T2." |
| 8 Any observability tool | 3:40 | "None of this is tied to a vendor. Find the two logs, match them on managed cluster name, workload/ManifestWork name and generation, subtract. And catch the missing T2: none after a timeout means it never arrived. Any observability tool can do that." |
| 9 Thank you | 4:15 | "If you run into any issues, reach us in #open-cluster-mgmt on Kubernetes Slack. Thank you." |

## Before the review with August and Mike

- Replace the example numbers on slide 6 with real measurements, or keep the "example output" label.
- Confirm they're comfortable with the "contributed by Guidewire" line on slide 5.
- Slide 3 answers the "why" feedback: the direct path is trusted, the OCM hop has to earn the same confidence. Check the wording lands with them.

Regions on slides 2, 3 and 4 are illustrative. Swap them for the real ones if you're comfortable sharing them.

Q&A backup for slide 7: no T2 can also mean the managed cluster's logs aren't reaching your observability tool, so check the workload/ManifestWork status on the hub cluster to confirm. A T2 that says "apply failed" means it arrived but didn't apply.
