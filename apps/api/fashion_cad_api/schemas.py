from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

ProductType = Literal["upper_garment", "laptop_bag"]
Mode = Literal["local_private", "hybrid", "cloud_creative"]


class Measurements(BaseModel):
    chest_mm: float | None = Field(default=None, gt=0)
    body_length_mm: float | None = Field(default=None, gt=0)
    laptop_width_mm: float | None = Field(default=None, gt=0)
    laptop_height_mm: float | None = Field(default=None, gt=0)
    laptop_depth_mm: float | None = Field(default=None, gt=0)


class CreateDesignRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    product_type: ProductType
    mode: Mode = "local_private"
    description: str = Field(default="", max_length=4000)
    measurements_mm: Measurements = Field(default_factory=Measurements)
    materials: list[str] = Field(default_factory=list, max_length=20)
    components: list[str] = Field(default_factory=list, max_length=30)
    cloud_consent: bool = False

    @model_validator(mode="after")
    def local_mode_never_has_cloud_consent(self) -> "CreateDesignRequest":
        if self.mode == "local_private" and self.cloud_consent:
            raise ValueError("El modo local privado no permite consentimiento cloud.")
        return self


class OperationRequest(BaseModel):
    kind: Literal[
        "add_component",
        "remove_component",
        "set_materials",
        "set_measurement",
        "set_description",
        "set_mode",
    ]
    value: str | float | list[str]
    note: str = Field(default="", max_length=500)


class DesignResponse(BaseModel):
    id: str
    name: str
    product_type: ProductType
    mode: Mode
    description: str
    measurements_mm: Measurements
    materials: list[str]
    components: list[str]
    revision: int
    approval_state: Literal["draft", "review", "approved"]
    confidence: Literal["manual", "local_assisted", "cloud_assisted"]
    missing: list[str]
    created_at: datetime
    updated_at: datetime


class AssistantRequest(BaseModel):
    message: str = Field(min_length=3, max_length=1000)


class AssistantResponse(BaseModel):
    message: str
    actions: list[str]
    design: DesignResponse


class ExportResponse(BaseModel):
    project_id: str
    revision: int
    artifacts: list[str]


class OperatorSessionRequest(BaseModel):
    requested_windows: list[Literal["Fashion CAD Studio", "Blender", "Fashion CAD Pattern Viewer"]]


class OperatorSessionResponse(BaseModel):
    session_id: str
    expires_at: datetime
    operator_enabled: bool
    allowed_windows: list[str]
    state: Literal["active", "paused"]


OperatorIntent = Literal["edit", "export", "print", "cloud", "overwrite"]


class OperatorActionRequest(BaseModel):
    session_id: str
    window_name: Literal["Fashion CAD Studio", "Blender", "Fashion CAD Pattern Viewer"]
    x: int | None = Field(default=None, ge=0, le=3840)
    y: int | None = Field(default=None, ge=0, le=2160)
    key: str | None = Field(default=None, min_length=1, max_length=40)
    text: str | None = Field(default=None, min_length=1, max_length=200)
    intent: OperatorIntent = "edit"
    confirmation_id: str | None = None


class OperatorConfirmationRequest(BaseModel):
    session_id: str
    window_name: Literal["Fashion CAD Studio", "Blender", "Fashion CAD Pattern Viewer"]
    intent: Literal["export", "print", "cloud", "overwrite"]
    summary: str = Field(min_length=3, max_length=300)


class OperatorConfirmationResponse(BaseModel):
    confirmation_id: str
    expires_at: datetime


class OperatorAuditResponse(BaseModel):
    id: str
    session_id: str
    action: str
    window_name: str | None
    outcome: str
    details: dict[str, Any]
    created_at: datetime


class RagDocumentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=100_000)
    source: str = Field(default="manual", max_length=500)


class RagImportRequest(BaseModel):
    relative_path: str = Field(min_length=1, max_length=300)


class RagResult(BaseModel):
    title: str
    source: str
    excerpt: str
    score: float
    source_page: int | None = None
    chunk_number: int | None = None
    chunk_id: str | None = None


class CapabilityResponse(BaseModel):
    local_mode: bool
    cloud_mode: bool
    operator_enabled: bool
    models: list[dict[str, Any]]


class JobCreateRequest(BaseModel):
    kind: Literal["model_inference", "embedding_index", "blender_render", "voice_transcription"]
    payload: dict[str, Any] = Field(default_factory=dict)
    gpu_exclusive: bool = False


class JobResponse(BaseModel):
    id: str
    kind: str
    status: Literal["queued", "running", "completed", "failed", "cancelled"]
    gpu_exclusive: bool
    payload: dict[str, Any]
    progress: int = Field(ge=0)
    total: int | None = Field(default=None, ge=0)
    message: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime

class CloudConsentRequest(BaseModel):
    asset_id: str = Field(min_length=1, max_length=200, pattern=r"^[A-Za-z0-9._ -]+$")
    provider: Literal["openai", "deepseek", "trellis_provider"]
    purpose: str = Field(min_length=3, max_length=500)
    estimated_cost_usd: float = Field(ge=0, le=1000)
    approved: bool


class CloudConsentResponse(BaseModel):
    id: str
    design_id: str
    asset_id: str
    provider: str
    purpose: str
    estimated_cost_usd: float
    approved: bool
    created_at: datetime

class BriefRequest(BaseModel):
    description: str = Field(min_length=3, max_length=4000)
    product_type: ProductType | None = None


class ProductBrief(BaseModel):
    product_type: ProductType
    confirmed: dict[str, Any]
    estimated: dict[str, Any]
    missing: list[str]
    next_question: str | None = None
