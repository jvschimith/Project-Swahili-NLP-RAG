# Page Inspection and Extraction

`PageInspector` records canonical link, HTML language, title, OpenGraph values,
JSON-LD types, semantic containers, paragraph/link/script counts, feed and
sitemap hints, and dynamic-page signals. Recommendations are heuristic evidence.

The implemented extraction order is JSON-LD article body, semantic `<article>`,
meaningful `<main>`, then filtered unique paragraphs. JSON-LD supports nested
objects, arrays and `@graph`, and recognizes Article, NewsArticle,
ReportageNewsArticle and BlogPosting. Malformed JSON-LD is ignored safely.

Script-heavy pages with insufficient static text return
`dynamic_browser_required`; no browser is installed or required. Future browser
inspection should remain optional and focus on rendered/public request evidence.
