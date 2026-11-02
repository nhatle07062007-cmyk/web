import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

file_name = 'abc-23.csv'
data_path = Path(__file__).resolve().parent / file_name
df = pd.read_csv(data_path, header=None)
if df.shape != (365, 7):
    raise ValueError(f"Dữ liệu phải có 365 dòng và 7 cột; hiện có {df.shape[0]} dòng, {df.shape[1]} cột.")
df = df.apply(pd.to_numeric, errors='raise')
if not np.isfinite(df.to_numpy()).all():
    raise ValueError("Dữ liệu giá không được chứa giá trị thiếu hoặc vô hạn.")

day_count = len(df)
analysis_year = 2025
df['Date'] = pd.date_range(f'{analysis_year}-01-01', periods=day_count, freq='D')

price_cols = [0, 1, 2, 3, 4, 5, 6]
df['Open'] = df[0]
df['Close'] = df[6]
df['High'] = df[price_cols].max(axis=1)
df['Low'] = df[price_cols].min(axis=1)

df['Ref_Price'] = df['Close'].shift(1)
df.loc[0, 'Ref_Price'] = df.loc[0, 'Open']
df['Floor_Price'] = df['Ref_Price'] * 0.9
df['Ceil_Price'] = df['Ref_Price'] * 1.1

df['Daily_Range'] = df['High'] - df['Low']
month_groups = df.groupby(df['Date'].dt.month)
monthly_stats = month_groups.agg(
    So_ngay=('Close', 'count'),
    Gia_dong_cua_trung_binh=('Close', 'mean'),
    Do_lech_chuan=('Close', 'std'),
    Gia_thap_nhat=('Low', 'min'),
    Gia_cao_nhat=('High', 'max'),
)
monthly_stats['Bien_do_gia'] = (
    monthly_stats['Gia_cao_nhat'] - monthly_stats['Gia_thap_nhat']
)
monthly_stats.index = monthly_stats.index.map(lambda month: f'T{month:02d}')
print(f'\nTHỐNG KÊ GIÁ THEO THÁNG ({analysis_year})')
print('Giá trung bình và độ lệch chuẩn được tính trên giá đóng cửa.')
print(monthly_stats.round(2).to_string())
most_volatile_month = monthly_stats['Do_lech_chuan'].idxmax()
widest_month = monthly_stats['Bien_do_gia'].idxmax()
print(
    f'Tháng có độ lệch chuẩn giá đóng cửa cao nhất: {most_volatile_month} '
    f'({monthly_stats.loc[most_volatile_month, "Do_lech_chuan"]:,.2f}).'
)
print(
    f'Tháng có biên độ High-Low rộng nhất: {widest_month} '
    f'({monthly_stats.loc[widest_month, "Bien_do_gia"]:,.2f}).'
)

quarter_groups = df.groupby(df['Date'].dt.quarter)
quarterly_stats = quarter_groups.agg(
    So_ngay=('Close', 'count'),
    Gia_dong_cua_trung_binh=('Close', 'mean'),
    Do_lech_chuan=('Close', 'std'),
    Gia_thap_nhat=('Low', 'min'),
    Gia_cao_nhat=('High', 'max'),
    Gia_dong_cua_dau_quy=('Close', 'first'),
    Gia_dong_cua_cuoi_quy=('Close', 'last'),
    Bien_do_trung_binh_ngay=('Daily_Range', 'mean'),
)
quarterly_stats['Bien_do_quy'] = (
    quarterly_stats['Gia_cao_nhat'] - quarterly_stats['Gia_thap_nhat']
)
quarterly_stats['Thay_doi_dau_cuoi_%'] = (
    (quarterly_stats['Gia_dong_cua_cuoi_quy']
     / quarterly_stats['Gia_dong_cua_dau_quy'] - 1) * 100
)
quarterly_stats.index = [f'Q{quarter}' for quarter in quarterly_stats.index]
print(f'\nĐÁNH GIÁ BIẾN ĐỘNG THEO QUÝ ({analysis_year})')
print(quarterly_stats.round(2).to_string())
most_volatile_quarter = quarterly_stats['Do_lech_chuan'].idxmax()
print(
    f'{most_volatile_quarter} có độ lệch chuẩn giá đóng cửa cao nhất '
    f'({quarterly_stats.loc[most_volatile_quarter, "Do_lech_chuan"]:,.2f}); '
    'cột Thay_doi_dau_cuoi_% cho biết hướng thay đổi giá trong từng quý.'
)

