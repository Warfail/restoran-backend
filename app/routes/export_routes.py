from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import StreamingResponse
import io
import xlsxwriter

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)

class ChartData(BaseModel):
    name: str
    pendapatan: float
    tahunLalu: float

class MenuPerformance(BaseModel):
    nama: str
    terjual: int
    persentase: float

class ExcelExportRequest(BaseModel):
    periodLabel: str
    activePeriod: str
    chartData: List[ChartData]
    menuLaris: List[MenuPerformance]
    menuKurangLaris: List[MenuPerformance]

@router.post("/sales-report-excel")
async def export_sales_report_excel(req: ExcelExportRequest):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # -------------------------------------------------------------
    # SHEET 1: LAPORAN PENDAPATAN
    # -------------------------------------------------------------
    ws1 = workbook.add_worksheet('Laporan Pendapatan')
    ws1.hide_gridlines(2)
    
    # Formats
    title_fmt = workbook.add_format({'bold': True, 'font_size': 18, 'bg_color': '#1B5E20', 'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter'})
    subtitle_fmt = workbook.add_format({'bold': True, 'font_size': 13, 'bg_color': '#2E7D32', 'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter'})
    header_fmt = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#1B5E20', 'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter', 'border': 1})
    data_fmt = workbook.add_format({'font_size': 10, 'valign': 'vcenter', 'border': 1})
    data_currency_fmt = workbook.add_format({'font_size': 10, 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0'})
    
    ws1.merge_range('A1:E1', '🍽️  Singkong Keju D9', title_fmt)
    ws1.set_row(0, 40)
    ws1.merge_range('A2:E2', 'LAPORAN PENDAPATAN', subtitle_fmt)
    ws1.set_row(1, 30)
    ws1.merge_range('A3:E3', f"Periode: {req.activePeriod} - {req.periodLabel}", subtitle_fmt)
    ws1.set_row(2, 25)
    
    ws1.set_column('B:B', 28)
    ws1.set_column('C:D', 25)
    ws1.set_column('E:E', 18)
    
    headers = ['No', 'Tanggal / Periode', 'Pendapatan Tahun Ini', 'Pendapatan Tahun Lalu', 'Pertumbuhan (%)']
    ws1.write_row('A5', headers, header_fmt)
    
    row_num = 5
    for idx, row in enumerate(req.chartData):
        growth = 100 if row.tahunLalu == 0 else ((row.pendapatan - row.tahunLalu) / row.tahunLalu) * 100
        ws1.write_number(row_num, 0, idx + 1, data_fmt)
        ws1.write_string(row_num, 1, row.name, data_fmt)
        ws1.write_number(row_num, 2, row.pendapatan, data_currency_fmt)
        ws1.write_number(row_num, 3, row.tahunLalu, data_currency_fmt)
        ws1.write_number(row_num, 4, growth, data_fmt)
        row_num += 1

    # Add Bar Chart
    bar_chart = workbook.add_chart({'type': 'column'})
    # Configure the first series (Pendapatan Tahun Ini)
    bar_chart.add_series({
        'name': 'Pendapatan Tahun Ini',
        'categories': ['Laporan Pendapatan', 5, 1, row_num - 1, 1],
        'values':     ['Laporan Pendapatan', 5, 2, row_num - 1, 2],
        'fill':       {'color': '#4CAF50'},
    })
    # Configure the second series (Pendapatan Tahun Lalu)
    bar_chart.add_series({
        'name': 'Pendapatan Tahun Lalu',
        'categories': ['Laporan Pendapatan', 5, 1, row_num - 1, 1],
        'values':     ['Laporan Pendapatan', 5, 3, row_num - 1, 3],
        'fill':       {'color': '#9E9E9E'},
    })
    bar_chart.set_title({'name': 'Tren Pendapatan'})
    bar_chart.set_x_axis({'name': 'Periode'})
    bar_chart.set_y_axis({'name': 'Pendapatan (Rp)'})
    bar_chart.set_size({'width': 700, 'height': 400})
    
    # Insert chart to worksheet
    ws1.insert_chart('G5', bar_chart)

    # -------------------------------------------------------------
    # SHEET 2: PERFORMA MENU
    # -------------------------------------------------------------
    ws2 = workbook.add_worksheet('Performa Menu')
    ws2.hide_gridlines(2)
    
    ws2.merge_range('A1:C1', '🍽️  Singkong Keju D9', title_fmt)
    ws2.set_row(0, 40)
    ws2.merge_range('A2:C2', 'PERFORMA MENU (5 TERLARIS)', subtitle_fmt)
    ws2.set_row(1, 30)
    
    ws2.set_column('B:B', 35)
    ws2.set_column('C:C', 22)
    
    ws2.write_row('A4', ['No', 'Nama Menu', 'Jumlah Terjual (Porsi)'], header_fmt)
    
    r2_num = 4
    for idx, item in enumerate(req.menuLaris):
        ws2.write_number(r2_num, 0, idx + 1, data_fmt)
        ws2.write_string(r2_num, 1, item.nama, data_fmt)
        ws2.write_number(r2_num, 2, item.terjual, data_fmt)
        r2_num += 1
        
    # Add Pie Chart for Menu Laris
    pie_chart = workbook.add_chart({'type': 'pie'})
    pie_chart.add_series({
        'name': 'Proporsi Penjualan Menu Laris',
        'categories': ['Performa Menu', 4, 1, r2_num - 1, 1],
        'values':     ['Performa Menu', 4, 2, r2_num - 1, 2],
        'data_labels': {'value': True, 'percentage': True}
    })
    pie_chart.set_title({'name': 'Distribusi 5 Menu Terlaris'})
    pie_chart.set_size({'width': 500, 'height': 350})
    ws2.insert_chart('E4', pie_chart)

    # Adding Menu Kurang Laris at the bottom
    start_kurang = r2_num + 3
    ws2.merge_range(f'A{start_kurang}:C{start_kurang}', 'PERFORMA MENU (5 KURANG LARIS)', subtitle_fmt)
    ws2.write_row(f'A{start_kurang+1}', ['No', 'Nama Menu', 'Jumlah Terjual (Porsi)'], header_fmt)
    
    r3_num = start_kurang + 1
    for idx, item in enumerate(req.menuKurangLaris):
        ws2.write_number(r3_num, 0, idx + 1, data_fmt)
        ws2.write_string(r3_num, 1, item.nama, data_fmt)
        ws2.write_number(r3_num, 2, item.terjual, data_fmt)
        r3_num += 1
        
    workbook.close()
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=Laporan_{req.activePeriod}_{req.periodLabel}.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
