import os
from decimal import Decimal
from datetime import date

import pytest

from app.utils.security import get_password_hash, verify_password
from app.utils import document_generator
from app.utils import email as email_utils
from app.models.alert import AlertType
from app.models.contract import Contract, ContractType


def test_security_hash_and_verify():
    pw = "minhasenha123"
    hashed = get_password_hash(pw)
    assert isinstance(hashed, str) and len(hashed) > 0
    assert verify_password(pw, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_security_long_password_truncation():
    # bcrypt has a 72-byte limit; ensure long passwords are handled without exception
    long_pw = "a" * 200
    hashed = get_password_hash(long_pw)
    assert verify_password(long_pw, hashed) is True


def test_document_generator_monkeypatch(monkeypatch, tmp_path):
    # monkeypatch DocxTemplate used inside document_generator to avoid requiring real docx files
    class FakeDoc:
        def __init__(self, path):
            self.path = path
            self.rendered = None

        def render(self, data):
            self.rendered = data

        def save(self, dest):
            content = b"FAKE-DOCX-BYTES:" + str(self.rendered).encode("utf-8")
            # dest may be a file-like object (BytesIO) or a path
            if hasattr(dest, "write"):
                dest.write(content)
            else:
                with open(dest, "wb") as f:
                    f.write(content)

    monkeypatch.setattr(document_generator, "DocxTemplate", FakeDoc)

    data = {"name": "Test"}

    # case 1: no output_path -> returns bytes from BytesIO
    res = document_generator.generate_contract_pdf("fake_template.docx", data)
    assert isinstance(res, (bytes, bytearray))
    assert b"FAKE-DOCX-BYTES" in res

    # case 2: with output_path -> file written and bytes returned
    out = tmp_path / "out.docx"
    res2 = document_generator.generate_contract_pdf("fake_template.docx", data, output_path=str(out))
    assert isinstance(res2, (bytes, bytearray))
    assert out.exists()


def test_email_rendering_and_subject():
    # Create a minimal Contract object in-memory
    contract = Contract(
        id=1,
        title="Test Contract",
        client_name="Client",
        end_date=date.today(),
        contract_type=ContractType.SERVICE,
        value=Decimal("1234.56"),
        currency="EUR",
        start_date=date.today(),
        created_by=1,
    )

    html = email_utils.render_contract_expiry_html(contract, 5, AlertType.T_MINUS_10, language="de")
    assert isinstance(html, str)
    assert "Test Contract" in html

    subj = email_utils.get_email_subject_by_type(AlertType.T_MINUS_10, "Test Contract", language="de")
    assert isinstance(subj, str)
    # ensure the subject mentions the relative days or contains expected wording
    assert "10" in subj or "T-10" in subj
