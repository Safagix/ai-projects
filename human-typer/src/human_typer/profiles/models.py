from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class TypingProfile(BaseModel):
    name: str = Field(default="default", min_length=1, max_length=64)

    key_hold_mean: float = Field(default=0.065, ge=0.005, le=0.500)
    key_hold_std: float = Field(default=0.025, ge=0.001, le=0.200)

    char_interval_mean: float = Field(default=0.110, ge=0.010, le=0.500)
    char_interval_std: float = Field(default=0.045, ge=0.001, le=0.200)

    word_pause_mean: float = Field(default=0.160, ge=0.010, le=1.000)
    word_pause_std: float = Field(default=0.050, ge=0.001, le=0.200)

    medium_pause_mean: float = Field(default=0.600, ge=0.100, le=3.000)
    medium_pause_std: float = Field(default=0.180, ge=0.010, le=1.000)
    medium_pause_every: int = Field(default=12, ge=3, le=10000)

    long_pause_mean: float = Field(default=2.500, ge=0.500, le=10.000)
    long_pause_std: float = Field(default=0.800, ge=0.050, le=3.000)
    long_pause_every: int = Field(default=45, ge=10, le=10000)

    typo_probability: float = Field(default=0.025, ge=0.0, le=0.300)
    typo_correction_delay_mean: float = Field(default=0.250, ge=0.020, le=1.000)
    typo_correction_delay_std: float = Field(default=0.080, ge=0.005, le=0.300)

    long_word_threshold: int = Field(default=8, ge=3, le=30)
    long_word_slowdown: float = Field(default=1.25, ge=1.0, le=3.0)

    sentence_end_pause: float = Field(default=0.350, ge=0.050, le=2.000)

    training_samples: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _validate_pause_ordering(self) -> TypingProfile:
        if self.long_pause_mean <= self.medium_pause_mean:
            raise ValueError("long_pause_mean must exceed medium_pause_mean")
        if self.long_pause_every <= self.medium_pause_every:
            raise ValueError("long_pause_every must exceed medium_pause_every")
        return self
