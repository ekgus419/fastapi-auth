## 📘 FastAPI 인증/회원 관리 시스템 API 명세서

### 🔐 1. 회원가입

- **Endpoint**: `POST /auth/signup`
- **설명**: 사용자 회원가입
- **Request Body** (JSON):

```
{
  "email": "testuser1@example.com",
  "password": "password1234",
  "name": "Test User"
}
```

- **인증**: ❌ 필요 없음
- **응답 예시**: `201 Created`

---

### 🔐 2. 로그인 (일반회원/관리자)

- **Endpoint**: `POST /auth/signin`
- **설명**: 이메일과 비밀번호로 로그인, JWT 발급
- **Request Body** (JSON):

```
{
  "email": "testuser1@example.com",
  "password": "password1234"
}
```

- **인증**: ❌ 필요 없음
- **응답 예시**:

```
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

### 👤 3. 사용자 단건 조회

- **Endpoint**: `GET /users/{user_id}`
- **설명**: 특정 사용자 조회 (본인 또는 관리자)
- **인증**: ✅ JWT 필수
- **Headers**:

```
Authorization: Bearer <access_token>
Accept: application/json
```

---

### ✏️ 4. 사용자 정보 수정

- **Endpoint**: `PUT /users/{user_id}`
- **설명**: 사용자 정보 수정 (본인 or 관리자)
- **인증**: ✅ JWT 필수
- **Headers**:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

- **Request Body** (JSON):

```
{
  "name": "Updated User",
  "email": "updated@example.com"
}
```

---

### ❌ 5. 사용자 탈퇴

- **Endpoint**: `DELETE /users/{user_id}`
- **설명**: 사용자 탈퇴 (soft delete)
- **인증**: ✅ JWT 필수
- **Headers**:

```
Authorization: Bearer <access_token>
```

---

### 📋 6. 전체 사용자 조회

- **Endpoint**: `GET /users?page=1&size=10`
- **설명**: 모든 사용자 목록 조회 (관리자만)
- **인증**: ✅ 관리자 JWT 필수
- **Headers**:

```
Authorization: Bearer <admin_token>
Accept: application/json
```
