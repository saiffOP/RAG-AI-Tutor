# RAG AI Tutor

A production-oriented Retrieval-Augmented Generation (RAG) system for educational question answering, built from scratch using Python, OpenAI, Pinecone, BM25, Reciprocal Rank Fusion (RRF), and FastAPI.

The system ingests course material from PDFs, PowerPoint presentations, and web pages, retrieves relevant information using hybrid semantic + keyword search, and generates grounded answers with source citations.

No LangChain or LlamaIndex is used — the RAG pipeline is implemented directly in Python.

---

## Overview

The RAG AI Tutor allows students to ask questions about course material and receive answers grounded in the available learning resources.

The current knowledge base contains content across four course areas:

- Machine Learning
- Deep Learning
- Natural Language Processing
- Large Language Models

Instead of relying only on the LLM's internal knowledge, the system retrieves relevant course content first and provides that evidence to the generation model.

This helps produce answers that are more relevant, traceable, and grounded in the supplied course material.

---

## Key Features

- Multi-source ingestion for PDF, PPTX, and web content
- Structure-aware document processing
- OpenAI embeddings
- Pinecone vector storage
- Semantic vector search
- BM25 keyword retrieval
- Hybrid retrieval using Reciprocal Rank Fusion (RRF)
- Course-level metadata filtering
- Grounded LLM answer generation
- Inline source citations
- PDF page and PowerPoint slide references
- Persistent lexical corpus for BM25
- Separate offline indexing and online query pipelines
- FastAPI REST API
- Pydantic request/response validation
- Health-check endpoint
- No LangChain/LlamaIndex dependency

---

## Architecture

The system separates knowledge-base indexing from runtime question answering.

### Offline Indexing

```text
PDF ───────┐
PPTX ──────┼──> Ingestion & Processing
Web ───────┘
                     |
                     v
              Retrieval Units
                 /       \
                /         \
               v           v
       OpenAI Embeddings   Persisted Corpus
               |                 |
               v                 v
            Pinecone            BM25
```

### Online RAG Pipeline

```text
                    User Question
                         |
              +----------+----------+
              |                     |
              v                     v
       OpenAI Embedding          BM25 Search
              |
              v
       Pinecone Semantic
            Search
              |                     |
              +----------+----------+
                         |
                         v
                        RRF
                         |
                         v
                      Top-K
                         |
                         v
                  Context Builder
                         |
                         v
                       OpenAI
                         |
                         v
              Grounded Answer
                 + Citations
                         |
                         v
                      FastAPI
```

---

## Structure-Aware Ingestion

Different source formats are processed according to their natural structure instead of applying the same fixed chunking strategy to every document.

### PDF

The course PDFs are structured as question-answer material.

Each question and its corresponding answer are preserved as a single retrieval unit.

```text
Question
   +
Answer
   ↓
Retrieval Unit
```

This prevents related questions and answers from being separated unnecessarily.

### PowerPoint

Each slide represents a natural content boundary, so each slide becomes an individual retrieval unit.

```text
Slide
  ↓
Retrieval Unit
```

### Web Content

Web pages are generally longer and less consistently structured.

The HTML is cleaned and the extracted content is split into smaller text chunks suitable for retrieval.

```text
HTML
 ↓
Clean Text
 ↓
Text Chunking
 ↓
Retrieval Units
```

---

## Knowledge Base

The current dataset produces:

| Course | Retrieval Units |
|---|---:|
| DL201 | 130 |
| LLM401 | 175 |
| ML101 | 118 |
| NLP301 | 137 |
| **Total** | **560** |

The knowledge base contains retrieval units from:

- PDF documents
- PowerPoint presentations
- Technical web resources

Each unit includes metadata such as:

```text
unit_id
document_id
course_id
source_type
source_name
page_number
slide_number
source_url
text
metadata
```

---

## Embeddings and Vector Storage

Retrieval units are converted into embeddings using the OpenAI Embeddings API.

The current embedding representation contains 1536 dimensions.

The vectors are stored in Pinecone together with source metadata.

```text
Retrieval Unit
      |
      v
OpenAI Embedding
      |
      v
1536-dimensional Vector
      |
      v
Pinecone
```

The current Pinecone namespace is:

```text
course-content
```

Indexing is performed in batches to make ingestion more reliable and efficient.

---

## Hybrid Retrieval

The project combines two retrieval techniques.

### 1. Semantic Search

The user's question is converted into an embedding and compared with vectors stored in Pinecone.

This allows the system to retrieve information based on semantic meaning even when the wording differs.

