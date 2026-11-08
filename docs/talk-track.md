# Talk track: Deploy with OCM with confidence

Slot: Mon Nov 9, 2026, 12:06-12:11 pm, Hyatt Regency Level 4, Regency Ballroom B-D.
Target: 4:40 spoken, 20 seconds of buffer. One speaker, own laptop, HDMI.
Last rehearsal ran 5:30, before slide 9 was added. Five minutes is a hard stop, so trim before the next run; the start times below are the 4:40 plan.
CNCF guidance is 3-5 slides; this deck has 10.

| Slide | Starts at | Say |
|---|---|---|
| 1 Title | 0:00 | "Deploy with OCM with confidence. I'm Suvaansh, a software engineer at Guidewire, which builds the software and platform P&C insurers run on, and an Open Cluster Management maintainer. Five minutes on two questions: how long did my workload take to reach the cluster, and did it arrive?" |
| 2 OCM in 20 seconds | 0:15 | "Open Cluster Management is a CNCF Incubating project, now in its sixth year. It's hub and spoke: one hub gives you a centralized view of your entire fleet and delivers work to every cluster through an agent. Both links are on the slide." |
| 3 At Guidewire: the stress this takes away (4 clicks) | 0:35 | Open: "Let me start with our use case at Guidewire: what stress does this take away?" Click 1: "Before using OCM, our CI/CD pipelines deploy straight to every managed cluster. Those pipelines took years to harden. We know their latency and we trust them." Click 2: "Now we're adding a new layer to a pipeline teams already trust." Click 3: "The pipeline applies to an OCM hub cluster and OCM carries the workload to the managed cluster. Same pipeline, one more hop." Click 4: "That hop is the question. How much lag does it add? And did the workload actually arrive? Teams won't move to the hub without the confidence they already have. So we measure the hop and prove every arrival. That's what this talk is about." |
| 4 One hub cluster, many regions (2 clicks) | 1:05 | Open: "That hub serves managed clusters in several regions." Click 1: "Teams apply a workload on the hub and OCM sends it everywhere." Click 2: "The hub can't tell us how long it took to land in us-west or ap-south, or whether it reached eu-west at all." |
| 5 Two timestamps, one key (5 clicks) | 1:30 | Click 1: "A user or a CI/CD pipeline applies a workload/ManifestWork on the hub cluster." Click 2: "The hub cluster's webhook sends a log with the workload/ManifestWork name, generation and a UTC timestamp. That's T1. Both sides log in UTC, so we can compare them directly." Click 3: "The work agent on the managed cluster picks it up over its watch." Click 4: "It applies the workload and sends the same kind of log, with its own timestamp. That's T2. This managed cluster log ships in OCM 1.4; we contributed it upstream." Click 5: "Your observability tool joins the two logs on the key they share: managed cluster, ManifestWork name, generation. Same key means same rollout. Subtract the two UTC timestamps: 434 milliseconds. Same key and no T2 inside the timeout: it never arrived. Nothing on the clusters does the math." |
| 6 Match the two logs | 2:20 | "One workload on one managed cluster, ap-south. The hub cluster log and the managed cluster log carry the same workload name, managed cluster and generation. Generation 1, the first rollout, took 912 milliseconds. Generation 2 was a smaller change and took 434. Generation 3 has a T1 but no T2: it never arrived." |
| 7 Never arrived (2 clicks) | 3:00 | Open: "Here's a workload for eu-west. The hub cluster logged its T1." Click 1: "But no T2. We give it a timeout." Click 2: "Timeout passes, still no T2. That workload never arrived. That's the whole check: a T1 with no T2." |
| 8 Any observability tool | 3:40 | "None of this is tied to a vendor. Find the two logs, match them on managed cluster name, workload/ManifestWork name and generation, subtract. And catch the missing T2: none after a timeout means it never arrived. Any observability tool can do that." |
| 9 Now at Guidewire: one hub, many clusters, full confidence | 4:15 | "So where are we now? At Guidewire we confidently deploy workloads with OCM from the hub to a large number of managed clusters. We clearly see the latency of every rollout, and we can tell when OCM caused a workload not to reach a managed cluster." |
| 10 Thank you | 4:30 | "If you run into any issues, reach us in #open-cluster-mgmt on Kubernetes Slack. And come find me this week at the KubeVela booth, kiosk P-3A, in the Solutions Showcase, Level 1, Hall 5. Thank you." |

## Day of

- Pick up your badge Sunday Nov 8 (Salt Palace, 200 South entrance, 8 AM-5 PM).
- Be in Regency Ballroom B-D by 11:51 AM. Check in at the Speaker Check-In desk at the back, then sit front row, stage right. Not seated when talks start = no-show.
- Bring your laptop, HDMI adapter and a clicker. Open the HTML deck from disk in Chrome, press F, mirror the display.
- No swag during the talk. The talk is recorded for the CNCF YouTube channel.
- After the talk, upload the PDF through the link in the CNCF email for Sessionize.

## Before the review with August and Mike

- Replace the example numbers on slide 6 with real measurements, or keep the "example output" label.
- Confirm they're comfortable with the "contributed by Guidewire" line on slide 5.
- Slide 3 answers the "why" feedback: the direct path is trusted, the OCM hop has to earn the same confidence. Check the wording lands with them.

Regions on slides 2, 3 and 4 are illustrative. Swap them for the real ones if you're comfortable sharing them.

Q&A backup for slide 7: no T2 can also mean the managed cluster's logs aren't reaching your observability tool, so check the workload/ManifestWork status on the hub cluster to confirm. A T2 that says "apply failed" means it arrived but didn't apply.
