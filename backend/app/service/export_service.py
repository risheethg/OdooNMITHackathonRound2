import csv
import io
import inspect
from datetime import datetime
from typing import Tuple, List

from fastapi import HTTPException, status
from pymongo.database import Database

from app.repo.manufacture_repo import ManufacturingOrderRepository
from app.core.logger import logs


class ExportService:
    """
    Service to export Manufacturing Orders as CSV or PDF if the MO status is 'done'.
    """

    def __init__(self, db: Database):
        self.mo_repo = ManufacturingOrderRepository(db)

    async def export(self, mo_id: str, fmt: str) -> Tuple[bytes, str, str]:
        """
        Export a manufacturing order as the requested format if it's completed.

        Returns: (content_bytes, filename, mime_type)
        """
        logs.define_logger(20, f"Export requested for MO {mo_id} as {fmt}", loggName=inspect.stack()[0])

        order = self.mo_repo.get_by_id(mo_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturing Order not found.")

        if order.get("status") != "done":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Manufacturing Order must be 'done' to export.")

        if fmt == "csv":
            content = self._generate_csv(order)
            filename = f"mo_{mo_id}.csv"
            mime = "text/csv"
            return content, filename, mime
        elif fmt == "pdf":
            content = self._generate_pdf(order)
            filename = f"mo_{mo_id}.pdf"
            mime = "application/pdf"
            return content, filename, mime
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported export format. Use 'csv' or 'pdf'.")

    def _generate_csv(self, order: dict) -> bytes:
        """Generate a single-row CSV with key MO details."""
        output = io.StringIO()
        writer = csv.writer(output)

        bom = order.get("bom_snapshot", {}) or {}
        components = bom.get("components", []) or []
        operations = bom.get("operations", []) or []

        headers = [
            "mo_id",
            "product_id",
            "quantity_to_produce",
            "status",
            "created_at",
            "updated_at",
            "components_count",
            "operations_count",
        ]
        writer.writerow(headers)

        def fmt_dt(val):
            if isinstance(val, datetime):
                return val.isoformat()
            return str(val) if val is not None else ""

        row = [
            order.get("_id", ""),
            order.get("product_id", ""),
            order.get("quantity_to_produce", ""),
            order.get("status", ""),
            fmt_dt(order.get("created_at")),
            fmt_dt(order.get("updated_at")),
            len(components),
            len(operations),
        ]
        writer.writerow(row)
        return output.getvalue().encode("utf-8")

    def _generate_pdf(self, order: dict) -> bytes:
        """
        Generate a minimal single-page PDF with MO details using raw PDF syntax.
        No external libraries required.
        """

        def esc(text: str) -> str:
            return (text or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        def fmt_dt(val):
            if isinstance(val, datetime):
                return val.isoformat()
            return str(val) if val is not None else ""

        bom = order.get("bom_snapshot", {}) or {}
        components = bom.get("components", []) or []
        operations = bom.get("operations", []) or []

        lines: List[str] = [
            "Manufacturing Order Report",
            f"MO ID: {order.get('_id', '')}",
            f"Product ID: {order.get('product_id', '')}",
            f"Quantity To Produce: {order.get('quantity_to_produce', '')}",
            f"Status: {order.get('status', '')}",
            f"Created At: {fmt_dt(order.get('created_at'))}",
            f"Updated At: {fmt_dt(order.get('updated_at'))}",
            f"Components: {len(components)} | Operations: {len(operations)}",
        ]

        # Build content stream for PDF
        content_lines = [
            "BT",            # Begin text object
            "/F1 12 Tf",     # Font Helvetica, size 12
            "72 740 Td",     # Move to (72, 740)
            "14 TL",         # Set leading to 14
        ]
        for line in lines:
            content_lines.append(f"({esc(line)}) Tj")
            content_lines.append("T*")  # Move to next line
        content_lines.append("ET")      # End text object

        content_stream = ("\n".join(content_lines) + "\n").encode("latin-1")

        # PDF objects
        obj1 = b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
        obj2 = b"2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n"
        obj3 = b"3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>>\nendobj\n"
        obj4 = (
            f"4 0 obj\n<</Length {len(content_stream)}>>\nstream\n".encode("latin-1")
            + content_stream + b"endstream\nendobj\n"
        )
        obj5 = b"5 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\nendobj\n"

        parts = []
        header = b"%PDF-1.4\n"
        parts.append(header)

        # Compute offsets
        offsets = [0]  # object 0 is free
        current_offset = len(header)

        for obj in (obj1, obj2, obj3, obj4, obj5):
            offsets.append(current_offset)
            parts.append(obj)
            current_offset += len(obj)

        xref_offset = current_offset
        # Build xref table
        xref_lines = [b"xref\n", f"0 {len(offsets)}\n".encode("latin-1")]
        # Free entry
        xref_lines.append(b"0000000000 65535 f \n")
        # In-use entries
        for off in offsets[1:]:
            xref_lines.append(f"{off:010} 00000 n \n".encode("latin-1"))
        parts.extend(xref_lines)

        # Trailer
        trailer = (
            b"trailer\n" +
            f"<</Size {len(offsets)} /Root 1 0 R>>\n".encode("latin-1") +
            b"startxref\n" +
            f"{xref_offset}\n".encode("latin-1") +
            b"%%EOF\n"
        )
        parts.append(trailer)

        return b"".join(parts)
