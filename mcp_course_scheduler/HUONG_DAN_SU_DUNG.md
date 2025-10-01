# Hướng Dẫn Sử Dụng MCP Server - Tiếng Việt

## Lỗi Thường Gặp

### Lỗi: "Failed to validate request: Received request before initialization was complete"

**Nguyên nhân**: Bạn đang gọi tool khác trước khi khởi tạo scheduler.

**Giải pháp**: Luôn luôn gọi `initialize_scheduler` TRƯỚC KHI sử dụng bất kỳ tool nào khác.

## Thứ Tự Sử Dụng Đúng

### Bước 1: Khởi Tạo Scheduler (BẮT BUỘC)

Khi server đã chạy, câu lệnh ĐẦU TIÊN bạn phải gọi là:

```
Please initialize the scheduler
```

Hoặc với tham số cụ thể:

```json
{
  "curriculum_file_path": "E:\\HaUI_Agent\\khung ctrinh cntt.json",
  "processed_file_path": "E:\\HaUI_Agent\\sample.json"
}
```

**Chờ kết quả trả về thành công** trước khi tiếp tục!

### Bước 2: Sử Dụng Các Tool Khác

Sau khi khởi tạo thành công, bạn có thể sử dụng các tool:

#### Gợi Ý Môn Học

```
Tôi là sinh viên kỳ 3, đã hoàn thành các môn:
- LP6010, BS6018, BS6002, DC6005, DC6004, DC6007, DC6006
- IT6011, IT6015, BS6027, IT6016, BS6001, LP6011

Tôi muốn học "Cấu trúc dữ liệu và giải thuật" kỳ này.
Không muốn học "Thiết kế đồ hoạ 2D".
Tối đa 18 tín chỉ.

Hãy gợi ý môn học cho tôi.
```

#### Tìm Kiếm Môn Học

```
Tìm các môn học về "lập trình"
```

#### Kiểm Tra Môn Tiên Quyết

```
Tôi đã học IT6015, BS6001. Tôi có thể học IT6002 không?
```

#### Xem Thông Tin Môn Học

```
Cho tôi biết thông tin về môn IT6015
```

#### Xem Môn Học Theo Kỳ

```
Cho tôi xem tất cả môn học của kỳ 4
```

#### Tính Tín Chỉ Còn Lại

```
Tôi đã hoàn thành các môn: IT6015, BS6001, BS6002, LP6010
Còn bao nhiêu tín chỉ để tốt nghiệp?
```

## Ví Dụ Workflow Hoàn Chỉnh

### 1. Sinh Viên Mới (Kỳ 1)

```
# Bước 1: Khởi tạo
Please initialize the scheduler

# Bước 2: Xem môn học kỳ 1
Show me all courses for semester 1

# Bước 3: Gợi ý lịch học
I'm a new student in semester 1.
Suggest a 20-credit schedule for me.
```

### 2. Sinh Viên Kỳ Giữa

```
# Bước 1: Khởi tạo
Please initialize the scheduler

# Bước 2: Gợi ý với điều kiện
Tôi đang học kỳ 4, đã hoàn thành:
IT6015, IT6016, IT6120, IT6126, BS6001, BS6002, LP6010, LP6011

Tôi muốn ưu tiên: Trí tuệ nhân tạo, Mạng máy tính
Không muốn: Thiết kế đồ hoạ 2D
Tối đa: 18 tín chỉ

Gợi ý lịch học.
```

### 3. Sinh Viên Học Lại/Bù

```
# Bước 1: Khởi tạo
Please initialize the scheduler

# Bước 2: Tính tiến độ
Calculate my remaining credits. I completed: IT6015, BS6002

# Bước 3: Gợi ý catch-up
I'm in semester 5 but only completed: IT6015, BS6002
Help me catch up. Max 22 credits.
```

## Các Tool Có Sẵn

| Tool                          | Mô Tả                | Cần Init?         |
| ----------------------------- | -------------------- | ----------------- |
| `initialize_scheduler`        | Khởi tạo scheduler   | ❌ (gọi đầu tiên) |
| `suggest_courses`             | Gợi ý môn học        | ✅                |
| `validate_prerequisites`      | Kiểm tra tiên quyết  | ✅                |
| `get_course_info`             | Thông tin môn học    | ✅                |
| `search_courses`              | Tìm kiếm môn học     | ✅                |
| `get_semester_courses`        | Xem môn theo kỳ      | ✅                |
| `calculate_remaining_credits` | Tính tín chỉ còn lại | ✅                |

## Lưu Ý Quan Trọng

1. ⚠️ **LUÔN LUÔN gọi `initialize_scheduler` đầu tiên**
2. ⚠️ Chờ kết quả khởi tạo thành công trước khi gọi tool khác
3. ⚠️ Sử dụng mã môn học (IT6015) chính xác hơn tên môn
4. ⚠️ Tín chỉ tối đa thực tế thường là 15-22 tín/kỳ
5. ⚠️ Chú ý các cảnh báo về môn học trước/môn tiên quyết

## Xử Lý Lỗi

### "Scheduler not initialized"

→ Gọi `initialize_scheduler` trước

### "Course not found"

→ Kiểm tra mã môn học có đúng không

### "Maximum credits must be > 0"

→ Đặt max_credits là số dương

### "Missing prerequisites"

→ Xem danh sách môn tiên quyết cần học trước

## Kết Quả Mong Đợi

Khi gọi `suggest_courses` thành công, bạn sẽ nhận được:

```json
{
  "success": true,
  "suggestions": [
    {
      "course_code": "IT6002",
      "course_name": "Cấu trúc dữ liệu và giải thuật",
      "credits": 3.0,
      "reason": "ON-TRACK: This course aligns with your current semester...",
      "strategy": "ON-TRACK",
      "warnings": [],
      "is_auto_included": false
    }
  ],
  "total_credits": 18.0,
  "warnings": [],
  "errors": []
}
```

## Các Chiến Lược Gợi Ý

1. **CATCH-UP**: Môn học đáng lẽ đã học ở kỳ trước
2. **ON-TRACK**: Môn học đúng kỳ hiện tại
3. **ADVANCED**: Môn học kỳ sau (có cảnh báo)
4. **PRIORITY REQUEST**: Môn học theo yêu cầu ưu tiên

## Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra đã gọi `initialize_scheduler` chưa
2. Đọc lại thông báo lỗi
3. Xem ví dụ workflow ở trên
4. Kiểm tra file dữ liệu tồn tại: `khung ctrinh cntt.json` và `sample.json`
