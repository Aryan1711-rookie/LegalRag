from enum import Enum


class IngestionStage(str, Enum):

    UPLOADED = "uploaded"
    QUEUED = "queued"
    PARSING = "parsing"
    NORMALIZING = "normalizing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


STAGE_PROGRESS = {
    IngestionStage.UPLOADED: 5,
    IngestionStage.QUEUED: 5,
    IngestionStage.PARSING: 10,
    IngestionStage.NORMALIZING: 30,
    IngestionStage.CHUNKING: 45,
    IngestionStage.EMBEDDING: 60,
    IngestionStage.INDEXING: 90,
    IngestionStage.COMPLETED: 100,
    IngestionStage.FAILED: 0
}