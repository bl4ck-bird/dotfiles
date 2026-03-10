# -------------------------------------------------------------------
# [필수 GNU 도구]
# -------------------------------------------------------------------
# GNU Sed: macOS BSD sed의 '-i' (in-place) 백업 확장자 필수 요구 등 비표준 동작 해결
if (( $+commands[gsed] )); then safe_alias sed="gsed"; fi

# GNU Tar: 리눅스 환경과 100% 동일한 압축 해제/생성 옵션 보장
if (( $+commands[gtar] )); then safe_alias tar="gtar"; fi

# GNU Make: 구형(3.81) 대신 병렬 처리 및 최신 문법 지원 (최신 4.x)
if (( $+commands[gmake] )); then safe_alias make="gmake"; fi

# GNU Awk: 더 빠르고 복잡한 정규식과 네트워크 확장을 지원
if (( $+commands[gawk] )); then safe_alias awk="gawk"; fi


# -------------------------------------------------------------------
# [GNU Coreutils] (현재 보류 - 필요시 패키지 설치 후 주석 해제)
# -------------------------------------------------------------------

# [1. 시간, 경로, 심볼릭 링크]
# 직관적인 자연어 시간 연산(tomorrow, 1 hour ago 등) 완벽 지원
if (( $+commands[gdate] ));     then safe_alias date="gdate"; fi
# 지정된 시간 동안만 명령어 실행 제한 (macOS에는 명령어 자체가 없음)
if (( $+commands[gtimeout] ));  then safe_alias timeout="gtimeout"; fi
# 심볼릭 링크의 원본 절대 경로를 정확히 추적
if (( $+commands[grealpath] )); then safe_alias realpath="grealpath"; fi
# 심볼릭 링크가 가리키는 값 읽기 (macOS readlink는 -f 옵션 미지원)
# if (( $+commands[greadlink] )); then safe_alias readlink="greadlink"; fi
# 파일 경로에서 디렉토리 부분만 추출
# if (( $+commands[gdirname] ));  then safe_alias dirname="gdirname"; fi
# 파일 경로에서 파일 이름만 추출
# if (( $+commands[gbasename] )); then safe_alias basename="gbasename"; fi

# [2. 파일 및 디렉토리 권한/제어]
# 파일 상태 출력 (BSD와 GNU의 출력 포맷 파라미터 -c vs -f 차이 극복)
# if (( $+commands[gstat] ));     then safe_alias stat="gstat"; fi
# 파일 복사 시 원본 속성 완벽 보존(-a) 및 고급 백업 옵션 제공
# if (( $+commands[gcp] ));       then safe_alias cp="gcp"; fi
# 파일 이동 시 상세 진행률 및 안전한 덮어쓰기 옵션 제공
# if (( $+commands[gmv] ));       then safe_alias mv="gmv"; fi
# 파일 삭제 시 빈 디렉토리 처리 및 안전 삭제 기능 개선
# if (( $+commands[grm] ));       then safe_alias rm="grm"; fi
# 디렉토리 생성
# if (( $+commands[gmkdir] ));    then safe_alias mkdir="gmkdir"; fi
# 빈 디렉토리 삭제
# if (( $+commands[grmdir] ));    then safe_alias rmdir="grmdir"; fi
# 파일의 타임스탬프 업데이트 또는 빈 파일 생성
# if (( $+commands[gtouch] ));    then safe_alias touch="gtouch"; fi
# 하드 링크 및 심볼릭 링크 생성
# if (( $+commands[gln] ));       then safe_alias ln="gln"; fi
# 파일 소유자 및 그룹 변경
# if (( $+commands[gchown] ));    then safe_alias chown="gchown"; fi
# 파일 권한 변경
# if (( $+commands[gchmod] ));    then safe_alias chmod="gchmod"; fi
# 파일 그룹 변경
# if (( $+commands[gchgrp] ));    then safe_alias chgrp="gchgrp"; fi
# 안전한 임시 파일 및 임시 디렉토리 생성
# if (( $+commands[gmktemp] ));   then safe_alias mktemp="gmktemp"; fi
# 파일을 복구할 수 없도록 안전하게 덮어쓰고 삭제 (보안 삭제)
# if (( $+commands[gshred] ));    then safe_alias shred="gshred"; fi

