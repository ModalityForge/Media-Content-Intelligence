# Dataset Inventory and Annotation Guide

Dataset binaries are local working assets, not repository content. The `.gitignore` excludes raw, processed, indexed, and restricted data.

## Local layout

```text
data/
├── raw/
│   └── ad_subset/                       Advertisement media subset
└── restricted/
    └── social_media_influencer/
        ├── catalog.json                 Cross-dataset inventory
        ├── manual_drop/                 Licensed manual archives, if any
        └── datasets/
            ├── microlens_50k/
            │   ├── raw/videos/
            │   ├── raw/metadata/
            │   ├── virality_metrics.csv
            │   ├── annotations_index.json
            │   ├── annotation_assets.json
            │   └── DATASET_INFO.md
            └── snapugc/
                ├── raw/videos/
                ├── raw/metadata/
                ├── virality_metrics.csv
                ├── annotations_index.json
                ├── annotation_assets.json
                ├── failed_downloads.json
                └── DATASET_INFO.md
```

## Current local inventory

| Dataset | Local items | Approximate size | Joined annotations | Intended project use |
|---|---:|---:|---|---|
| Advertisement subset | 63 local files | 109 MiB | Source-dependent manifests | Ad/logo/OCR/creative-content experiments |
| MicroLens-50K subset | 100 videos | 254.1 MiB cataloged | `likes`, `views`, `title`, source archive member, hashes | Popularity priors, semantic retrieval, multimodal indexing |
| SnapUGC subset | 30 videos | 59.5 MiB cataloged | `ecr`, optional `title`/`description`, split, source URL, hashes | Five-second retention/engagement prediction and short-video retrieval |

The complete social-media directory occupies approximately 331 MB in decimal units. Exact current values are recorded in `data/restricted/social_media_influencer/catalog.json`.

## Annotation semantics

### MicroLens

- `likes` and `views` are collection-time snapshots, not live counters.
- `title` is textual content supplied by the published dataset.
- `source_url`, `archive_member`, and `archive_disk` preserve provenance.
- `sha256` verifies the locally extracted video.
- Large user-video interaction pairs are optional via `--include-interactions` and are excluded from the compact subset by default.

Useful derived features include `log1p(views)`, `log1p(likes)`, `likes / max(views, 1)`, title embeddings, topic labels, OCR/title agreement, and content-versus-popularity evaluations.

### SnapUGC

- `ecr` is the published engagement continuation rate for training items.
- `title` and `description` are sparse; blank values mean the source record did not provide them.
- `split` identifies the source annotation split.
- `source_url` is the publisher-provided CDN URL.
- `failed_downloads.json` records stale or invalid media links so repeat runs can skip them.
- The public CSVs inspected by the downloader do not expose NAWP labels, even though the paper describes NAWP as a metric.

ECR can be used as a supervised regression target for opening-hook or first-five-second retention models. Do not combine it directly with MicroLens likes/views as if they were the same measurement.

## Download commands

MicroLens compact subset:

```bash
python scripts/download_socmed_dataset.py \
  --datasets microlens \
  --microlens-variant 50k \
  --size-budget-mb 450 \
  --max-videos 100 \
  --max-file-mb 5 \
  --accept-research-terms
```

SnapUGC compact subset:

```bash
python scripts/download_socmed_dataset.py \
  --datasets snapugc \
  --size-budget-mb 150 \
  --max-videos 30 \
  --max-file-mb 3 \
  --accept-research-terms
```

Advertisement downloader options:

```bash
python scripts/download_ad_datasets.py --help
```

## Connecting data to MCI

The downloaders prepare media and annotation manifests; they do not automatically populate the application indexes. A complete integration should:

1. Register each `raw/videos/*` asset through `components/ingestion/`.
2. Generate frames, audio, transcripts, OCR, and captions through `components/preprocessing/` and `components/indexing/`.
3. Preserve the source `video_id` when writing metadata and vector indexes.
4. Store engagement fields as metadata features, not as relevance ground truth.
5. Split evaluation by creator, topic, or time when those identifiers are available to reduce leakage.
6. Keep derived outputs outside the immutable `raw/` directory.

## Rights and publication boundary

MicroLens is academic-research-only and prohibits unauthorized modification or redistribution of its videos. SnapUGC is a published research dataset whose source media should likewise not be republished from this repository. Review each publisher’s current terms before use.

Consequently:

- Do not commit dataset videos, archives, generated catalogs containing restricted records, or derived media.
- Do not publish creator identities or infer sensitive traits.
- Keep checksums and provenance locally for auditability.
- Commit processing code so authorized users can reproduce their own local subset.
