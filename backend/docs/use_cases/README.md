# Use Case Diagrams

이 디렉토리는 Streamlink Dashboard의 Use Case 다이어그램들을 포함합니다. 사용자별로 분리하여 가독성을 높였습니다.

## 📋 다이어그램 목록

### 1. **`use_case_overview.puml`** - 전체 개요
- 모든 Actor들과 주요 Use Case들의 고수준 관계
- 시스템 전체 구조를 한눈에 파악 가능
- 세부사항 없이 전체적인 흐름만 표시

### 2. **`admin_use_cases.puml`** - 관리자 Use Cases
- **Actor**: Admin User
- **주요 기능**:
  - 사용자 관리 (CRUD)
  - 시스템 설정 및 모니터링
  - 플랫폼 설정 관리
  - Rotation Policy 관리
  - 시스템 백업/복원

### 3. **`user_use_cases.puml`** - 일반 사용자 Use Cases
- **Actor**: Regular User
- **주요 기능**:
  - 녹화 파일 관리 (브라우징, 다운로드, 삭제)
  - 즐겨찾기 관리
  - 스케줄 관리 (생성, 편집, 활성화/비활성화)
  - File Explorer 스타일 인터페이스
  - 시스템 상태 확인

### 4. **`system_use_cases.puml`** - 시스템 Use Cases
- **Actors**: Scheduler System, Streamlink Engine, Rotation Service, System Monitor
- **주요 기능**:
  - 자동 녹화 실행
  - 스트림 관리 및 모니터링
  - 파일 관리 및 메타데이터 업데이트
  - Rotation Policy 적용 및 정리
  - 시스템 모니터링 및 에러 처리

## 🔗 관계 유형

### Include 관계 (`<<include>>`)
- **의미**: 필수적인 관계, 포함된 Use Case가 반드시 실행됨
- **예시**: `browse_recordings` → `view_recording_details`

### Extend 관계 (`<<extend>>`)
- **의미**: 선택적인 관계, 조건에 따라 실행될 수 있음
- **예시**: `view_recording_details` → `download_recording`

## 🎯 주요 Flow 패턴

### 1. **Recording Management Flow**
```
browse_recordings → view_recording_details → [download/delete/play/preview/mark_favorite]
```

### 2. **Schedule Management Flow**
```
manage_schedules → [create/edit/delete/enable/disable] → test_schedule
```

### 3. **System Execution Flow**
```
execute_scheduled_recording → check_stream_status → start_recording → save_recording_file
```

### 4. **Error Handling Flow**
```
handle_system_error → log_error → [retry_failed_operation/escalate_error] → notify_admin
```

## 📊 다이어그램 보기 방법

### PlantUML Online Server
1. [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/) 접속
2. 각 `.puml` 파일의 내용을 복사하여 붙여넣기
3. 다이어그램 자동 생성

### VS Code Extension
1. PlantUML 확장 프로그램 설치
2. `.puml` 파일 열기
3. `Alt+Shift+D`로 미리보기

### Local PlantUML
```bash
# Java와 PlantUML JAR 파일 필요
java -jar plantuml.jar use_case_overview.puml
```

## 🔄 다이어그램 업데이트

새로운 Use Case나 Actor가 추가될 때:

1. **Overview 다이어그램** 먼저 업데이트
2. **해당 사용자별 다이어그램** 업데이트
3. **Include/Extend 관계** 재검토
4. **README.md** 업데이트

## 📝 설계 원칙

1. **단일 책임**: 각 다이어그램은 하나의 Actor에 집중
2. **Flow 공유**: 공통되는 흐름은 Include/Extend 관계로 표현
3. **가독성**: 복잡한 관계는 여러 다이어그램으로 분리
4. **일관성**: 모든 다이어그램에서 동일한 스타일 사용
