---
description: Stage 6 of build-tam - find decision makers at the target accounts via search_people, tagged by buyer persona.
argument-hint: [account set, e.g. "A+B" or "top20"]
---

You are running **Stage 6 (Decision Makers)** of the `build-tam` pipeline. Load the `build-tam` skill for the persona→params mapping and the `domains` max-100 chunking rule.

Steps:
1. Decide the account set from `$ARGUMENTS` (default: the A+B accounts from the workforce-ranked table). Collect their domains; chunk into ≤100 per `search_people` call.
2. Ensure a **Decision Makers** table exists mapping personas → `search_people` params (create if missing): GTM Economic Buyer, Technical Champion, Product Buyer, Risk/Compliance Buyer.
3. Run **one `search_people` call per persona per chunk** using the seniority+department params from the skill (2 credits/person). For each returned person, find the matched current experience whose `company.domain` is a target; derive the persona from that `department`. Cap ~1-2 per company per persona.
4. Write a **`<Segment> - Decision Makers (People)`** table: Name, Title, Company, Domain, Persona, Seniority, Department, LinkedIn, Location, plus an empty **Email** column and a **PersonID** column (holds the CompanyEnrich person id for the email stage).
5. Report counts per persona and companies covered.

End with: `Next: /get-emails` (resolve work emails for the people you'll actually contact).