### 2. BM25 Keyword Search

BM25 provides lexical retrieval and is useful when queries contain exact terminology such as:

```text
DBSCAN
Conv2D
transformer
embedding
```

### Why Use Both?

Semantic retrieval is strong at understanding meaning.

BM25 is strong at matching important words and technical terms.

Using both provides complementary retrieval signals.

---

## Reciprocal Rank Fusion (RRF)

Semantic search and BM25 produce different types of scores, so their raw scores are not directly combined.

Instead, the project uses Reciprocal Rank Fusion.

RRF combines results based on their ranking positions.

```text
Semantic Results        BM25 Results
       |                     |
       +----------+----------+
                  |
                  v
                 RRF
                  |
                  v
          Combined Ranking
```

The highest-ranked results are then used as context for generation.

---

## Grounded Answer Generation

The final retrieved results are converted into structured context.

Each source receives an identifier:

```text
[S1]
[S2]
[S3]
...
```

The generation model receives:

```text
System Instructions
        +
User Question
        +
Retrieved Context
```

The model is instructed to:

- Answer using only the supplied course context
- Avoid inventing unsupported information
- State when the available context is insufficient
- Use only valid source IDs
- Cite the evidence supporting its claims

Example:

```text
Using a student's final exam score as an input can cause data
leakage because that information would not be available at
prediction time [S3].
```

The API also returns the corresponding source metadata so the citation can be traced back to the original material.

---

## Metadata Filtering

Retrieval can optionally be restricted to a particular course.

Example:

```json
{
  "question": "What is data leakage?",
  "course_id": "ML101"
}
```

This restricts retrieval to ML101 content.

Without a course filter, the system can search across the complete knowledge base.

---

## Offline Indexing vs Runtime Retrieval

A key design decision is separating document processing from the live RAG application.

Documents are processed only when the knowledge base is built or updated.

### Indexing

```text
Source Documents
      ↓
Ingestion
      ↓
Retrieval Units
      ↓
      ├──> OpenAI Embeddings ──> Pinecone
      |
      └──> retrieval_units.json
```

The processed retrieval units are persisted locally for BM25.

### Runtime

When the application starts:

```text
Load retrieval_units.json
        ↓
Build BM25 index
        ↓
Connect to Pinecone
        ↓
Initialize OpenAI services
        ↓
RAG Service Ready
```

The original PDFs, presentations, and websites are therefore not reprocessed for every user request.

---

## FastAPI Service

The RAG pipeline is exposed through a REST API built with FastAPI.

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Ask a Question

```http
POST /ask
```

Example request:

```json
{
  "question": "Why is it a problem to use a student's final exam marks to predict whether they will pass?",
  "course_id": "ML101"
}
```

Example response:

```json
{
  "question": "Why is it a problem to use a student's final exam marks to predict whether they will pass?",
  "answer": "Using a student's final exam mark as a feature causes data leakage because it would not be available at prediction time [S3].",
  "sources": [
    {
      "source_id": "S3",
      "unit_id": "ML101:01_ML_Fundamentals:q7",
      "course_id": "ML101",
      "source_type": "pdf",
      "source_name": "01_ML_Fundamentals.pdf",
      "page_number": 4,
      "slide_number": null,
      "source_url": null
    }
  ]
}
```

---

## Project Structure

```text
rag-ai-tutor/
│
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── schemas.py
│   │
│   ├── ingestion/
│   │   ├── models.py
│   │   ├── pdf_loader.py
│   │   ├── pptx_loader.py
│   │   ├── web_loader.py
│   │   └── pipeline.py
│   │
│   ├── chunking/
│   │
│   ├── embeddings/
│   │   └── openai_embeddings.py
│   │
│   ├── indexing/
│   │   └── indexer.py
│   │
│   ├── vectorstore/
│   │   └── pinecone_store.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── bm25_retriever.py
│   │   ├── hybrid_retriever.py
│   │   └── fusion.py
│   │
│   ├── generation/
│   │   ├── context_builder.py
│   │   └── generator.py
│   │
│   ├── rag/
│   │   └── service.py
│   │
│   └── storage/
│       └── corpus_store.py
│
├── data/
│   ├── ML101/
│   ├── DL201/
│   ├── NLP301/
│   ├── LLM401/
│   └── index/
│       └── retrieval_units.json
│
├── scripts/
│   ├── index_knowledge_base.py
│   ├── test_embeddings.py
│   ├── test_pinecone.py
│   ├── test_retrieval.py
│   ├── test_ingestion_pipeline.py
│   └── test_rag.py
│
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-ai-tutor
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

Do not commit `.env` or API keys to source control.

---

## Build the Knowledge Base

After adding or updating course content, run:

```bash
python -m scripts.index_knowledge_base
```

The indexing pipeline:

1. Processes PDF, PPTX, and web sources
2. Creates retrieval units
3. Generates OpenAI embeddings
4. Upserts vectors into Pinecone
5. Persists the processed corpus for BM25 retrieval

Normal API requests do not rerun this ingestion pipeline.

---

## Run the API

Start FastAPI using Uvicorn:

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Example RAG Flow

For a question such as:

```text
Why is using a student's final exam score to predict whether
they will pass a problem?
```

the application performs:

```text
Question
   ↓
