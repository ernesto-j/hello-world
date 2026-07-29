# ScreenFixed (Brisbane CBD) — pressure-tested valuation

**Business:** ScreenFixed, Level 1, 303 Adelaide St, Brisbane CBD — repair side only
**Date of analysis:** 2026-07-29 · All figures AUD · 20,000 Monte Carlo runs (`model/simulate.py`, seed 42)

---

## TL;DR

Your back-of-envelope ($700K–$1.05M) is **not wrong — it's conditional**, and the condition
is doing all the work. The valuation question collapses to one factual dispute:

- **At your own throughput assumption (6–15 repairs/day)** and ScreenFixed's *actual published
  prices*, revenue is **$370K–$651K (p10–p90, median $498K)** and the business is worth
  **$121K–$466K (median ~$270K)**. Zero of 20,000 runs reach the owner's stated $1.1–1.2M revenue.
- **If the $1.1–1.2M revenue claim is real**, it implies ~20–28 repairs/day (or material mail-in /
  mobile-service volume). Under that scenario — with wages scaled up for the extra techs — the
  valuation is **$499K–$1.22M (median ~$796K)**, and conditioning on revenue actually landing in
  the stated band gives **$586K–$979K (median ~$769K)**. That brackets your original range.

So: **verify revenue before anything else** (BAS/GST lodgements, POS job counts, merchant
statements). Nothing else you could learn about this business moves the number as much.

**Two red flags found during research:**

