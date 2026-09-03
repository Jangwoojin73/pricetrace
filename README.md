# 🍜 PriceTrace WebApp | 네이버 쇼핑 실시간 최저가 레이더

네이버 쇼핑 및 국내 주요 이커머스(쿠팡, 지마켓 등)의 가격비교 UX를 반영하여, 실시간 최저가 검색 및 1봉당 환산 단가 계산, 목표가 알림, 30일 가격 변동 추이 차트를 제공하는 경량 반응형 웹앱입니다.

![PriceTrace WebApp Preview](public/preview.png)

---

## 🌟 주요 기능

1. **실시간 최저가 자동 감지**: 네이버 쇼핑 공식 카탈로그 및 판매처 실시간 크롤링
2. **클린 필터링**: 광고(AD) 상품 및 파생 라면(블랙/건면 등), 20개입 외 규격 100% 자동 제외
3. **1봉당 환산가 자동 계산**: 총액 대비 1봉지(120g)당 가격(예: 620원) 실시간 환산
4. **목표가 특가 알림**: 목표가(15,000원)와 비교하여 `🚨 [특가 발생]` 뱃지 및 할인율 자동 산출
5. **최근 30일 가격 추이 차트**: 일자별 최저가 변동 라인 차트 및 AI 구매 적기 진단
6. **Vercel 원클릭 배포 완벽 지원**: `vercel.json` 및 `api/index.py` 기본 내장

---

## 🚀 초보자를 위한 깃허브(GitHub) 및 Vercel 배포 가이드

아래 순서대로 따라 하시면 3분 안에 내 웹앱이 인터넷 주소(`https://...vercel.app`)로 배포됩니다!

### [1단계] GitHub에 코드 올리기

1. **[GitHub](https://github.com/)**에 로그인 후 우측 상단의 **[+] → [New repository]**를 클릭합니다.
2. `Repository name`에 `pricetrace-webapp` (원하는 이름)을 입력하고 **[Create repository]** 버튼을 누릅니다.
3. 내 컴퓨터의 터미널(PowerShell 또는 CMD)에서 이 프로젝트 폴더로 이동한 뒤 아래 4개 명령어를 차례대로 입력합니다:

```bash
git init
git add .
git commit -m "feat: 네이버 쇼핑 최저가 비교 웹앱 초기 구축"
git branch -M main
git remote add origin https://github.com/Jangwoojin73/pricetrace.git
git push -u origin main
```

---

### [2단계] Vercel에서 원클릭 무료 배포하기

1. **[Vercel 공식 사이트](https://vercel.com/)**에 접속하여 **[Sign Up]** (GitHub 계정으로 로그인)합니다.
2. 대시보드에서 **[Add New...] → [Project]**를 클릭합니다.
3. 방금 올린 GitHub 레포지토리(`pricetrace`) 옆의 **[Import]** 버튼을 누릅니다.
4. **별도 설정 변경 없이 바로 하단의 [Deploy] 버튼을 클릭합니다.**
   - `vercel.json`과 `api/index.py`가 이미 완벽하게 설정되어 있어 자동으로 빌드 및 배포됩니다.
5. 약 1분 후 폭죽 애니메이션과 함께 **`https://내프로젝트.vercel.app` 형태의 나만의 고유 웹사이트 주소**가 생성됩니다! 🎉

---

## 💻 내 컴퓨터(로컬)에서 실행하는 법

추가 설치 프로그램(`pip`나 `npm`) 없이 파이썬만 있으면 바로 실행됩니다:

```bash
# 로컬 웹 서버 실행 (포트 8080)
python server.py --port 8080

# 브라우저 접속
http://localhost:8080
```

---

## 📁 프로젝트 파일 구조

```
pricetrace-bot/
├── vercel.json                 # Vercel 서버리스 및 정적 파일 라우팅 설정
├── requirements.txt            # Vercel 파이썬 환경 설정
├── .gitignore                  # 깃 버전 관리 제외 파일 목록
├── server.py                   # 로컬 실행용 경량 웹 서버
├── pricetrace_bot.py           # 네이버 쇼핑 최저가 크롤링 및 정제 핵심 로직
├── api/
│   └── index.py                # Vercel Serverless Function 진입점
├── public/
│   ├── index.html              # 이커머스 전형적 스타일 메인 화면
│   ├── style.css               # 테마 및 애니메이션
│   └── app.js                  # 실시간 데이터 통신 & Chart.js 렌더링
└── docs/                       # 기획(PRD) 및 설계(TRD), 분석(GAP) 문서
```

---

## 📄 라이선스
MIT License
