import matplotlib
matplotlib.use('Agg') 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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

day_count = len(df) # Đảm bảo day_count = 365
analysis_year = 2025
df['Date'] = pd.date_range(f'{analysis_year}-01-01', periods=day_count, freq='D')
label_x = day_count + 13

candle_days = set()
for start in range(0, day_count, 30):
    end = min(start + 30, day_count)
    candle_count = min(8, max(1, round((end - start) * 8 / 30)))
    bucket_width = (end - start) / candle_count
    candle_days.update(np.linspace(start + bucket_width / 2,
                                   end - bucket_width / 2,
                                   candle_count, dtype=int))

price_cols = [0, 1, 2, 3, 4, 5, 6]
df['Open'] = df[0]
df['Close'] = df[6]
df['High'] = df[price_cols].max(axis=1)
df['Low'] = df[price_cols].min(axis=1)

df['Ref_Price'] = df['Close'].shift(1)
df.loc[0, 'Ref_Price'] = df.loc[0, 'Open']
df['Floor_Price'] = df['Ref_Price'] * 0.9
df['Ceil_Price'] = df['Ref_Price'] * 1.1

global_max = df['High'].max()
global_min = df['Low'].min()

days_sorted = sorted(candle_days)
step = min(np.diff(days_sorted)) if len(days_sorted) > 1 else 1
body_w = step * 0.82
line_w = body_w * 0.6
min_body = (global_max - global_min) * 0.004

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7.5), sharex=True, gridspec_kw={'height_ratios': [1, 1]})
fig.patch.set_facecolor('black')
plt.subplots_adjust(left=0.11, right=0.95, bottom=0.1, top=0.99, hspace=0.08)

for ax in [ax1, ax2]:
    ax.set_facecolor('black')
    ax.tick_params(colors='white', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('white')
    ax.set_ylabel('VND', color='white', fontweight='bold')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

y_axis_max = np.ceil(global_max / 5000) * 5000
for ax in [ax1, ax2]:
    ax.set_ylim(0, y_axis_max)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5000))

ax2.set_xlabel('Date', color='white', fontweight='bold')
ax2.set_xticks(np.arange(0, day_count, 30))
ax2.set_xlim(-5, day_count + 35)

days_data = []
lows_data = []
highs_data = []

line_max = ax2.axhline(y=0, color='green', linestyle='--', lw=0.8, alpha=0.6)
line_min = ax2.axhline(y=0, color='red', linestyle='--', lw=0.8, alpha=0.6)
text_max = ax2.text(label_x, 0, "", color='green', va='center', ha='right')
text_min = ax2.text(label_x, 0, "", color='red', va='center', ha='right')

line_current = ax2.axhline(y=0, color='brown', linestyle='-', lw=1.0, alpha=0.6)
text_current = ax2.text(0, 0, "", color='red', va='center', ha='left')

fill_collection = None
high_line, = ax2.plot([], [], color='olivedrab', lw=1.2)
low_line, = ax2.plot([], [], color='darkorange', lw=1.2)

def get_candle_color(close_p, ref_p, floor_p, ceil_p):
    if np.isclose(close_p, floor_p, atol=1.0): 
        return 'dodgerblue'
    if np.isclose(close_p, ceil_p, atol=1.0): 
        return 'mediumorchid'
    if np.isclose(close_p, ref_p, atol=1e-2): 
        return 'yellow'
    if close_p < ref_p: 
        return 'red'
    return 'limegreen'

def init():
    return []

def animate(i):
    global fill_collection
    if i >= len(df):
        return []

    row = df.iloc[i]
    day = i
    o, c, h, l = row['Open'], row['Close'], row['High'], row['Low']
    ref, floor, ceil = row['Ref_Price'], row['Floor_Price'], row['Ceil_Price']

    color = get_candle_color(c, ref, floor, ceil)

    # Biểu đồ trên (ax1) - Candlestick
    if day in candle_days:
        ax1.plot([day, day], [l, h], color=color, lw=1.2,
                 solid_capstyle='butt', zorder=2)

        body_bottom = min(o, c)
        body_height = max(abs(o - c), min_body)
        rect = plt.Rectangle((day - body_w / 2, body_bottom), body_w, body_height,
                             facecolor=color, edgecolor='none', zorder=3)
        ax1.add_patch(rect)

        mid = body_bottom + body_height / 2
        ax1.plot([day - line_w / 2, day + line_w / 2], [mid, mid],
                 color='white', lw=1.8, solid_capstyle='butt', zorder=4)
    
    # Biểu đồ dưới (ax2) - Dải băng động
    days_data.append(day)
    lows_data.append(l)
    highs_data.append(h)

    current_max = max(highs_data)
    current_min = min(lows_data)

    line_max.set_ydata([current_max, current_max])
    text_max.set_position((label_x, current_max))
    text_max.set_text(f"{int(current_max):,}")

    line_min.set_ydata([current_min, current_min])
    text_min.set_position((label_x, current_min))
    text_min.set_text(f"{int(current_min):,}")

    if c >= ref:
        current_color = 'limegreen'
        band_color = 'limegreen'
        low_line.set_color('olivedrab')
    else:
        current_color = 'red'
        band_color = 'darkorange'
        low_line.set_color('darkorange')

    if fill_collection:
        fill_collection.remove()
    fill_collection = ax2.fill_between(days_data, lows_data, highs_data,
                                       color=band_color, alpha=0.45)
    high_line.set_data(days_data, highs_data)
    low_line.set_data(days_data, lows_data)

    line_current.set_ydata([c, c])
    text_current.set_position((day + 3, c))
    text_current.set_text(f"{int(c):,}")
    text_current.set_color(current_color)

    return []


target_duration_seconds = 180  
playback_fps = day_count / target_duration_seconds  # 365 / 154 ≈ 2.37 fps

ani = animation.FuncAnimation(fig, animate, frames=day_count, init_func=init,
                              interval=1000 / playback_fps, blit=False)

try:
    writer = animation.FFMpegWriter(
        fps=playback_fps, 
        codec='libx264', 
        extra_args=['-pix_fmt', 'yuv420p']
    )
    print(f"Đang render video quét trọn vẹn {day_count} dòng dữ liệu...")
    ani.save('dothi.mp4', writer=writer)
    print("Đã xuất file video thành công: dothi.mp4")
except Exception as e:
    print("Lỗi khi xuất video (kiểm tra lại ffmpeg):", e)
    plt.show()