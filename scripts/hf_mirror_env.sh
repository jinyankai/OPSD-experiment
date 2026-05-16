#!/usr/bin/env bash
# Shared Hugging Face download settings for experiment scripts.
#
# Default behavior uses https://hf-mirror.com because direct access to
# huggingface.co may be unavailable on some servers. Override with:
#   HF_ENDPOINT=https://huggingface.co bash scripts/run_opsd_1b.sh
# Disable the mirror default entirely with:
#   USE_HF_MIRROR=0 bash scripts/run_opsd_1b.sh

if [[ "${USE_HF_MIRROR:-1}" != "0" ]]; then
    export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
    export HUGGINGFACE_CO_RESOLVE_ENDPOINT="${HUGGINGFACE_CO_RESOLVE_ENDPOINT:-$HF_ENDPOINT}"
fi

if [[ "${PRINT_HF_ENDPOINT:-1}" != "0" ]]; then
    echo "[hf] HF_ENDPOINT=${HF_ENDPOINT:-<unset>}"
fi
