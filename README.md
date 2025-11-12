# Giám sát log tập trung với ELK Stack

Dự án này đáp ứng yêu cầu “Monitoring Infrastructure with ELK Stack”: chạy Elasticsearch, Logstash, Kibana và Nginx bằng Docker Compose, thu thập log Nginx vào Elasticsearch, và trình diễn một visualization đơn giản trên Kibana.

```
Client traffic → Nginx → shared-logs volume → Logstash → Elasticsearch → Kibana
```

## Thành phần

- **Nginx**: phục vụ trang tĩnh mẫu và ghi access log JSON ra volume `shared-logs`.
- **Logstash**: đọc file log từ volume, enrich bằng GeoIP/User-Agent rồi đẩy vào Elasticsearch (index `nginx-%{+YYYY.MM.dd}`) đồng thời in stdout để debug.
- **Elasticsearch**: lưu trữ log và cung cấp REST API/ingest cho Kibana.
- **Kibana**: tạo data view `nginx-*`, khám phá log và dựng visualization (ví dụ Requests per status code).
- **`scripts/log_generator.py`**: mô phỏng traffic bình thường, brute-force `/login`, và directory scan để nhanh chóng có dữ liệu demo.

## Cấu trúc

```
.
├── docker-compose.yml
├── logstash/
│   ├── Dockerfile
│   └── pipeline.conf
├── nginx/
│   └── default.conf
├── scripts/
│   └── log_generator.py
└── requirements.txt
```

## Chuẩn bị

1. Cài Docker và Docker Compose plugin.
2. (Tùy chọn) tạo virtualenv cho script và cài dependency:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Khởi chạy ELK Stack

```bash
docker compose up -d
```

- Elasticsearch mở ở `http://localhost:9200`.
- Kibana ở `http://localhost:5601`.
- Nginx demo ở `http://localhost:8080`.

## Sinh log demo

```bash
python3 scripts/log_generator.py
```

- Normal traffic gọi ngẫu nhiên `/`, `/products`, `/about-us`.
- Brute-force spam `/login`.
- Directory scan thử `admin_backup/config_X.txt`.

Nhấn `Ctrl + C` để dừng khi đã đủ dữ liệu. Logstash sẽ đẩy vào index theo ngày, có thể xem ngay trên Kibana Discover.

## Visualization gợi ý

1. Vào Kibana → **Stack Management → Data Views → Create data view**.
2. Đặt index pattern `nginx-*`, time field `@timestamp`.
3. Mở **Discover** để trình chiếu luồng log.
4. (Demo khuyến khích) vào **Visualize → Lens**:
   - Horizontal axis: `Terms` trên `status`.
   - Vertical axis: `Records`.
   - Filter `request_uri : "/login"` để minh họa brute-force.

## Dọn dẹp

```bash
docker compose down -v
```

Lệnh trên dừng tất cả dịch vụ và xóa volume `esdata`, `shared-logs`.
