## Cấu trúc thư mục

py/
|-- main.py             # Tệp mã nguồn chính chạy server FastAPI 
|-- requirements.txt    # Khai báo các thư viện Python cần cài đặt cho dự án
|-- render.yaml         # Tệp cấu hình để triển khai lên nền tảng Render 
|-- index.html          # Giao diện người dùng (HTML) 
|-- style.css           # Tệp định dạng giao diện (CSS) 
|-- scripts.js          # Tệp xử lý tương tác người dùng (JavaScript) 
|-- dothi.mp4           # Video mô phỏng biến động giá 
|-- phan_tich_gia/      # Thư mục chứa dữ liệu CSV ngay_bat_thuong và ảnh biểu đồ 
    |-- boxplot_gia_theo_thang.png
    |-- gia_trung_binh_theo_thang.png 
    |-- phan_bo_gia_2_nua_nam.png 
    |-- xu_huong_gia_ca_nam.png
    |-- ngay_bat_thuong.csv
|-- videogk/            # Tạo video và xử lý dữ liệu 
    |-- phan_tich_gia/  # Thư mục chứa dữ liệu CSV ngay_bat_thuong và ảnh biểu đồ 
        |-- boxplot_gia_theo_thang.png
        |-- gia_trung_binh_theo_thang.png 
        |-- phan_bo_gia_2_nua_nam.png 
        |-- xu_huong_gia_ca_nam.png
        |-- ngay_bat_thuong.csv 
    |-- abc-23.csv              # Dữ liệu đầu vào 
    |-- dothi.mp4               # Video mô phỏng biến động giá 
    |-- dothimophong.py         # Mô phỏng đồ thị dạng video
    |-- phantichthongke.py      # Phân tích thống kê và trực quan hoá

