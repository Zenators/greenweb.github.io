from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def rupiah(value):
    return "Rp {:,.0f}".format(float(value or 0)).replace(",", ".")


def safe_text(value):
    return escape(str(value if value is not None else "-"))


def format_date(value):
    if not value:
        return "-"

    return value.strftime("%d-%m-%Y %H:%M")


def create_pdf(title, subtitle, elements, pagesize=A4):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="GreenRoots",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="GreenTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#236B45"),
        alignment=TA_CENTER,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="GreenSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=18,
    ))

    story = [
        Paragraph("GreenRoots", styles["GreenTitle"]),
        Paragraph(title, styles["Heading2"]),
        Paragraph(subtitle, styles["GreenSubtitle"]),
        Spacer(1, 5),
    ]

    story.extend(elements)

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Dokumen ini dibuat secara otomatis oleh sistem GreenRoots.",
        styles["Italic"],
    ))

    document.build(story)

    buffer.seek(0)
    return buffer.getvalue()


def generate_user_orders_pdf(user, orders):
    from reportlab.lib.styles import ParagraphStyle

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(
            f"Nama Pengguna: {safe_text(user.name)}",
            styles["Normal"],
        ),
        Paragraph(
            f"Email: {safe_text(user.email)}",
            styles["Normal"],
        ),
        Paragraph(
            f"Tanggal Laporan: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"],
        ),
        Spacer(1, 15),
    ]

    data = [[
        "ID",
        "Program",
        "Jumlah",
        "Total",
        "Status",
        "Tanggal",
    ]]

    grand_total = 0

    for order in orders:
        grand_total += float(order.total_price or 0)

        data.append([
            f"#{order.id}",
            Paragraph(
                safe_text(order.program.name if order.program else "-"),
                ParagraphStyle(
                    "ProductCell",
                    parent=styles["Normal"],
                    fontSize=8,
                ),
            ),
            str(order.quantity),
            rupiah(order.total_price),
            safe_text(order.status),
            format_date(order.created_at),
        ])

    if not orders:
        data.append(["-", "Belum ada pesanan", "-", "-", "-", "-"])

    table = Table(
        data,
        colWidths=[12*mm, 48*mm, 17*mm, 28*mm, 30*mm, 35*mm],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#236B45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F2F7F3"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(
        f"<b>Total seluruh pesanan: {rupiah(grand_total)}</b>",
        styles["Normal"],
    ))

    return create_pdf(
        "Laporan Riwayat Pesanan",
        "Laporan seluruh pesanan pengguna",
        elements,
    )


def generate_single_order_pdf(user, order):
    styles = getSampleStyleSheet()

    payment = order.payment

    elements = [
        Paragraph(
            f"Nama Pengguna: {safe_text(user.name)}",
            styles["Normal"],
        ),
        Paragraph(
            f"Email: {safe_text(user.email)}",
            styles["Normal"],
        ),
        Spacer(1, 12),
        Paragraph("DETAIL PESANAN", styles["Heading2"]),
    ]

    details = [
        ["Nomor Pesanan", f"#{order.id}"],
        ["Tanggal Pesanan", format_date(order.created_at)],
        ["Nama Program", safe_text(order.program.name if order.program else "-")],
        ["Jumlah Unit", str(order.quantity)],
        ["Jumlah Pohon", str(order.quantity * order.trees_per_unit)],
        ["Harga per Unit", rupiah(order.unit_price)],
        ["Biaya Penanaman", rupiah(order.service_fee)],
        ["Biaya Pengiriman", rupiah(order.delivery_fee)],
        ["Total Pembayaran", rupiah(order.total_price)],
        ["Status Pesanan", safe_text(order.status)],
        [
            "Metode Penanaman",
            "Ditanamkan GreenRoots"
            if order.planting_type == "greenroots"
            else "Ditanam Sendiri",
        ],
        [
            "Metode Pembayaran",
            safe_text(payment.payment_method if payment else "-"),
        ],
        [
            "Status Pembayaran",
            safe_text(payment.status if payment else "Belum ada pembayaran"),
        ],
        ["Lokasi Penanaman", safe_text(order.planting_location)],
        ["Alamat Pengiriman", safe_text(order.delivery_address)],
    ]

    table = Table(details, colWidths=[55*mm, 105*mm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF3EC")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    if order.plantings:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(
            "RIWAYAT PENANAMAN",
            styles["Heading2"],
        ))

        planting_data = [[
            "Lokasi",
            "Jumlah",
            "Status",
            "Tanggal",
        ]]

        for planting in order.plantings:
            planting_data.append([
                safe_text(planting.location),
                str(planting.planted_quantity),
                safe_text(planting.status),
                format_date(planting.planting_date),
            ])

        planting_table = Table(
            planting_data,
            colWidths=[65*mm, 25*mm, 35*mm, 35*mm],
            repeatRows=1,
        )

        planting_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#236B45")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))

        elements.append(planting_table)

    return create_pdf(
        f"Laporan Pesanan #{order.id}",
        "Detail transaksi pengguna GreenRoots",
        elements,
    )


def generate_admin_orders_pdf(orders):
    styles = getSampleStyleSheet()

    data = [[
        "ID",
        "Pengguna",
        "Program",
        "Jumlah",
        "Total",
        "Pesanan",
        "Pembayaran",
        "Tanggal",
    ]]

    grand_total = 0

    for order in orders:
        grand_total += float(order.total_price or 0)

        data.append([
            str(order.id),
            Paragraph(
                safe_text(order.user.name if order.user else "-"),
                styles["Normal"],
            ),
            Paragraph(
                safe_text(order.program.name if order.program else "-"),
                styles["Normal"],
            ),
            str(order.quantity),
            rupiah(order.total_price),
            safe_text(order.status),
            safe_text(order.payment.status if order.payment else "-"),
            format_date(order.created_at),
        ])

    if not orders:
        data.append(["-", "Belum ada data", "-", "-", "-", "-", "-", "-"])

    table = Table(
        data,
        colWidths=[
            10*mm, 32*mm, 38*mm, 13*mm,
            27*mm, 25*mm, 27*mm, 32*mm,
        ],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#236B45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F2F7F3"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements = [
        Paragraph(
            f"Tanggal Laporan: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"],
        ),
        Paragraph(
            f"Jumlah Pesanan: {len(orders)}",
            styles["Normal"],
        ),
        Spacer(1, 12),
        table,
        Spacer(1, 15),
        Paragraph(
            f"<b>Total Nilai Seluruh Pesanan: {rupiah(grand_total)}</b>",
            styles["Normal"],
        ),
    ]

    return create_pdf(
        "Laporan Rekap Transaksi",
        "Laporan seluruh pesanan GreenRoots",
        elements,
        pagesize=landscape(A4),
    )