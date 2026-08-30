# MCP Tools Reference

## Retrieval Tools

### Vector Search Tool
- **Name**: `vector_search`
- **Input**:
  ```json
  {"query": "string", "top_k": 10, "filters": {}}
  ```
- **Output**:
  ```json
  {"results": [{"clip_id": "string", "score": 0.9, "video_id": "string"}]}
  ```

### BM25 Search Tool
- **Name**: `bm25_search`
- **Input**: `{"query": "string", "top_k": 10}`
- **Output**: Similar to vector search

### RRF Fusion Tool
- **Name**: `rrf_fusion`
- **Input**: `{"result_sets": [], "k": 60}`
- **Output**: `{"results": [{"clip_id": "string", "rrf_score": 0.8}]}`

### Rerank Tool
- **Name**: `rerank_results`
- **Input**: `{"results": [], "query": "string"}`
- **Output**: `{"results": [{"clip_id": "string", "reranked_score": 0.9}]}`

## Vision Tools

### Logo Detection Tool
- **Name**: `logo_detection`
- **Input**:
  ```json
  {"clip_ids": ["clip-001"], "target_brands": ["Adidas", "Nike"]}
  ```
- **Output**:
  ```json
  {"detections": [{"clip_id": "clip-001", "brand": "Adidas", "confidence": 0.9}]}
  ```

### Talent Match Tool
- **Name**: `talent_match`
- **Input**: `{"clip_ids": ["clip-001"], "target_talents": ["Messi"]}`
- **Output**: `{"matches": [{"clip_id": "clip-001", "talent": "Messi", "confidence": 0.9}]}`

### Action Classification Tool
- **Name**: `action_classification`
- **Input**: `{"clip_ids": ["clip-001"], "target_actions": ["drinking"]}`
- **Output**: `{"classifications": [{"clip_id": "clip-001", "action": "drinking"}]}`

## Policy Tools

### Rights Check Tool
- **Name**: `rights_check`
- **Input**:
  ```json
  {"clip_ids": ["clip-001"], "territory": "Germany", "usage_type": "digital_highlights", "duration_seconds": 30}
  ```
- **Output**:
  ```json
  {"results": [{"clip_id": "clip-001", "rights_cleared": true, "explanation": "..."}]}
  ```

### Exclusion Check Tool
- **Name**: `exclusion_check`
- **Input**: `{"clip_ids": ["clip-001"], "excluded_brands": ["Nike"]}`
- **Output**: `{"results": [{"clip_id": "clip-001", "passed": true}]}`

## Output Tools

### Clip Generation Tool
- **Name**: `clip_generation`
- **Input**: `{"video_id": "video-001", "start_time": 0, "end_time": 30}`
- **Output**: `{"clip_id": "clip-001", "status": "generated"}`

### Export Clip Tool
- **Name**: `export_clip`
- **Input**: `{"clip_id": "clip-001", "format": "mp4"}`
- **Output**: `{"download_url": "/downloads/clip-001.mp4"}`