# Search discovery rollout

## Positioning

Use **S++ (ServPP)** when introducing the project. S++ remains the language name; ServPP is a searchable alternate spelling. Describe the project as an experimental role-oriented language for business systems. Do not describe the compiler as open source or imply that a public SDK distribution exists.

Initial topic choices are editorial hypotheses, not measured search volumes or ranking promises:

| Search intent | Terms | Destination |
| --- | --- | --- |
| Find the project | S++ programming language; ServPP | `/` |
| Understand the approach | business modeling language; role-oriented programming | `/guide/`, `/articles/role-oriented-order-lifecycle/` |
| Separate business and realization | business logic and database design; separate business logic from infrastructure | `/articles/business-logic-and-database-design/` |
| Model consistency | business transaction modeling; transaction boundaries | `/articles/business-transactions-and-infrastructure/` |
| Evaluate concrete behavior | Petstore business modeling; banking deposit modeling | `/examples/`, `/sources/` |

## Published changes

- Clear brand/category titles and visible alternate spelling on the homepage.
- Unique page descriptions, canonical URLs, Open Graph and text sharing summaries.
- Homepage `WebSite` structured data with S++ and ServPP names; article structured data with actual publication dates and project authorship.
- Three original English articles, an article index, homepage reading cards and navigation from the other pages.
- Source and book links inside the articles, with explicit implementation limits rather than claims of universal production readiness.
- A sitemap containing the article routes and all other public HTML pages; downloads remain excluded from crawling through robots.txt.
- Publication checks reject GitHub links, missing metadata and broken local links. Book copyright remains reserved-rights, with its notice served locally.

No analytics tracker, paid advertising, automated external posting or fake rating/review data is introduced. Site-name and article structured data communicate facts; they do not guarantee a particular search appearance.

## Account-dependent setup

Use an owner-controlled Google account. Do not commit account credentials, browser sessions or authentication cookies. A Google HTML verification tag is public website content and can be committed when supplied by the owner.

1. In [Search Console](https://search.google.com/search-console/), add the URL-prefix property `https://us.servpp.top/` (including HTTPS and trailing slash).
2. Choose **HTML tag** under the alternative verification methods. Send the public `google-site-verification` tag to the website maintainer, or let the maintainer operate a browser after the owner has logged in.
3. Put that exact tag inside the maintained homepage `<head>` in `website/static/index.html`. Build, check and publish. Keep the tag in future builds because Google may recheck it.
4. Click **Verify** in Search Console. A site being reachable is not evidence that this verification succeeded; retain the actual verification result.
5. Under **Sitemaps**, submit `sitemap.xml`. Confirm the submitted URL is `https://us.servpp.top/sitemap.xml` and inspect its eventual fetch result.
6. Use **URL inspection** for the homepage, `/articles/`, the three article pages and `/book/`. Run the live test and request indexing where available. Retain the actual response; do not claim that requesting indexing guarantees inclusion.

Account verification and Search Console submission must be reported separately from successful website deployment. Without an authenticated owner session, their status is **pending**, even if all website checks pass.

### HTML file verification

The owner selected Google's HTML-file method for this rollout. The supplied public file `google7f75a76777f31f44.html` is maintained under `website/static/` and served verbatim at the website root. It has been fetched over HTTPS with status 200 and checked against the original bytes. The builder must not add a title, canonical link or other page metadata to this file, and the file is not an article or sitemap entry. Keep it when publishing future site versions.

The owner confirmed successful Search Console ownership verification on October 16, 2026. This confirmation is separate from the HTTPS check of the file. The HTML-tag procedure above remains an alternative for future owners.

## Rollout evidence — October 16, 2026

The search changes and three articles were published from revision `55190ce`. The corresponding GitHub Actions run `38843452296` passed. The 176 public content pages have distinct titles and descriptions, canonical URLs, sharing metadata and valid local links. The site sitemap has 176 unique page entries, including all three articles. All 299 publication files at that stage matched their local generated SHA-256 values; no HTML page linked to GitHub or returned a `noindex` response header.

Desktop and mobile browser checks covered the homepage, article index and all three articles. The live mobile route from homepage to article index to transaction article passed without browser errors or document overflow. These are website checks, not evidence of a real Googlebot visit or inclusion in Google's index. Ownership verification has been confirmed by the owner. The owner also confirmed submitting the correct `https://us.servpp.top/sitemap.xml` URL on October 16, 2026. Google's sitemap processing result has not been independently observed. The owner attempted a manual indexing request and reported “Oops! Something went wrong — We had a problem submitting your indexing request. Please try again later.” That request did not succeed; the generic message does not establish its cause.

## Measure and improve

After verification, use Search Console's Page indexing and Performance reports. Keep a first 28-day baseline of impressions, clicks and actual search queries; low or absent initial data is not a reason to invent demand estimates. Segment brand searches (ServPP and S++) from topic searches.

Review which pages are indexed, which queries bring relevant readers and whether visitors reach the guide, examples or contact link. Improve articles around questions that actual evaluators ask. Add a new article only when it provides a concrete explanation or example; do not create near-duplicate pages for spelling variants.

The public source browser remains available without linking to the GitHub repository. Prepare external promotional posts from `promotion-copy.md`, then publish only through owner-approved accounts and channels.

## Official references

- [Google's technical requirements](https://developers.google.com/search/docs/essentials/technical)
- [Site names and alternate names](https://developers.google.com/search/docs/appearance/site-names)
- [Titles](https://developers.google.com/search/docs/appearance/title-link)
- [Descriptions](https://developers.google.com/search/docs/appearance/snippet)
- [Ownership verification](https://support.google.com/webmasters/answer/9008080)
- [Sitemap submission](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Requesting a recrawl](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)

### Distinguish the two Search Console inputs

Submit only `sitemap.xml` (or its complete URL when the field has no fixed prefix) under **Sitemaps**. The owner encountered “Sitemap is HTML” after submitting `/book/` there; that URL is a normal page, not a sitemap. Remove erroneous page submissions from the Sitemaps report. Normal page URLs belong in the top **URL inspection** field, where the owner can request indexing. The corrected sitemap submission has been confirmed; it does not by itself establish that Google has indexed any page.

### Manual indexing request failure

Following the owner-reported submission error, live checks again returned HTTP 200 for the homepage, robots.txt and sitemap.xml. The homepage had no noindex metadata or X-Robots-Tag header, its canonical URL was correct, and robots.txt allowed public page crawling. These checks do not prove that Google can fetch the page from its own network. Use Search Console's **Test live URL** result for that distinction: a successful live test plus a failed request is different from a fetch or crawlability failure. Manual requests are optional, have submission quotas and do not guarantee inclusion. Keep the submitted sitemap in place; avoid repeated retries, and retry the homepage later if desired. Do not alter valid site files merely to suppress this generic Search Console message.
