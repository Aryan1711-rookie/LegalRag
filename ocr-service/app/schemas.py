from pydantic import BaseModel

class OCRBlock(BaseModel):
    label: str
    reading_order: int
    bbox: list[float]

    html: str 
    confidence: float | None = None

    skipped: bool = False
    error: bool = False

class OCRPage(BaseModel):
    page_number: int
    image_bbox: list[float]
    text:str
    blocks: list[OCRBlock]
    preprocessing: dict | None = None

class OCRResponse(BaseModel):
    status: str
    engine: str
    model: str
    filename: str
    total_pages: int
    execution_time_seconds: float
    pages: list[OCRPage]
