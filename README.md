# 🛠️ dotfiles

My dotfiles, provisioned and managed by [`chezmoi`](https://github.com/twpayne/chezmoi).

## 📋 Prerequisites

### Minimal Dependencies

- git, curl

#### macOS

**Install XCode CLI Tools**:

```sh
xcode-select --install
```

## 🚀 Provisioning & Apply

실행 환경(Runtime Context)에 따라 가장 적합한 부트스트래핑 방식을 선택하십시오.

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
