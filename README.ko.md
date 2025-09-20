<div align="center">

# 🎮 Streamlink Dashboard

*당신의 궁극적인 스트리밍 녹화 동반자*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://hub.docker.com/r/zerobell/streamlink-dashboard)
[![FastAPI](https://img.shields.io/badge/FastAPI-109989?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

<p>
    <a href="https://www.buymeacoffee.com/zerobell">
      <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee" alt="Buy Me a Coffee">
    </a>
</p>

---

**🚀 좋아하는 스트림을 다시는 놓치지 마세요!** 세련되고 현대적인 웹 대시보드로 여러 플랫폼의 라이브 스트림을 자동으로 녹화하세요.

</div>

Streamlink을 사용한 자동화된 스트리밍 녹화를 위한 강력한 웹 기반 대시보드 애플리케이션입니다. 현대적인 기술로 구축되었으며 원활한 스트림 관리를 위해 설계되었습니다.

## 프로젝트 개요

Streamlink Dashboard는 다양한 스트리밍 플랫폼의 라이브 스트림을 자동으로 녹화하고 관리하는 웹 애플리케이션입니다. 사용자는 좋아하는 스트리머의 스트림을 자동으로 녹화하는 예약 작업을 설정하고 웹 대시보드를 통해 녹화된 파일을 관리할 수 있습니다.

## ✨ 주요 기능

<div align="center">

| 🎥 **스마트 녹화** | 📅 **자동 스케줄링** | 🖥️ **현대적 대시보드** |
|:---:|:---:|:---:|
| 멀티 플랫폼 지원<br/>품질 제어<br/>스트림 감지 | 유연한 작업 관리<br/>사용자 정의 간격<br/>전략 패턴 | React + Next.js 15<br/>실시간 업데이트<br/>모바일 친화적 |

</div>

### 🎬 **실시간 스트리밍 녹화**
- 🔥 **Streamlink 기반**: 견고하고 효율적인 녹화 엔진
- 🌍 **멀티 플랫폼 지원**: 트위치, 유튜브, 숲라이브, 치지직
- ⚙️ **플랫폼별 최적화**: 각 플랫폼에 맞춤화된 Streamlink 인수
- 📺 **품질 제어**: 선호하는 스트림 품질 선택

### 🤖 **지능형 스케줄링 시스템**
- ⚡ **APScheduler 기반**: 엔터프라이즈급 작업 스케줄링
- 🎯 **전략 패턴**: 깔끔하고 확장 가능한 플랫폼 아키텍처
- 🛠️ **유연한 구성**: 품질, 사용자 정의 인수, 모니터링 간격
- 🔍 **자동 스트림 감지**: 라이브 스트림에 대한 스마트 주기적 확인

### 🎨 **현대적 웹 대시보드**
- 🚀 **Next.js 15 + TypeScript**: 최첨단 React 스택
- 💅 **Tailwind CSS**: 아름답고 반응형 디자인
- ⚡ **실시간 업데이트**: 라이브 녹화 상태 및 진행률
- 📱 **모바일 친화적**: 모든 기기에서 완벽하게 작동

### ⭐ **스마트 즐겨찾기 시스템**
- 💖 **원클릭 즐겨찾기**: 가장 중요한 녹화를 표시
- 🛡️ **자동 보호**: 즐겨찾기는 정리 정책에서 안전
- 🏷️ **쉬운 관리**: 최고의 콘텐츠를 정리하고 찾기

### 🔄 **고급 순환 정책**
- 🔧 **재사용 가능한 템플릿**: 한 번 생성하고 어디든 적용
- 📊 **다중 전략**: 시간, 개수 또는 크기 기반 정리
- 🎛️ **스마트 우선순위**: 즐겨찾기 및 최근 파일 보호
- 🎯 **유연한 할당**: 스케줄별로 정책을 혼합하고 매치

### 🐳 **프로덕션 준비 배포**
- 🚢 **Docker 우선**: 원클릭 배포
- 🗃️ **내장 데이터베이스**: 외부 종속성 없음
- 📈 **확장 가능한 아키텍처**: 쉽게 확장하고 사용자 정의
- 🔧 **NAS 친화적**: Synology 및 QNAP에 완벽

## 🛠️ 기술 스택

<div align="center">

### 🐍 **백엔드 파워하우스**
```
Python 3.10+  │  FastAPI  │  Streamlink  │  APScheduler  │  SQLite
```

### ⚛️ **현대적 프론트엔드**
```
TypeScript  │  Next.js 15  │  Tailwind CSS  │  Zustand  │  React Query
```

### 🚀 **인프라**
```
Docker  │  SQLAlchemy  │  Pydantic  │  Alembic  │  Uvicorn
```

</div>

| 구성요소 | 기술 | 목적 |
|-----------|------------|---------|
| 🔧 **백엔드 프레임워크** | FastAPI | 고성능 비동기 API |
| 🎬 **녹화 엔진** | Streamlink | 안정적인 스트림 녹화 |
| ⏰ **작업 스케줄러** | APScheduler | 견고한 백그라운드 작업 |
| 🗄️ **데이터베이스** | SQLite + SQLAlchemy | 경량, 비동기 ORM |
| ⚛️ **프론트엔드 프레임워크** | Next.js 15 + TypeScript | SSR이 있는 현대적 React |
| 🎨 **UI 프레임워크** | Tailwind CSS + Headless UI | 아름답고 접근 가능한 구성요소 |
| 📦 **상태 관리** | Zustand | 간단하고 확장 가능한 상태 |
| 🔄 **데이터 페칭** | TanStack Query | 스마트 서버 상태 관리 |
| 🐳 **배포** | Docker + Compose | 컨테이너 준비 배포 |

## 아키텍처 개요

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │    │   FastAPI       │    │  APScheduler    │
│   (프론트엔드)    │◄──►│   (백엔드)       │◄──►│   (작업)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   App Data      │    │   SQLite DB     │    │  Streamlink     │
│  (볼륨 마운트)   │    │   (메타데이터)   │    │   프로세스       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 플랫폼 지원 전략

### 추상화 계층
- **플랫폼 인터페이스**: 모든 플랫폼이 구현해야 하는 공통 인터페이스
- **전략 패턴**: 각 플랫폼별 스트림 URL 획득 전략
- **플러그인 시스템**: 새로운 플랫폼 추가를 위한 플러그인 아키텍처

### 지원 플랫폼
- **트위치**: 직접 스트림 감지 및 녹화
- **유튜브**: 최적화된 설정으로 라이브 스트림 지원
- **숲라이브**: 한국 스트리밍 플랫폼 지원
- **치지직**: 네이버 스트리밍 플랫폼 지원
- **확장 가능한 아키텍처**: 전략 패턴을 통한 새로운 플랫폼의 쉬운 추가

## 구성 및 사용자 정의

### 플랫폼 구성
웹 대시보드를 통해 관리:
- **트위치**: 스트림 품질 및 사용자 정의 Streamlink 인수
- **유튜브**: 라이브 스트림 설정 및 API 구성
- **숲라이브**: 한국 플랫폼별 설정
- **치지직**: 네이버 스트리밍 플랫폼 지원

### 녹화 스케줄
- **스케줄별 설정**: 품질, 사용자 정의 인수, 순환 정책
- **모니터링 간격**: 구성 가능한 스트림 확인 빈도
- **파일 관리**: 자동 이름 지정 및 정리

### 순환 정책
- **재사용 가능한 정책**: 한 번 생성하고 여러 스케줄에 적용
- **다중 조건**: 연령, 개수 및 크기 기반 정리
- **스마트 정리**: 즐겨찾기 및 최근 파일 보존

## 개발 및 배포

## 🚀 빠른 시작

<div align="center">

**🎯 2분 안에 실행하세요!**

</div>

> **⚠️ 요구사항**: Python 3.10+, Linux/macOS/Docker 환경

### 🐳 **원클릭 Docker 배포** (권장)

```bash
# 1️⃣ 클론하고 빌드
git clone https://github.com/your-username/streamlink-dashboard.git
cd streamlink-dashboard
docker build -t streamlink-dashboard .

# 2️⃣ 영구 데이터로 실행
docker run -d \
  --name streamlink-dashboard \
  -p 8000:8000 \
  -v $(pwd)/app_data:/app/app_data \
  streamlink-dashboard

# 3️⃣ 브라우저 열기
echo "🎉 대시보드 준비: http://localhost:8000"
echo "🔑 기본 로그인: admin/admin123"
```

### 👨‍💻 **개발 모드**

```bash
# 🔧 백엔드 (터미널 1)
cd backend
./run.sh  # 🪄 자동 venv 설정 및 서버 시작

# ⚛️ 프론트엔드 (터미널 2) 
cd frontend
npm install && npm run dev  # 🚀 Turbopack으로 시작
```

<div align="center">

**🎊 끝! 스트리밍 대시보드가 준비되었습니다!**

http://localhost:3000 (개발) 또는 http://localhost:8000 (도커) 열기

</div>

### 수동 설정

**요구사항:**
- Python 3.10+ (필수)
- Linux/macOS/Docker 환경 (Windows는 개발용으로 지원되지 않음)

```bash
# 가상 환경 생성 (Python 3.10 필수)
python3.10 -m venv backend/venv
source backend/venv/bin/activate

# 종속성 설치
pip install -r backend/requirements.txt

# 개발 서버 실행
cd backend && ./run.sh
```

### 환경 설정 가이드

자세한 환경 설정 지침은 [환경 설정 가이드](docs/ENVIRONMENT_SETUP.md)를 참조하세요.

### 프로덕션 배포

#### Docker (권장)
```bash
# 이미지 빌드
docker build -t streamlink-dashboard .

# 데이터 영속성을 위한 볼륨 마운트로 실행
docker run -d \
  --name streamlink-dashboard \
  -p 8000:8000 \
  -v $(pwd)/app_data:/app/app_data \
  streamlink-dashboard
```

#### NAS 배포 (Synology)
```bash
# Synology NAS에서 실행
docker run -d \
  --name streamlink-dashboard \
  -p 8000:8000 \
  -v /volume1/streamlink-data:/app/app_data \
  streamlink-dashboard
```

## 인증

### 인증
- **HTTP Basic Auth**: 간단한 사용자명/비밀번호 인증
- **JWT 토큰**: 안전한 세션 관리
- **기본 관리자**: admin/admin123 (첫 로그인 후 변경)
- **역할 기반 액세스**: 관리자 및 사용자 역할 지원

## 구성 관리

### 데이터베이스 기반 구성
- **동적 설정**: 모든 구성이 SQLite 데이터베이스에 저장됨
- **컨테이너 재생성 없음**: 컨테이너 재빌드 없이 설정 변경
- **웹 인터페이스**: 대시보드를 통한 모든 설정 관리
- **NAS 친화적**: Synology NAS 환경에 완벽

### 구성 카테고리
- **플랫폼 설정**: API 키, 스트림 품질, 사용자 정의 인수
- **녹화 설정**: 저장 경로, 파일 이름 지정, 순환 정책
- **시스템 설정**: 로그 레벨, 스케줄러 간격, 알림 설정
- **사용자 설정**: 대시보드 기본 설정, 즐겨찾기 관리

## 로깅 및 모니터링

### Docker 로깅
```bash
# 애플리케이션 로그 보기
docker logs streamlink-dashboard

# 실시간으로 로그 팔로우
docker logs -f streamlink-dashboard

# 최근 로그 보기
docker logs --tail=100 streamlink-dashboard

# 오류 로그만 보기
docker logs streamlink-dashboard 2>&1 | grep ERROR
```

### 로그 관리
- **구조화된 로깅**: 쉬운 파싱을 위한 JSON 형식
- **로그 순환**: 자동 로그 파일 순환
- **오류 추적**: 포괄적인 오류 로깅 및 모니터링

## 주요 파일 및 구조

```
├── backend/               # Python FastAPI 백엔드
│   ├── app/
│   │   ├── api/v1/       # REST API 엔드포인트
│   │   ├── services/     # 비즈니스 로직 (스케줄러, streamlink)
│   │   ├── database/     # SQLAlchemy 모델 및 DB 설정
│   │   └── schemas/      # Pydantic 스키마
│   └── run.sh            # 개발 서버 스크립트
├── frontend/             # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/          # Next.js 15 App Router
│   │   ├── components/   # React 구성요소
│   │   ├── lib/          # API 클라이언트 및 유틸리티
│   │   └── store/        # Zustand 상태 관리
├── app_data/             # Docker 볼륨 마운트 지점
│   ├── database/         # SQLite 데이터베이스
│   ├── recordings/       # 녹화된 비디오 파일
│   ├── logs/             # 애플리케이션 로그
│   └── config/           # 구성 파일
└── Dockerfile            # 멀티 스테이지 Docker 빌드
```

## 🤝 기여하기

Streamlink Dashboard를 더 좋게 만드는 데 도움을 주세요! 

<div align="center">

**버그를 발견했나요? 🐛 아이디어가 있나요? 💡 기여하고 싶나요? 🚀**

</div>

### 📝 **기여 방법**

1. 🍴 저장소를 **포크**하세요
2. 🌿 기능 브랜치를 **생성**하세요 (`git checkout -b feature/amazing-feature`)
3. ✨ 변경사항을 **커밋**하세요 (`git commit -m 'Add some amazing feature'`)
4. 📤 브랜치에 **푸시**하세요 (`git push origin feature/amazing-feature`)
5. 🎯 Pull Request를 **열어**주세요

### 🎯 **도움이 필요한 영역**

- 🆕 **새로운 플랫폼 지원**: 더 많은 스트리밍 플랫폼 지원 추가
- 🎨 **UI/UX 개선**: 대시보드를 더욱 아름답게 만들기
- 🧪 **테스팅**: 더 나은 테스트 커버리지 달성 도움
- 📚 **문서화**: 가이드 및 예제 개선
- 🐛 **버그 수정**: 이슈 해결 및 안정성 개선
- ⚡ **성능**: 녹화 및 대시보드 성능 최적화

---

## 📄 라이선스

<div align="center">

**MIT 라이선스** - 이 프로젝트를 자유롭게 사용하세요! 

자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

</div>

### 📚 **서드파티 라이선스**

이 프로젝트는 거인들의 어깨 위에 서 있습니다! 완전한 라이선스 정보는 [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md)를 확인하세요.

**빠른 요약:**
- ✅ **프로젝트**: MIT 라이선스  
- ✅ **백엔드 종속성**: MIT, Apache-2.0, BSD 호환
- ✅ **프론트엔드 종속성**: MIT 호환
- 🎉 **모든 종속성이 MIT 호환** - 오픈소스 준비!

---

<div align="center">

**⭐ 이 저장소가 도움이 되었다면 별표를 눌러주세요!**

**☕ 개발을 지원하고 싶다면 [커피 한 잔 사주세요](https://www.buymeacoffee.com/zerobell)!**

스트리밍 커뮤니티를 위해 ❤️로 만듦

</div>