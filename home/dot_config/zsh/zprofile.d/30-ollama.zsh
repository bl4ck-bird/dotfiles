if (( $+commands[ollama] )); then
    # 모델 저장 경로
    export OLLAMA_MODELS="$XDG_DATA_HOME/ollama/models"
    [[ -d "$OLLAMA_MODELS" ]] || mkdir -p "$OLLAMA_MODELS"

    # 모델 동시 로드 제한
    export OLLAMA_MAX_LOADED_MODELS=1

    # 모델 메모리 상주 시간
    export OLLAMA_KEEP_ALIVE="24h"

    # 병령 요청 제한
    export OLLAMA_NUM_PARALLEL=1

    # KV 캐시 양자화
    export OLLAMA_KV_CACHE_TYPE="q4_0"

    # 클라우드 기능 제외
    export OLLAMA_NO_CLOUD=1

    # MoE 아키텍처와 긴 컨텍스트 처리 시 연산 속도를 획기적으로 가속
    export OLLAMA_FLASH_ATTENTION=1

    # Contenxt 제한
    export OLLAMA_NUM_CTX=32768

    # Run: ollama serve
fi
