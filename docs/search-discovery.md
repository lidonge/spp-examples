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
