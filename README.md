# 🛠️ dotfiles

My dotfiles, provisioned and managed by [`chezmoi`](https://github.com/twpayne/chezmoi).

## 📋 1. Prerequisites

### 🔐 Authentication (Bootstrap)

이 저장소는 **Private**으로 격리되어 있으므로, 초기 셋업(Pull)을 위해 HTTPS 기반의 일회성 인증 토큰이 필요합니다.

1. [GitHub Fine-grained PAT](https://github.com/settings/tokens?type=beta) 생성
2. **Repository access**: `Only select repositories` ➡️ `dotfiles` 선택
3. **Permissions**: `Contents` ➡️ `Read-only` Or `Read and write`

> 💡 **Note**: 해당 PAT는 최초 부트스트래핑 과정의 닭과 달걀(Chicken-and-Egg) 문제를 해결하기 위한 용도입니다. 셋업 시 Git Config(`url."git@github.com:".insteadOf`)가 주입되어 향후 모든 통신은 SSH 프로토콜로 자동 전환됩니다.

### 📦 Minimal Dependencies (Container / Headless)

Alpine Linux 등 최소 설치 환경에서는 부트스트랩 스크립트 파이프라인을 실행하기 위해 아래 패키지가 선행되어야 합니다.

```sh
apk add --no-cache curl git
```

## 🚀 2. Provisioning & Apply

실행 환경(Runtime Context)에 따라 가장 적합한 부트스트래핑 방식을 선택하십시오.
Git 자격 증명(Credential) 프롬프트 발생 시, 발급받은 PAT를 Password란에 입력합니다.

**🟢 Zero-Base (새 Mac, 깡통 VM)**
`chezmoi`가 없고 저장소도 클론되지 않은 환경입니다. 공식 설치기를 경유하여 바이너리 설치(`~/.local/bin`)와 템플릿 렌더링을 단번에 체이닝합니다.

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- -b ~/.local/bin init --apply bl4ck-bird
```

**🟡 CDE & Dev Containers (저장소가 이미 클론된 환경)**
GitHub Codespaces나 VS Code Dev Containers처럼 플랫폼 엔진이 저장소를 이미 물리 디스크에 복제해둔 상태라면, 레포지토리 내부에 있는 진입점 스크립트를 직접 실행합니다.

```sh
./install.sh
```

> 💡 **VS Code 자동화**: 로컬 에디터 설정에 `"dotfiles.repository": "bl4ck-bird/dotfiles", "dotfiles.targetPath": "~/dotfiles", "dotfiles.installCommand": "install.sh"`를 주입하면 컨테이너 생성 시 100% 자동 적용됩니다.

**🔵 Pre-installed (`chezmoi` 기설치 환경)**
이미 시스템에 패키지 매니저(Homebrew 등)를 통해 `chezmoi` 바이너리가 존재하는 경우, 내장 명령어로 즉시 초기화합니다.

```sh
chezmoi init --apply bl4ck-bird
```
