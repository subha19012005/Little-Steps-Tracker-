# Little Steps Tracker — Growth Monitoring API Documentation

> **Module:** Person 3 (Growth Monitoring Backend & Database)  
> **Client Consumer:** Person 4 (Flutter Growth Monitoring UI & Charts)  
> **Upstream Module:** Person 1 (Child Management & Child ID)  
> **Downstream Module:** Person 5 (WHO Growth Assessment & Risk)

---

## 1. Overview & Base URLs

The Growth Monitoring Backend handles saving and querying raw physical growth measurement data (height, weight, date) for children.

| Environment | Base URL |
| :--- | :--- |
| **Local PC / Swagger UI** | `http://127.0.0.1:8000` |
| **Android Emulator (Flutter)** | `http://10.0.2.2:8000` |
| **iOS Simulator (Flutter)** | `http://127.0.0.1:8000` |
| **Physical Android/iOS Device (Wi-Fi)** | `http://<YOUR_COMPUTER_LOCAL_IP>:8000` *(e.g. `http://192.168.1.15:8000`)* |

> ⚠️ **Important Network Note for Flutter (Person 4):**
> When testing on a physical mobile device, the phone and your development computer must be connected to the **same Wi-Fi network**. Use your computer's local IP address (find via `ipconfig` on Windows), not `localhost` or `127.0.0.1`.

Interactive Swagger documentation is available in your browser at:
`http://127.0.0.1:8000/docs`

---

## 2. API Endpoints

### 2.1. System Health Checks

#### `GET /`
Verifies that the API service is alive.

- **Status Code:** `200 OK`
- **Response:**
  ```json
  {
    "message": "Little Steps Tracker API is running"
  }
  ```

#### `GET /health`
Used for health checks and automated monitors.

- **Status Code:** `200 OK`
- **Response:**
  ```json
  {
    "status": "ok"
  }
  ```

---

### 2.2. Record a Growth Measurement

#### `POST /api/growth-records`
Saves a new physical growth measurement for a child.

- **HTTP Method:** `POST`
- **Path:** `/api/growth-records`
- **Content-Type:** `application/json`

#### Validation Rules
| Field | Type | Required | Constraints |
| :--- | :--- | :--- | :--- |
| `child_id` | String | Yes | Non-empty string (e.g. `"LST-001"`) |
| `measurement_date` | String | Yes | ISO 8601 date format: `YYYY-MM-DD` |
| `height` | Float / Number | Yes | Height in centimeters (cm); **must be > 0** |
| `weight` | Float / Number | Yes | Weight in kilograms (kg); **must be > 0** |

#### Example Request Body
```json
{
  "child_id": "LST-001",
  "measurement_date": "2026-10-05",
  "height": 95.2,
  "weight": 14.1
}
```

#### Successful Response
- **Status Code:** `201 Created`
- **Response Body:**
  ```json
  {
    "id": 1,
    "child_id": "LST-001",
    "measurement_date": "2026-10-05",
    "height": 95.2,
    "weight": 14.1,
    "created_at": "2026-10-05T15:30:00.123456Z"
  }
  ```

#### Error Responses

- **422 Unprocessable Entity** (Invalid or Missing Fields):
  ```json
  {
    "error": "Validation Error",
    "message": "The request body contains invalid or missing fields.",
    "details": [
      {
        "field": "height",
        "message": "Input should be greater than 0",
        "type": "greater_than"
      }
    ]
  }
  ```

- **500 Internal Server Error** (Database Failure):
  ```json
  {
    "detail": "Failed to store growth measurement record due to a database error."
  }
  ```

---

### 2.3. Retrieve Child Growth History

#### `GET /api/children/{child_id}/growth-history`
Returns all historical growth measurements for a given child, ordered with the **newest measurement first** (descending by `measurement_date`).

- **HTTP Method:** `GET`
- **Path:** `/api/children/{child_id}/growth-history`
- **URL Parameters:**
  - `child_id` (String, required): Unique child identifier (e.g. `LST-001`).

#### Example Request
```http
GET /api/children/LST-001/growth-history HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
```

#### Successful Response (Child with records)
- **Status Code:** `200 OK`
- **Response Body:**
  ```json
  [
    {
      "id": 3,
      "child_id": "LST-001",
      "measurement_date": "2026-10-05",
      "height": 95.2,
      "weight": 14.1,
      "created_at": "2026-10-05T15:30:00.123456Z"
    },
    {
      "id": 2,
      "child_id": "LST-001",
      "measurement_date": "2026-09-05",
      "height": 94.0,
      "weight": 13.7,
      "created_at": "2026-09-05T10:15:00.000000Z"
    },
    {
      "id": 1,
      "child_id": "LST-001",
      "measurement_date": "2026-08-01",
      "height": 92.0,
      "weight": 13.0,
      "created_at": "2026-08-01T09:00:00.000000Z"
    }
  ]
  ```

#### Successful Response (Child with NO records yet)
- **Status Code:** `200 OK`
- **Response Body:**
  ```json
  []
  ```

#### Error Responses

- **400 Bad Request** (Empty or Whitespace-only child_id):
  ```json
  {
    "detail": "child_id must not be empty or whitespace only."
  }
  ```

- **500 Internal Server Error** (Database Connection Failure):
  ```json
  {
    "detail": "Failed to retrieve growth records due to a database error."
  }
  ```

---

## 3. Flutter Integration Guide (For Person 4)

### Dart Model Snippet

```dart
class GrowthRecord {
  final int id;
  final String childId;
  final String measurementDate; // YYYY-MM-DD
  final double height;
  final double weight;
  final String? createdAt;

  GrowthRecord({
    required this.id,
    required this.childId,
    required this.measurementDate,
    required this.height,
    required this.weight,
    this.createdAt,
  });

  factory GrowthRecord.fromJson(Map<String, dynamic> json) {
    return GrowthRecord(
      id: json['id'],
      childId: json['child_id'],
      measurementDate: json['measurement_date'],
      height: (json['height'] as num).toDouble(),
      weight: (json['weight'] as num).toDouble(),
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'child_id': childId,
      'measurement_date': measurementDate,
      'height': height,
      'weight': weight,
    };
  }
}
```

### Dart HTTP Service Snippet

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class GrowthService {
  // Use http://10.0.2.2:8000 for Android Emulator
  // Use http://192.168.x.x:8000 for Physical Device
  static const String baseUrl = 'http://10.0.2.2:8000';

  // 1. Create a measurement record
  Future<GrowthRecord?> createRecord({
    required String childId,
    required String date,
    required double height,
    required double weight,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/growth-records'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'child_id': childId,
        'measurement_date': date,
        'height': height,
        'weight': weight,
      }),
    );

    if (response.statusCode == 201) {
      return GrowthRecord.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to save measurement: ${response.body}');
    }
  }

  // 2. Fetch history (ordered newest first)
  Future<List<GrowthRecord>> fetchGrowthHistory(String childId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/children/$childId/growth-history'),
    );

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => GrowthRecord.fromJson(item)).toList();
    } else {
      throw Exception('Failed to fetch history: ${response.body}');
    }
  }
}
```