at_floor = np.isclose(
    df['Close'], df['Floor_Price'], rtol=0, atol=1e-2
)
at_ceiling = np.isclose(
    df['Close'], df['Ceil_Price'], rtol=0, atol=1e-2
)
at_reference = np.isclose(
    df['Close'], df['Ref_Price'], rtol=0, atol=1e-2
)
anomaly_mask = at_floor | at_ceiling | at_reference
anomalies = pd.DataFrame({
    'Ngay_gia_dinh': df.loc[anomaly_mask, 'Date'].dt.strftime('%Y-%m-%d'),
    'Dong_du_lieu': df.index[anomaly_mask] + 1,
    'Gia_dong_cua': df.loc[anomaly_mask, 'Close'],
    'Gia_tham_chieu': df.loc[anomaly_mask, 'Ref_Price'],
    'Gia_san': df.loc[anomaly_mask, 'Floor_Price'],
    'Gia_tran': df.loc[anomaly_mask, 'Ceil_Price'],
    'Bat_thuong': np.select(
        [
            at_floor[anomaly_mask],
            at_ceiling[anomaly_mask],
            at_reference[anomaly_mask],
        ],
        ['Giá sàn', 'Giá trần', 'Giá tham chiếu'],
        default='',
    ),
})
print('\nCÁC DÒNG CÓ GIÁ ĐÓNG CỬA BẰNG GIÁ SÀN/TRẦN/THAM CHIẾU')
print('Giá tham chiếu là giá đóng cửa của dòng trước; dòng đầu lấy giá mở cửa làm giả định.')
print(anomalies.round(2).to_string(index=False))

annual_high = df['High'].max()
annual_low = df['Low'].min()
annual_mean_close = df['Close'].mean()
annual_high_date = df.loc[df['High'].idxmax(), 'Date']
annual_low_date = df.loc[df['Low'].idxmin(), 'Date']
annual_amplitude = annual_high - annual_low
largest_daily_swing = df['Daily_Range'].idxmax()
print(f'\nXU HƯỚNG VÀ BIÊN ĐỘ CẢ NĂM ({analysis_year})')
print(f'Giá đóng cửa trung bình năm: {annual_mean_close:,.2f} VND.')
print(
    f'Giá đóng cửa đầu/cuối kỳ: {df["Close"].iloc[0]:,.2f} / '
    f'{df["Close"].iloc[-1]:,.2f}; thay đổi '
    f'{(df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100:.2f}%.'
)
print(
    f'Biên độ toàn kỳ (High lớn nhất - Low nhỏ nhất): {annual_amplitude:,.2f}; '
    f'đỉnh {annual_high:,.2f} ngày {annual_high_date:%Y-%m-%d}, '
    f'đáy {annual_low:,.2f} ngày {annual_low_date:%Y-%m-%d}.'
)
print(
    f'Biên độ High-Low lớn nhất trong một dòng: '
    f'{df.loc[largest_daily_swing, "Daily_Range"]:,.2f} ngày '
    f'{df.loc[largest_daily_swing, "Date"]:%Y-%m-%d} '
    f'(dòng {largest_daily_swing + 1}).'
)


output_dir = Path(__file__).resolve().parent / 'phan_tich_gia'
output_dir.mkdir(exist_ok=True)

