"""
Unit tests for antifraud_rag/schemas.py - Pydantic models/schemas.
"""

from uuid import UUID

import pytest
from pydantic import ValidationError

from antifraud_rag.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    DirectHitData,
    MatchedCase,
    RAGPromptContext,
    RAGPromptData,
)


class TestAnalysisRequest:
    """Tests for AnalysisRequest schema."""

    def test_valid_request(self):
        """Test valid analysis request."""
        request = AnalysisRequest(text="Test fraud text", source="api")
        assert request.text == "Test fraud text"
        assert request.source == "api"

    def test_request_required_text_field(self):
        """Test analysis request requires text field."""
        with pytest.raises(ValidationError) as exc_info:
            AnalysisRequest()
        assert any(err["loc"] == ("text",) for err in exc_info.value.errors())

    def test_request_optional_metadata(self):
        """Test analysis request with optional metadata."""
        request = AnalysisRequest(text="Test text")
        assert request.source == "user_submission"  # default


class TestMatchedCase:
    """Tests for MatchedCase schema."""

    def test_valid_matched_case(self):
        """Test valid matched case."""
        case = MatchedCase(
            case_id=UUID("12345678-1234-5678-1234-567812345678"),
            description="Fraud case description",
            confidence=0.95,
            fraud_type="phone_scam",
            key_indicators=["urgent", "money"],
        )
        assert case.confidence == 0.95
        assert case.fraud_type == "phone_scam"

    def test_matched_case_defaults(self):
        """Test matched case default values."""
        case = MatchedCase(
            case_id=UUID("12345678-1234-5678-1234-567812345678"),
            description="Description",
            confidence=0.5,
        )
        assert case.fraud_type is None
        assert case.key_indicators == []

    def test_matched_case_requires_fields(self):
        """Test matched case requires case_id, description, and confidence."""
        with pytest.raises(ValidationError):
            MatchedCase(description="Test")


class TestDirectHitData:
    """Tests for DirectHitData schema."""

    def test_valid_direct_hit_data(self):
        """Test valid direct hit data."""
        case = MatchedCase(
            case_id=UUID("12345678-1234-5678-1234-567812345678"),
            description="Test",
            confidence=0.9,
        )
        data = DirectHitData(
            risk_level="HIGH",
            matched_cases=[case],
            recommended_action="报警",
        )
        assert data.risk_level == "HIGH"
        assert len(data.matched_cases) == 1

    def test_direct_hit_defaults(self):
        """Test direct hit data default values."""
        case = MatchedCase(
            case_id=UUID("12345678-1234-5678-1234-567812345678"),
            description="Test",
            confidence=0.9,
        )
        data = DirectHitData(matched_cases=[case])
        assert data.risk_level == "HIGH"
        assert data.recommended_action == "停止一切操作，立即报警"


class TestRAGPromptContext:
    """Tests for RAGPromptContext schema."""

    def test_valid_context(self):
        """Test valid RAG prompt context."""
        context = RAGPromptContext(
            relevant_cases=[{"description": "Case 1", "fraud_type": "scam"}],
            anti_fraud_tips=[{"title": "Tip 1", "content": "Be careful"}],
        )
        assert len(context.relevant_cases) == 1
        assert len(context.anti_fraud_tips) == 1

    def test_context_empty_lists(self):
        """Test context with empty lists."""
        context = RAGPromptContext(relevant_cases=[], anti_fraud_tips=[])
        assert context.relevant_cases == []
        assert context.anti_fraud_tips == []


class TestRAGPromptData:
    """Tests for RAGPromptData schema."""

    def test_valid_rag_data(self):
        """Test valid RAG prompt data."""
        data = RAGPromptData(
            risk_level="MEDIUM",
            rrf_score=0.75,
            prompt="分析这个请求",
            context=RAGPromptContext(relevant_cases=[], anti_fraud_tips=[]),
        )
        assert data.risk_level == "MEDIUM"
        assert data.rrf_score == 0.75

    def test_rag_data_defaults(self):
        """Test RAG data default values."""
        data = RAGPromptData(
            rrf_score=0.5,
            prompt="Test prompt",
            context=RAGPromptContext(relevant_cases=[], anti_fraud_tips=[]),
        )
        assert data.risk_level == "MEDIUM"


class TestAnalysisResponse:
    """Tests for AnalysisResponse schema."""

    def test_direct_hit_response(self):
        """Test AnalysisResponse with DirectHit data."""
        case = MatchedCase(
            case_id=UUID("12345678-1234-5678-1234-567812345678"),
            description="Test",
            confidence=0.9,
        )
        response = AnalysisResponse(
            status="success",
            result_type="Direct_Hit",
            data=DirectHitData(matched_cases=[case]),
        )
        assert response.status == "success"
        assert response.result_type == "Direct_Hit"

    def test_rag_prompt_response(self):
        """Test AnalysisResponse with RAG prompt data."""
        response = AnalysisResponse(
            status="success",
            result_type="RAG_Prompt",
            data=RAGPromptData(
                rrf_score=0.6,
                prompt="分析",
                context=RAGPromptContext(relevant_cases=[], anti_fraud_tips=[]),
            ),
        )
        assert response.result_type == "RAG_Prompt"

    def test_response_default_status(self):
        """Test response has default status."""
        response = AnalysisResponse(
            result_type="Direct_Hit",
            data=DirectHitData(matched_cases=[]),
        )
        assert response.status == "success"