OpenAI Query Embedding
   ↓
Pinecone Semantic Search
   +
BM25 Keyword Search
   ↓
RRF
   ↓
Top Relevant Retrieval Units
   ↓
Context Builder
   ↓
OpenAI Generation
   ↓
Grounded Answer + Citations
```

---

## Design Decisions

### Why not use fixed chunking for everything?

The source material already contains useful semantic boundaries.

Preserving question-answer pairs and individual slides provides more meaningful retrieval units than blindly splitting every source by a fixed number of tokens.

Generic chunking is used where the source does not provide reliable natural boundaries, such as longer web content.

### Why hybrid retrieval?

Semantic and lexical retrieval solve slightly different problems.

Pinecone provides semantic similarity, while BM25 improves exact keyword and technical-term matching.

### Why RRF?

BM25 and vector similarity scores use different scoring systems.

RRF combines rankings rather than attempting to directly compare incompatible raw scores.

### Why no reranker?

A reranking stage was considered, but the hybrid retrieval pipeline already produced strong Top-K results for the current knowledge base.

A reranker would introduce additional latency and complexity and can be added later if evaluation shows that relevant candidates are being retrieved but ranked poorly.

### Why no LangChain?

The project intentionally implements the RAG components directly in Python.

For the current scope, this keeps the retrieval and generation logic explicit, provides direct control over each stage, and avoids adding an orchestration abstraction that is not required.

---

## Current Status

Implemented:

- [x] PDF ingestion
- [x] PPTX ingestion
- [x] Web ingestion
- [x] Structure-aware retrieval units
- [x] OpenAI embeddings
- [x] Pinecone vector indexing
- [x] Persistent BM25 corpus
- [x] Semantic retrieval
- [x] BM25 retrieval
- [x] Reciprocal Rank Fusion
- [x] Metadata filtering
- [x] Grounded generation
- [x] Source citations
- [x] FastAPI service
- [x] Health endpoint
- [x] Question-answer endpoint

Planned improvements:

- [ ] Golden evaluation dataset
- [ ] Recall@K / Precision@K / MRR retrieval evaluation
- [ ] Faithfulness and answer-relevance evaluation
- [ ] Citation correctness evaluation
- [ ] Latency monitoring
- [ ] Token and cost monitoring
- [ ] Response caching
- [ ] Structured application logging
- [ ] Docker containerization
- [ ] AWS deployment

---

## Evaluation Plan

The next stage of the project separates retrieval evaluation from generation evaluation.

### Retrieval

Planned metrics include:

- Hit Rate@K
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)

### Generation

Planned metrics include:

- Faithfulness
- Answer relevance
- Citation correctness
- Unsupported claim / hallucination rate

A labelled golden dataset will be used so that improvements to retrieval or generation can be measured rather than judged only from individual examples.

---

## Future Improvements

Beyond the current implementation:

- Automated evaluation pipeline
- Query/result caching
- Latency and cost observability
- Prompt-injection safeguards for retrieved content
- Improved insufficient-context detection
- Docker deployment
- AWS hosting
- Optional reranking if evaluation demonstrates a measurable benefit
- Incremental document re-indexing

---

## Tech Stack

**Language:** Python

**LLM & Embeddings:** OpenAI

**Vector Database:** Pinecone

**Keyword Retrieval:** BM25

**Rank Fusion:** Reciprocal Rank Fusion (RRF)

**API:** FastAPI

**Server:** Uvicorn

**Document Processing:** PDF, PPTX, HTML/Web

---

## Project Goal

The goal of this project is not simply to connect an LLM to a vector database.

It demonstrates an end-to-end RAG architecture covering:

**ingestion → structure-aware processing → embeddings → vector storage → hybrid retrieval → rank fusion → grounded generation → citations → API serving**

with a clear separation between offline knowledge-base indexing and online question answering.