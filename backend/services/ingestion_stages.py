from enum import Enum


class IngestionStage(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    NORMALIZING = "normalizing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


STAGE_PROGRESS = {
    IngestionStage.UPLOADED: 5,
    IngestionStage.PARSING: 10,
    IngestionStage.NORMALIZING: 40,
    IngestionStage.CHUNKING: 50,
    IngestionStage.EMBEDDING: 60,
    IngestionStage.INDEXING: 85,
    IngestionStage.COMPLETED: 100,
}