# [3. 텍스트 파싱, 정렬, 출력]
# 텍스트 라인 정렬 (버전 번호 정렬 -V 등 고급 정렬 지원)
# if (( $+commands[gsort] ));     then safe_alias sort="gsort"; fi
# Base64 인코딩/디코딩 (macOS 기본 도구와 줄바꿈 처리 옵션 차이 극복)
# if (( $+commands[gbase64] ));   then safe_alias base64="gbase64"; fi
# 파일 내용 출력 및 병합
# if (( $+commands[gcat] ));      then safe_alias cat="gcat"; fi
# 파일 내용을 역순(아래에서 위로)으로 출력 (macOS에는 없음)
# if (( $+commands[gtac] ));      then safe_alias tac="gtac"; fi
# 파일의 마지막 부분 출력 (소수점 단위 용량 등 정밀 제어 지원)
# if (( $+commands[gtail] ));     then safe_alias tail="gtail"; fi
# 파일의 시작 부분 출력
# if (( $+commands[ghead] ));     then safe_alias head="ghead"; fi
# 파일의 줄, 단어, 바이트 수 계산
# if (( $+commands[gwc] ));       then safe_alias wc="gwc"; fi
# 중복된 텍스트 라인 제거
# if (( $+commands[guniq] ));     then safe_alias uniq="guniq"; fi
# 파일의 각 라인에서 특정 필드 추출
# if (( $+commands[gcut] ));      then safe_alias cut="gcut"; fi
# 여러 파일의 라인을 나란히 병합
# if (( $+commands[gpaste] ));    then safe_alias paste="gpaste"; fi
# 공통 필드를 기준으로 두 파일의 라인 결합
# if (( $+commands[gjoin] ));     then safe_alias join="gjoin"; fi
# 파일을 여러 개의 작은 파일로 분할
# if (( $+commands[gsplit] ));    then safe_alias split="gsplit"; fi
# 문자 변환 및 삭제
# if (( $+commands[gtr] ));       then safe_alias tr="gtr"; fi

# [4. 해시, 시퀀스, 계산기]
# MD5 해시값 계산 및 검증 (macOS는 호환되지 않는 md5 명령어 사용)
# if (( $+commands[gmd5sum] ));   then safe_alias md5sum="gmd5sum"; fi
# SHA-1 해시값 계산 및 검증
# if (( $+commands[gsha1sum] ));  then safe_alias sha1sum="gsha1sum"; fi
# SHA-256 해시값 계산 및 검증 (macOS는 shasum -a 256 사용)
# if (( $+commands[gsha256sum] ));then safe_alias sha256sum="gsha256sum"; fi
# 숫자의 시퀀스(수열) 출력 (쉘 스크립트 반복문에 유용)
# if (( $+commands[gseq] ));      then safe_alias seq="gseq"; fi
# 텍스트 라인을 무작위로 섞거나 난수 생성 (macOS에는 없음)
# if (( $+commands[gshuf] ));     then safe_alias shuf="gshuf"; fi
# 수식 계산 및 문자열 패턴 매칭
# if (( $+commands[gexpr] ));     then safe_alias expr="gexpr"; fi
# 숫자의 소인수분해
# if (( $+commands[gfactor] ));   then safe_alias factor="gfactor"; fi

# [5. 시스템 정보 및 기타]
# 현재 사용자와 그룹의 ID 출력
# if (( $+commands[gid] ));       then safe_alias id="gid"; fi
# 현재 유효한 사용자 이름 출력
# if (( $+commands[gwhoami] ));   then safe_alias whoami="gwhoami"; fi
# 사용자가 속한 그룹 목록 출력
# if (( $+commands[ggroups] ));   then safe_alias groups="ggroups"; fi
# 시스템 및 커널 정보 출력
# if (( $+commands[guname] ));    then safe_alias uname="guname"; fi
# 환경 변수 설정 및 명령어 실행
# if (( $+commands[genv] ));      then safe_alias env="genv"; fi
# 환경 변수 값 출력
# if (( $+commands[gprintenv] )); then safe_alias printenv="gprintenv"; fi
# 터미널 세션이 끊겨도 백그라운드에서 명령어 계속 실행
# if (( $+commands[gnohup] ));    then safe_alias nohup="gnohup"; fi
# 지정된 시간 동안 대기 (소수점 단위 초 지원)
# if (( $+commands[gsleep] ));    then safe_alias sleep="gsleep"; fi