1. **The "separate" secondhand business isn't separate.** "Screen Fixed", "Mobile Trade"
   (trade.com.au) and "Fixo" (phone-parts wholesaler) are all registered business names of the
   same entity — **Screen Care Pty Ltd, ABN 23 623 258 499** — and trade.com.au's Brisbane store
   operates from the same 303 Adelaide St address ([ABR record](https://abr.business.gov.au/ABN/View?abn=23623258499),
   [trade.com.au](https://www.trade.com.au/)). Any revenue figure the owner quotes must be
   dissected: repair-service revenue vs device-trading revenue vs intercompany parts supply
   (Fixo supplies ScreenFixed itself). This is the most likely innocent explanation for a
   $1.1–1.2M figure that repair jobs alone can't support.
2. **"Operating since 2015" is marketing copy.** The ABN dates from Dec 2017, GST registration
   from Jul 2021, and the "SCREEN FIXED" business name from **Jan 2024**. The "40,000+ customers"
   claim covers the whole 3-city brand (Brisbane, Sydney, Melbourne), not this store. Review
   depth is thin: ~8 reviews on ProductReview (5.0★), ~24 on Trustpilot brand-wide (~4★, snippet-
   derived — direct fetch was blocked). Good reputation, but not a moat a buyer should pay for.

---

## 1. Revenue distribution (Monte Carlo on throughput × ticket mix)

Instead of `mean(triangular) × 300 × $370`, both throughput and the average ticket are
distributions. Trading days were corrected from ~300 to **~250**: the store trades **Mon–Fri
9–5 only, closed weekends and public holidays** ([their own location page](https://www.screenfixed.com.au/locations/brisbane/)).
That correction alone removes ~17% of your assumed revenue.

The ticket is modelled as a mix of five job types priced from **ScreenFixed's own published
price list** ([iPhone price list](https://www.screenfixed.com.au/repairs/price-list-for-iphone-repairs/)):

| Job type | Share of jobs* | Price (low/mode/high) | Basis |
|---|---|---|---|
| Budget screens | 40% | $119 / $149 / $219 | CITED — iPhone 11–14 aftermarket $119–165, iPad 9 $149 |
| Premium screens | 18% | $195 / $279 / $650 | CITED — original-refurb tiers $195–279, iPhone 17 $239–499, Z Fold 6 $899 |
| Tablet screens | 10% | $129 / $179 / $320 | CITED low end; upper end INFERRED |
| Batteries | 17% | $99 / $119 / $139 | CITED — $99–139 across iPhone models |
| Ports & other | 15% | $45 / $129 / $279 | CITED — port cleaning $45–55, port repair $79–279 |

\* Shares are a **GUESS** (no published mix; screens are the most common job globally). The
Dirichlet uncertainty on shares is in the model, and the what-if tool lets you drag them.

**Implied average ticket: $167–$229 (p10–p90), median $193.** This is the pressure-test's
sharpest finding: your model implied **$355–385/job**, which ScreenFixed's own price list
cannot support at any plausible mix — the priciest common repair (original-refurb iPhone
screen) is $279. A $370 average would require most jobs to be foldable/flagship OLED work.

**Result (base case, 6–15 repairs/day):**

| | p10 | p50 | p90 |
|---|---|---|---|
| Jobs/year | 1,973 | 2,566 | 3,213 |
| Revenue | **$370K** | **$498K** | **$651K** |

P(revenue ∈ owner's $1.1–1.2M) = **0.0%**. Either the throughput assumption is ~2.3× too low,
or the revenue figure includes the commingled trading business, or it's inflated.

## 2. Cost stack & SDE

| Item | Low / Mode / High | Basis |
|---|---|---|
| Rent (gross occupancy) | $16K / $28K / $45K | INFERRED→GUESS — see §5 |
| Occupancy extras | $1K / $3K / $6K | GUESS |
| Non-owner wages | $60K / $95K / $150K | GUESS — ~2 named Brisbane techs on about-us; assumes owner works + 1–2 FTE |
| Parts cost | per-category % of price (20–55%) | GUESS — one AU comp lists COGS ~33% of revenue |
| Other opex | 6–14% of revenue | GUESS — insurance, merchant fees, software, marketing, utilities |

**SDE (base case): $62K / $136K / $224K (p10/p50/p90); margin median 27%** — inside your
assumed 25–35%, so your margin instinct was fine. The problem was never margin; it's revenue.

P(SDE < 0) ≈ 0.4%.

## 3. Valuation distribution

Multiple modelled as triangular **1.3× / 2.0× / 2.8×** (see §4).

| Scenario | p10 | p50 | p90 |
|---|---|---|---|
| **A. Your throughput (6–15/day), real prices** | **$121K** | **$270K** | **$466K** |
| B. Owner's revenue true (16–28/day, premium-tilted mix, wages scaled to $140–260K) | $499K | $796K | $1.22M |
| B, conditioned on revenue ∈ $1.1–1.2M | $586K | $769K | $979K |

P(valuation ∈ your original $700K–$1.05M | scenario A) ≈ **0.6%**.

Honest read on the confidence interval: even within one scenario the p10–p90 spans ~4× (A) or
~2.4× (B), and the scenario choice itself is worth ~$500K. Anyone quoting this business at a
±10% precision is selling false comfort. The distribution, not a point, is the answer.

Charts: `model/outputs/revenue_dist.png`, `sde_dist.png`, `valuation_dist.png`, `tornado.png`.
Raw numbers: `model/outputs/results.json`.

## 4. Comps: is 2–3× SDE right? (No — it's the top of the range.)

Researched and then **adversarially verified** (each load-bearing claim re-fetched):

| Comp | Figures | Implied multiple | Status |
|---|---|---|---|
| [BizBuySell phone & computer repair benchmark](https://www.bizbuysell.com/learning-center/valuation-benchmarks/phone-computer-repair/) (US, 2021–25 solds) | median sale $170K, median SDE $88K | **median 1.54×, avg 1.94×, IQR 1.17–2.40×** | CONFIRMED (US data — AU applicability is judgement) |
| [LINK Business, 2 Sydney shops](https://linkbusiness.com.au/business-for-sale/2-mobile-phone-repair-shops-for-sale/) | ask $260K, rev $620K, SDE $150K (3-yr avg, broker-labelled SDE) | **1.73×** | CONFIRMED by direct fetch |
| [SEEK Business, Wetherill Park NSW](https://www.seekbusiness.com.au/business-listing/mobile-phone-repair-shop-for-sale/745391) | ask $80K, rev $400K, net $127K | **0.63×** | CONFIRMED — likely distressed/high-rent outlier |
| [North Lakes QLD](https://soldonnet.com.au/search/Businessdetail.asp?ID=33360&customerID=95895241) | ask $110K, rev $180–210K, owner return ~$100K | **~1.1×** | CONFIRMED — but 491-visa-eligible, price distorted |
| AU generic small-biz guides ([businessforsale.com.au](https://www.businessforsale.com.au/business-advice/how-much-is-my-business-worth-a-general-guide-for-australian-owners), [bsale](https://bsale.com.au/repair-for-sale-business)) | — | 1.5–3.0× SDE typical; comparable trades 1.5–2.5× | CITED, not repair-specific |

The verifier also **refuted** one researcher claim (a "300% multiple cyclicality" narrative not
present in its cited source) — dropped. Verifier's recommendation, adopted here:
**low 1.3× / mode 2.0× / high 2.8×**, where the low and mode are evidence-anchored and the
high end requires demonstrable management depth (not pure owner-dependency). Asking prices
≠ sold prices, and most AU listings hide financials — the honest sample is small.

**Verdict on your 2–3× assumption: high.** 3× has essentially no comp support for an
owner-operated single-site repair shop; 2× is defensible as a *mode*, not a floor. These are
asking/benchmark multiples — completed AU sales data for this exact sector wasn't findable.

## 5. Rent reality check (Adelaide St, Level 1)

No listing for Level 1/303 Adelaide St itself was findable. Anchors (all via
realcommercial/commercialrealestate listings and [McGees market note](https://www.bne.mcgees.com.au/post?post_id=14399)):

- Ground-floor Brisbane CBD retail: **$530–$1,850/sqm/yr gross** (CITED, wide quality range)
- Actual Level 1 CBD comp: 458–460 George St, 200sqm at **$250/sqm net** (CITED) — upper floors
  rent at a heavy discount to ground
- The subject building is a small heritage strata block; a suite in it was once marketed as
  **"Cheapest Rent in CBD"** (CITED, old listing)
- Estimated gross occupancy for a 40–70sqm Level 1 tenancy: **$16K / $28K / $45K per year**
  (**GUESS-grade synthesis** of the above — the researcher could not source the upper-floor
  discount percentage directly)

Folded into the cost stack explicitly (not buried in margin). Note it's small: rent moves the
valuation ~±$20K, an order of magnitude less than throughput. CBRE Brisbane retail reports
(Q1 2025–Q1 2026) confirm rents rising and vacancy falling (17.5–18.5%), so bias the range up
slightly at lease renewal.

## 6. Sensitivity — your hypothesis, tested

> "My hypothesis is margin and ticket mix dominate the digital/foot-traffic factors."

**Refuted.** One-at-a-time p10→p90 swings (base case, others at median ~$270K):

| Rank | Input | Valuation swing |
|---|---|---|
| 1 | **Repairs per day** (the foot-traffic factor) | **±$131K** |
| 2 | Price: premium screens | ±$59K |
| 3 | SDE multiple | ±$56K |
| 4 | Non-owner wages | ±$51K |
| 5 | Price: ports & other | ±$35K |
| 6 | Price: budget screens | ±$32K |
| 7 | Mix: premium share | ±$27K |
| 8–10 | Parts %, other opex | ±$22–23K each |

Spearman rank correlations against valuation agree: repairs/day 0.73, avg ticket 0.43,
multiple 0.30, wages −0.27. Throughput out-moves the next factor ~2:1; ticket-mix components
are collectively second; margin inputs are mid-table; rent and trading days are noise.
Practical translation: **a POS job-count report is worth more than every other diligence
document combined.**

## 7. What's cited vs guessed (summary)

- **CITED:** trading days (Mon–Fri), all repair prices, the SDE-multiple evidence base, the
  Level 1 George St rent comp, ground-floor CBD rent ranges, ABN/entity structure, review counts.
- **INFERRED:** rent range for the subject tenancy, brand-wide vs store-level customer claims,
  Trustpilot figures (fetch-blocked, snippet-derived).
- **GUESSED:** job-mix shares, parts-cost %, wages, other-opex %, and above all
  **repairs/day — the single input that dominates the answer and the one with no evidence
  behind it at all.**

## 8. Re-running with real figures

- Offline: edit `model/params.yaml`, run `python3 model/simulate.py` (needs numpy, matplotlib, pyyaml).
- Interactive: open `whatif.html` (no install, no network needed) — tweak drivers, watch the
  distributions move, then "Copy parameters" to export JSON back into the yaml.
- Presets in the tool: *Base case* (this document's scenario A), *Owner optimistic* (what must
  be true for the revenue claim), *Conservative*.

---

*Research: 4 web-research agents + 1 adversarial verification agent (2026-07-29); modelling and
synthesis as described above. This is an analytical aid, not a formal business valuation or
financial advice.*
