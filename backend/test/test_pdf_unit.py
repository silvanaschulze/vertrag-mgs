"""
Testes unitários básicos para integração PDF.
Basic unit tests for PDF integration.
"""
import os
import tempfile
import shutil
from datetime import datetime, date, timezone
from pathlib import Path
import hashlib

import pytest

from app.schemas.contract import ContractCreate, ExtractionMetadata


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF"


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory for testing"""
    temp_dir = tempfile.mkdtemp()
    upload_dir = Path(temp_dir) / "uploads" / "contracts"
    upload_dir.mkdir(parents=True, exist_ok=True)
    yield str(upload_dir)
    shutil.rmtree(temp_dir)


def test_extraction_metadata_schema():
    """Test ExtractionMetadata schema validation"""
    # Valid metadata
    valid_meta = ExtractionMetadata(
        original_file_name="test.pdf",
        original_file_storage_name="1_123456789_test.pdf",
        original_file_sha256="a" * 64,  # Valid SHA256
        ocr_text="Sample text",
        ocr_text_sha256="b" * 64,
        uploaded_at=datetime.now(timezone.utc)
    )
    
    assert valid_meta.original_file_name == "test.pdf"
    assert valid_meta.original_file_sha256 == "a" * 64
    assert valid_meta.original_file_sha256 is not None
    assert len(valid_meta.original_file_sha256) == 64


def test_contract_create_with_metadata():
    """Test ContractCreate with extraction_metadata field"""
    extraction_meta = ExtractionMetadata(
        original_file_name="contract.pdf",
        original_file_storage_name="1_123456789_contract.pdf",
        original_file_sha256="abc123" * 10 + "abcd",  # 64 char hash
        ocr_text="Contract content",
        ocr_text_sha256="def456" * 10 + "efgh",
        uploaded_at=datetime.now(timezone.utc)
    )
    
    contract: ContractCreate = ContractCreate(  # type: ignore[call-arg]
        title="Test Contract with PDF",
        start_date=date(2025, 1, 1),
        client_name="Test Client",
        extraction_metadata=extraction_meta
    )
    
    # Verify metadata is properly attached
    assert contract.extraction_metadata is not None
    assert contract.extraction_metadata.original_file_name == "contract.pdf"
    if contract.extraction_metadata.original_file_sha256:
        assert contract.extraction_metadata.original_file_sha256.startswith("abc123")
        assert len(contract.extraction_metadata.original_file_sha256) == 64


def test_contract_create_without_metadata():
    """Test ContractCreate works without extraction_metadata"""
    contract: ContractCreate = ContractCreate(  # type: ignore[call-arg]
        title="Regular Contract",
        start_date=date(2025, 1, 1),
        client_name="Regular Client"
    )
    
    # Should create contract successfully
    assert contract.title == "Regular Contract"
    assert contract.client_name == "Regular Client"
    
    # extraction_metadata should be None
    assert contract.extraction_metadata is None


def test_pdf_hash_calculation(sample_pdf_content):
    """Test SHA256 hash calculation for PDF content"""
    file_hash = hashlib.sha256(sample_pdf_content).hexdigest()
    assert len(file_hash) == 64
    assert file_hash.isalnum()
    
    # Test OCR text hash
    ocr_text = "Sample extracted text from PDF"
    normalized_text = " ".join(ocr_text.lower().split())
    ocr_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
    assert len(ocr_hash) == 64
    assert ocr_hash != file_hash  # Should be different


def test_file_operations(temp_upload_dir, sample_pdf_content):
    """Test file saving and reading in upload directory"""
    filename = "test_contract.pdf"
    file_path = Path(temp_upload_dir) / filename
    
    # Write file
    with open(file_path, "wb") as f:
        f.write(sample_pdf_content)
    
    # Verify file exists
    assert file_path.exists()
    assert file_path.is_file()
    
    # Read file back
    with open(file_path, "rb") as f:
        read_content = f.read()
    
    assert read_content == sample_pdf_content
    
    # Verify hash matches
    original_hash = hashlib.sha256(sample_pdf_content).hexdigest()
    read_hash = hashlib.sha256(read_content).hexdigest()
    assert original_hash == read_hash


def test_duplicate_detection_logic(sample_pdf_content):
    """Test duplicate detection logic without database"""
    # Create same content with different filenames
    file1_content = sample_pdf_content
    file2_content = sample_pdf_content  # Same content
    file3_content = b"Different PDF content"
    
    # Calculate hashes
    hash1 = hashlib.sha256(file1_content).hexdigest()
    hash2 = hashlib.sha256(file2_content).hexdigest()
    hash3 = hashlib.sha256(file3_content).hexdigest()
    
    # Same content should have same hash (duplicates)
    assert hash1 == hash2
    
    # Different content should have different hash
    assert hash1 != hash3
    assert hash2 != hash3


def test_ocr_text_normalization():
    """Test OCR text normalization for duplicate detection"""
    # Different formatting, same content
    text1 = "This is a contract with some content"
    text2 = "This  is   a  contract    with  some content"  # Extra spaces
    text3 = "THIS IS A CONTRACT WITH SOME CONTENT"  # Upper case
    text4 = "This is a different contract"  # Different content
    
    # Normalize function (same as in contracts_import.py)
    def normalize_text(text: str) -> str:
        return " ".join(text.lower().split())
    
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    norm3 = normalize_text(text3)
    norm4 = normalize_text(text4)
    
    # Same content should normalize to same text
    assert norm1 == norm2
    assert norm1 == norm3
    
    # Different content should normalize differently
    assert norm1 != norm4
    
    # Calculate hashes
    hash1 = hashlib.sha256(norm1.encode("utf-8")).hexdigest()
    hash2 = hashlib.sha256(norm2.encode("utf-8")).hexdigest()
    hash3 = hashlib.sha256(norm3.encode("utf-8")).hexdigest()
    hash4 = hashlib.sha256(norm4.encode("utf-8")).hexdigest()
    
    # Same normalized content should have same hash
    assert hash1 == hash2 == hash3
    
    # Different normalized content should have different hash
    assert hash1 != hash4


def test_upload_file_naming_convention():
    """Test upload file naming convention"""
    user_id = 123
    timestamp = 1700000000
    original_filename = "my_contract.pdf"
    
    # Simulate naming convention from contracts_import.py
    storage_name = f"{user_id}_{timestamp}_{original_filename}"
    expected = "123_1700000000_my_contract.pdf"
    
    assert storage_name == expected
    
    # Test file path construction
    upload_dir = "/uploads/contracts"
    full_path = os.path.join(upload_dir, storage_name)
    expected_path = "/uploads/contracts/123_1700000000_my_contract.pdf"
    
    assert full_path == expected_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])