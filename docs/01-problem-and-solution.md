# Niyam: problem and solution

Niyam (Hindi for "rule" or "regulation") is a question-answering system over Indian financial regulation. It answers questions about RBI and SEBI circulars with citations to the source text, and declines to answer when the evidence is not strong enough.

## 1. Problem statement

RBI and SEBI publish regulation as long PDF circulars and master directions. Many are amended, partly withdrawn or superseded by later circulars, so the question "what rule applies today?" often means reading several documents and working out which one wins.

Three things make this hard today:

- **Search is literal.** Keyword search on a website misses paraphrases. A person asking about "know your customer norms for small accounts" may never find the circular that uses different wording.
- **Documents are messy.** Many are scanned or table-heavy PDFs, which plain-text tools handle poorly.
- **General chatbots are unsafe for this.** They answer fluently but may not cite a source, may quote a rule that was later amended, and cannot show which paragraph supports a claim. In compliance work, an uncited answer is not usable.

## 2. Who it is for

- A compliance or risk analyst at a fintech or NBFC who needs to find the governing circular quickly and check the exact wording.
- A founder or product manager checking whether a regulation applies to a planned product.
- A student or professional preparing for a regulatory exam who wants answers tied to the source text.

## 3. Solution overview

Niyam ingests a curated set of public RBI and SEBI circulars, splits them into searchable passages, and answers questions in four steps:

1. **Retrieve.** Combine keyword search and semantic (vector) search, then rerank the candidates.
2. **Generate.** Ask the language model to answer using only the retrieved passages.
3. **Cite.** Attach the source circular, date and passage to every claim.
4. **Verify or refuse.** Check that the answer is supported by the passages. If the evidence is weak or missing, say so instead of guessing.

The system is built as a production-style service: authenticated API, background ingestion, caching, tracing, automated quality checks in CI, and a cloud deployment.

## 4. Goals

- Grounded answers: every answer cites its source or is an explicit refusal.
- Measurable quality: retrieval and answer quality are measured on a labelled question set, and changes are judged by those numbers.
- Model independence: the language model and embedding model are chosen by configuration, with no code changes.
- Production practices: typed code, tests, structured logging, tracing, security controls, containers, CI/CD and a live deployment.
- Explainability: every design choice is recorded in a decision log and can be defended.

## 5. Non-goals

- Niyam does not give legal advice and does not replace reading the original circular.
- It does not cover private documents, internal bank policies or non-Indian regulation in version 1.
- It does not fine-tune models in version 1.
- It does not include multi-tenant billing, or a custom-built frontend beyond a Streamlit interface.

## 6. Initial success targets

These are starting targets, set before any measurement. They will be revised after the baseline evaluation in the evaluation phase, and the final numbers will be reported as results.

| Area           | Initial target                                                     |
| -------------- | ------------------------------------------------------------------ |
| Retrieval      | Recall@5 of at least 0.85 on the labelled question set             |
| Answer quality | Faithfulness (answer supported by retrieved text) of at least 0.85 |
| Citations      | 100% of answers carry citations or are explicit refusals           |
| Latency        | p95 under 6 seconds for uncached requests                          |
| Cost           | Cost per query measured and reported                               |
| Security       | Prompt-injection attack success rate under 5% on the red-team set  |

## 7. Assumptions and risks

| Item                                                        | Handling                                                                             |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Sources are public RBI and SEBI circulars only              | No private or personal data is ingested                                              |
| Scanned PDFs may parse poorly                               | Use a layout-aware parser with OCR fallback, and measure parsing quality on a sample |
| Circulars get superseded                                    | Store issue date and status as metadata, and prefer current documents when answering |
| The language model may still produce unsupported statements | Grounding check, refusal behaviour and faithfulness evaluation                       |
| User questions may contain personal data                    | Redact personal data before logging or tracing                                       |
| Free-tier model and tracing limits                          | Rate limiting, caching, and a configurable fallback model                            |

## 8. Scope of version 1

In scope: ingestion, hybrid retrieval, cited answers with refusals, authentication, evaluation, observability, CI/CD and deployment.
Out of scope for now: fine-tuning, billing, a custom frontend, and non-Indian regulators.
