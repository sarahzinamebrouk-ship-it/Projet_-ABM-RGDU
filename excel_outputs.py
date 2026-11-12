"""Write a small, formatted Excel workbook using only the Python standard library."""

from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape, quoteattr


def _column_name(number):
    name = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _cell_xml(reference, value, style):
    if value is None or value == "":
        return f'<c r="{reference}" s="{style}"/>'
    if isinstance(value, bool):
        return f'<c r="{reference}" s="{style}" t="b"><v>{int(value)}</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{reference}" s="{style}"><v>{value}</v></c>'
    return (
        f'<c r="{reference}" s="{style}" t="inlineStr">'
        f'<is><t xml:space="preserve">{escape(str(value))}</t></is></c>'
    )


def _worksheet_xml(headers, rows, column_widths):
    all_rows = [headers, *rows]
    column_count = len(headers)
    last_column = _column_name(column_count)
    last_row = len(all_rows)

    columns_xml = "".join(
        f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
        for index, width in enumerate(column_widths, start=1)
    )

    row_xml = []
    for row_number, values in enumerate(all_rows, start=1):
        style = 1 if row_number == 1 else 2
        cells = "".join(
            _cell_xml(f"{_column_name(column_number)}{row_number}", value, style)
            for column_number, value in enumerate(values, start=1)
        )
        row_height = ' ht="36" customHeight="1"' if row_number == 1 else ""
        row_xml.append(f'<row r="{row_number}"{row_height}>{cells}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<dimension ref="A1:{last_column}{last_row}"/>'
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews>'
        f'<cols>{columns_xml}</cols>'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        f'<autoFilter ref="A1:{last_column}{last_row}"/>'
        '</worksheet>'
    )


def write_workbook(path, sheets):
    """Create an Excel workbook from (name, headers, rows, widths) sheets."""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + "".join(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for index, _ in enumerate(sheets, start=1)
        )
        + '</Types>'
    )

    root_relationships = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    sheet_entries = "".join(
        f'<sheet name={quoteattr(name)} sheetId="{index}" r:id="rId{index}"/>'
        for index, (name, _, _, _) in enumerate(sheets, start=1)
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{sheet_entries}</sheets></workbook>'
    )

    workbook_relationships = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
            for index, _ in enumerate(sheets, start=1)
        )
        + f'<Relationship Id="rId{len(sheets) + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/></Relationships>'
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF4C2673"/>'
        '<bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
        '<border><left style="thin"><color rgb="FFD0CAD8"/></left>'
        '<right style="thin"><color rgb="FFD0CAD8"/></right>'
        '<top style="thin"><color rgb="FFD0CAD8"/></top>'
        '<bottom style="thin"><color rgb="FFD0CAD8"/></bottom><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="3">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyAlignment="1">'
        '<alignment vertical="center" wrapText="1"/></xf>'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyAlignment="1">'
        '<alignment vertical="top" wrapText="1"/></xf>'
        '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types)
        workbook.writestr("_rels/.rels", root_relationships)
        workbook.writestr("xl/workbook.xml", workbook_xml)
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_relationships)
        workbook.writestr("xl/styles.xml", styles_xml)
        for index, (_, headers, rows, widths) in enumerate(sheets, start=1):
            workbook.writestr(
                f"xl/worksheets/sheet{index}.xml",
                _worksheet_xml(headers, rows, widths),
            )
