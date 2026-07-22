# build-tam - the guide

*The companion guide to the live "map your TAM from the terminal" session. A plain-language walkthrough of what this does, why each step exists, and what to do with the list once you have it. For install steps and exact commands, see the [README](../README.md).*

This runs on [CompanyEnrich](https://companyenrich.com) - a B2B data API for company and people data, exposed as an MCP server so an AI agent (Claude Code here) can call it directly. The same data is available through the CoIQ API, so CoIQ users can run this exact process against their stack.

---

## The idea in one sentence

Instead of describing your market with keywords, you **show it 7-10 of your best customers** and it finds every company that looks like them - then ranks that market by who is actually in a position to buy right now, and hands you the people to reach.

## Why closed-won deals are the seed

You start from deals you already won because those are your proven pattern. Successful customers are the clearest description of who you should sell to next - so you feed them in and work backwards: reverse-engineer the profile behind your wins, then go find more companies that match it. You are not guessing at an ICP; you are extracting it from reality.

## The problem it solves

Most prospect lists are built one of two ways, and both leak:

- **Keyword search** ("find fintech SaaS companies") only catches companies that literally use your keyword. It misses the ones that *are* your customer but describe themselves differently, and it lets in noise. In our test run, keyword search returned **347** companies; the lookalike approach off the same profile returned **1,606** - and the keyword list's top result was not even a fit.
- **Static TAM lists** go stale the day they are built and say nothing about *timing* - who has budget and pain this quarter versus who is frozen.

A common mistake is to stop at "this list looks like my closed-won deals, they are in the same industry, done." That gives you a plausible list, not a prioritized one. This process fixes both leaks: it works from examples (so it finds companies that resemble your winners however they describe themselves), then layers live signals on top so you work the accounts that are actually in-market.

## How it works - seven stages

Each stage reads the previous stage's output, saves its own, and points you to the next. You run them in order as slash commands.

| # | Stage | What happens | You get |
|---|-------|--------------|---------|
| 1 | **Segment + seeds** | Enrich your closed-won book, group it into coherent segments, and curate up to 10 clean example customers per segment. | Your seed list |
| 2 | **Reverse-engineer the ICP** | Pull the seeds' full profiles and read off the shared pattern - vertical, business model, size, funding stage, geography, tech maturity, core need, and a one-sentence ICP. | An evidence-backed ICP |
| 3 | **Lookalike expansion** | Feed the seeds to the engine and get the whole market that resembles them, each with an enriched profile and a similarity score. Sized cheaply first, then materialized. | The lookalike market |
| 4 | **Tier scoring (A/B/C)** | Score every account on fit (how much it resembles your winners) plus a growth signal (is it hiring). Hot = both. | Hot / Warm / Nurture tiers |
| 5 | **Workforce ranking** | Re-rank the good-fit accounts by real headcount growth. A funded company adding people is deploying budget - that is the timing signal. | The in-market shortlist |
| 6 | **Decision makers** | Find the buyers at the top accounts, tagged by persona (economic buyer, technical champion, product, risk/compliance), with title, seniority, department, location, and LinkedIn URL. | Named contacts |
| 7 | **Work emails** | Resolve verified work emails for the specific people you will contact. Done last, and only for who you will actually reach, because it is the charged step. | A contactable list |

**A few practical notes from running it:**

- **Segment before you expand.** You *can* throw every seed in at once, but lookalike quality is better when the seeds are one coherent profile - the engine considers all seeds together, so a mixed bag blurs the result. One clean segment at a time wins.
- **Seeds cap at 10 per lookalike.** That is the input limit, and it is plenty - a tight 10 beats a noisy 30.
- **Keep the ICP table even though lookalikes work without it.** Stage 2 is optional to the machine but valuable to the humans - your RevOps, sales, and customer-success teams need that profile in front of them, and it doubles as the reasoning you personalize outreach with.
- **The AI orchestrates each step.** This runs through MCP rather than raw API calls on purpose: an intelligence layer sits between the stages, making judgment calls (which segment, which seeds to drop, which persona) that a fixed script cannot. You can re-run the same workflow with different inputs.
- **Order is flexible.** For example, scoring the tiers before materializing the full list saves a pass. Adjust to your case.

## Why the two signals matter

Fit alone tells you *who looks like a customer*. It does not tell you *who is buying*. In our test run, a third of the "right company" accounts were actually **shrinking** - firmographic targeting alone would have sequenced all of them and spent a third of the effort on companies in a hiring freeze. Stacking a growth signal on top of fit is what separates "looks like our customer" from "is in-market now."

Workforce growth is one signal; it is not the only one. Depending on your offer, the sharpest signal might be:

- **Overall or department-specific hiring** - a growing GTM team means they are investing in that motion.
- **Recent funding** - relevant when your product needs real budget to adopt.
- **Tool-stack engagement** - if they are actively using Clay, an enrichment tool, or an adjacent product, there is a gap you can fill or replace.
- **Content / influencer activity** - useful for partnership and content plays.

Pick the signal that matches what you sell. The pipeline layers it in the same way workforce growth is layered here.

## The proof it works

The strongest evidence is a hold-out test. In our run we seeded the engine with 10 customers and **held back the other 60** closed-won accounts in that segment. Working only from the 10, the lookalike **rediscovered 45 of the 60** it had never been told about - 11 of them in the top 30 results. It reconstructed three-quarters of a book it never saw. Every *other* company on the list has the same claim to your attention.

Two quick ways to sanity-check the output yourself: the similarity percentages track CompanyEnrich's own built-in scoring, and a hold-out like the one above tells you the rediscovery rate on companies you already know the answer for.

## After the list: turning it into outreach

A ranked list is the setup, not the play. What worked in the session:

- **Lead with proof.** Take a customer you did great work for, pull its lookalikes, and go after them with the case study - the results and the pain points you already solved. Mentioning a company you helped (ideally a competitor of the prospect) signals "we could do the same for you," which earns replies.
- **Personalize by persona, not just by company.** A head of marketing and a CEO have different objectives - Stage 6 already tags the persona, so write to it.
- **Give something before asking.** Tease the result and offer the case study as the call to action rather than pushing straight for a meeting. Enough to build trust, not so much they can just do it themselves.
- **Feed the agent a structure that already works.** When an email format converts, save it and hand it to the agent for the next batch - same as reusing a good lookalike query. The system compounds as you teach it what works.

## Practical Q&A (from the session)

- **LinkedIn or email?** Email reaches more people; LinkedIn gets higher reply rates. The best results came from combining them in a connected flow - connect on LinkedIn, then email, then a short LinkedIn message - so your face and company feel familiar before the ask. Relevance beats channel: reach the right person with a real signal and both channels perform.
- **Which signals convert best?** Engagement with an adjacent tool stack was the standout - it surfaces a real product gap. Hiring (especially GTM roles) and funding follow, depending on your offer.
- **How fresh is the data, and how often do I re-run?** Data refreshes on a periodic cadence with some real-time signals for the time-sensitive fields. Re-run the pipeline on a schedule (automated or manual); each run can show the diff against the previous batch so you see what changed.
- **Does coverage work outside the US?** CompanyEnrich sources every active domain (a live website or a Google Maps presence), so coverage is global rather than US-only. As with anything, test it on your own market to confirm fit.

## What you end up with

A ranked, named, contactable list: the companies that look like your best customers, filtered to the ones hiring (and therefore buying), with the right people and their emails attached - ready to hand to outreach, with the case-study angle to personalize it.

## Run it yourself

1. Install the plugin and connect your CompanyEnrich account (see the [README](../README.md)). Optionally connect Airtable for a visual workspace, or use the CSV fallback.
2. Point stage 1 at your own closed-won accounts (an Airtable table, a Google Sheet export, a CRM, or a CSV).
3. Fire the seven commands in order - each one tells you the next.

You bring your own examples and your own accounts; the engine does the expansion, scoring, and contact-finding.
