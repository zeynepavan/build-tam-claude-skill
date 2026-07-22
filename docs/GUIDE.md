# build-tam - the guide

*A plain-language walkthrough of what this does and how it works. For the install steps and exact commands, see the [README](../README.md).*

---

## The idea in one sentence

Instead of describing your market with keywords, you **show it 7-10 of your best customers** and it finds every company that looks like them - then ranks that market by who's actually in a position to buy right now, and hands you the people to email.

## The problem it solves

Most prospect lists are built one of two ways, and both leak:

- **Keyword search** ("find fintech SaaS companies") only catches companies that literally use your keyword. It misses the ones that *are* your customer but describe themselves differently, and it lets in noise. In our test run, the keyword approach found **347** companies; the lookalike approach off the same profile found **1,606** - and the keyword list's top result wasn't even a fit.
- **Static TAM lists** go stale the day they're built and tell you nothing about *timing* - who has budget and pain this quarter versus who's frozen.

This fixes both: it works from examples (so it finds companies that resemble your winners, however they describe themselves), and it layers a live buying signal on top (so you work the accounts that are actually in-market).

## How it works - seven stages

Each stage reads the previous stage's output and produces one table. You run them in order.

| # | Stage | What happens | You get |
|---|-------|--------------|---------|
| 1 | **Segment + seeds** | Pick one coherent slice of your closed-won book and curate 7-10 clean example customers. A tight, consistent set beats a big noisy one. | Your seed list |
| 2 | **Reverse-engineer the ICP** | Pull the seeds' full profiles and read off the shared pattern - size, geography, funding stage, tech, core need. You don't *write* the ICP; you *derive* it from who already bought. | An evidence-backed ICP |
| 3 | **Lookalike expansion** | Feed the seeds to the engine and get the whole market that resembles them. This is your real TAM - sized cheaply first, then materialized. | The lookalike market |
| 4 | **Tier scoring (A/B/C)** | Score every account on two things: how much it resembles your winners (right company?) **and** whether it's growing its headcount (in-market now?). Hot = both. | Hot / Warm / Nurture tiers |
| 5 | **Workforce ranking** | Rank the good-fit accounts by real hiring growth, computed from monthly headcount history. This is the timing signal - a funded company that's adding people is deploying budget. | The in-market shortlist |
| 6 | **Decision makers** | Find the actual buyers at the top accounts, sorted by persona (economic buyer, technical champion, product, risk/compliance). | Named contacts |
| 7 | **Work emails** | Resolve verified work emails for the specific people you'll contact. Done last, and only for who you'll actually email, because it's the costly step. | A contactable list |

## Why the two signals matter

Fit alone tells you *who looks like a customer*. It doesn't tell you *who's buying*. In our test run, a third of the "right company" accounts were actually **shrinking** - firmographic targeting alone would have sequenced all of them and burned a third of the effort on companies in a hiring freeze. Stacking a growth signal on top of fit is what separates "looks like our customer" from "is in-market now."

## The proof it actually works

The strongest evidence is a hold-out test. In our run we seeded the engine with 10 customers and **held back the other 60** closed-won accounts in that segment. Working only from the 10, the lookalike **rediscovered 45 of the 60** it had never been told about - 11 of them in the top 30 results. It reconstructed three-quarters of a book it never saw. Every *other* company on the list has the same claim to your attention.

## What you end up with

A ranked, named, contactable list: the companies that look like your best customers, filtered to the ones hiring (and therefore buying), with the right people and their emails attached - ready to hand to outreach.

## Run it yourself

1. Install the plugin and connect your CompanyEnrich account (see the [README](../README.md)).
2. Point stage 1 at your own closed-won accounts (an Airtable table or a CSV).
3. Fire the seven commands in order - each one tells you the next.

You bring your own examples and your own accounts; the engine does the expansion, scoring, and contact-finding.
