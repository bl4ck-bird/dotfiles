# Zsh 히스토리 최적화 (XDG 격리)
[[ -d "$XDG_STATE_HOME/zsh" ]] || mkdir -p "$XDG_STATE_HOME/zsh"
export HISTFILE="$XDG_STATE_HOME/zsh/history"
export HISTSIZE=100000
export SAVEHIST=$HISTSIZE

# 대화형 쉘 프롬프트에서 "#" 기호를 사용한 주석 처리 허용
setopt INTERACTIVE_COMMENTS

# 모든 zsh 세션(터미널 탭/창) 간에 히스토리를 실시간으로 공유
setopt SHARE_HISTORY

# 명령어 기록 시 불필요한 연속 공백을 하나로 줄여서 깔끔하게 저장
setopt HIST_REDUCE_BLANKS

# 히스토리 확장(예: !!) 사용 시 명령어를 즉시 실행하지 않고 프롬프트에 불러와 확인 및 수정 가능하게 함
setopt HIST_VERIFY

# 명령어 실행 시작 타임스탬프 및 소요 시간을 히스토리에 함께 저장
setopt EXTENDED_HISTORY

# 히스토리 파일 크기 제한을 초과하여 기록을 지울 때, 중복된 항목부터 우선 삭제
setopt HIST_EXPIRE_DUPS_FIRST

# 쉘 종료 시 기존 히스토리 파일을 덮어쓰지 않고 새로운 기록만 덧붙임
setopt APPEND_HISTORY

# 쉘 종료를 기다리지 않고 명령어가 실행되는 즉시 히스토리 파일에 저장
setopt INC_APPEND_HISTORY

# 직전에 실행한 명령어와 완전히 동일한 명령어는 히스토리에 중복 기록하지 않음
setopt HIST_IGNORE_DUPS

# 명령어 앞에 공백(Space)을 입력하고 실행한 경우 히스토리에 기록하지 않음 (보안/1회성 명령어용)
setopt HIST_IGNORE_SPACE