# Biểu đồ giá đóng cửa trung bình theo tháng, kèm độ lệch chuẩn.
fig_monthly, ax_monthly = plt.subplots(figsize=(11, 5))
month_labels = [f'T{month:02d}' for month in range(1, 13)]
ax_monthly.bar(
    month_labels,
    monthly_stats['Gia_dong_cua_trung_binh'],
    yerr=monthly_stats['Do_lech_chuan'],
    capsize=4,
    color='steelblue',
    alpha=0.85,
)
ax_monthly.set_title(f'Giá đóng cửa trung bình theo tháng ({analysis_year})')
ax_monthly.set_xlabel('Tháng')
ax_monthly.set_ylabel('Giá (VND)')
ax_monthly.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda value, _: f'{value:,.0f}')
)
ax_monthly.grid(axis='y', alpha=0.25)
fig_monthly.tight_layout()
fig_monthly.savefig(output_dir / 'gia_trung_binh_theo_thang.png', dpi=150)
plt.close(fig_monthly)

# Boxplot biểu diễn phân phối giá đóng cửa từng tháng.
monthly_close = [
    df.loc[df['Date'].dt.month == month, 'Close'].to_numpy()
    for month in range(1, 13)
]
fig_box, ax_box = plt.subplots(figsize=(12, 5))
ax_box.boxplot(monthly_close, showfliers=True)
ax_box.set_xticks(range(1, 13), month_labels)
ax_box.set_title(f'Phân phối giá đóng cửa theo tháng ({analysis_year})')
ax_box.set_xlabel('Tháng')
ax_box.set_ylabel('Giá (VND)')
ax_box.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda value, _: f'{value:,.0f}')
)
ax_box.grid(axis='y', alpha=0.25)
fig_box.tight_layout()
fig_box.savefig(output_dir / 'boxplot_gia_theo_thang.png', dpi=150)
plt.close(fig_box)

# Histogram so sánh phân phối giá đóng cửa của nửa đầu và nửa cuối năm.
first_half = df.loc[df['Date'].dt.quarter.isin([1, 2]), 'Close']
second_half = df.loc[df['Date'].dt.quarter.isin([3, 4]), 'Close']
fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
ax_hist.hist(first_half, bins=20, alpha=0.6, label='Q1 + Q2', color='royalblue')
ax_hist.hist(second_half, bins=20, alpha=0.6, label='Q3 + Q4', color='darkorange')
ax_hist.set_title(f'Phân bố giá đóng cửa: Q1+Q2 và Q3+Q4 ({analysis_year})')
ax_hist.set_xlabel('Giá đóng cửa (VND)')
ax_hist.set_ylabel('Số dòng')
ax_hist.legend()
ax_hist.grid(axis='y', alpha=0.25)
fig_hist.tight_layout()
fig_hist.savefig(output_dir / 'phan_bo_gia_2_nua_nam.png', dpi=150)
plt.close(fig_hist)

# Đường giá đóng cửa toàn năm để quan sát xu hướng tổng thể.
fig_trend, ax_trend = plt.subplots(figsize=(12, 5))
ax_trend.plot(
    df['Date'],
    df['Close'],
    color='slateblue',
    lw=1.2,
    label='Giá đóng cửa',
)
ax_trend.axhline(
    annual_mean_close,
    color='darkorange',
    linestyle='--',
    lw=1.5,
    label=f'Trung bình năm: {annual_mean_close:,.2f} VND',
)
ax_trend.set_title(f'Giá đóng cửa theo thời gian ({analysis_year})')
ax_trend.set_xlabel('Ngày giả định theo thứ tự dòng')
ax_trend.set_ylabel('Giá (VND)')
ax_trend.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda value, _: f'{value:,.0f}')
)
ax_trend.legend()
ax_trend.grid(alpha=0.25)
fig_trend.tight_layout()
fig_trend.savefig(output_dir / 'xu_huong_gia_ca_nam.png', dpi=150)
plt.close(fig_trend)


anomalies.to_csv(output_dir / 'ngay_bat_thuong.csv', index=False)
print(f'\nĐã lưu bảng bất thường và 4 biểu đồ tại: {output_dir}')