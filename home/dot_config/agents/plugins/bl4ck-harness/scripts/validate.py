#!/usr/bin/env python3
"""배포 패키지의 이름·문서 연결·한글 지침을 오프라인으로 확인한다."""

import json
from pathlib import Path
import re
import sys

from harness import contained, local_links


def main():
    root = Path(__file__).resolve().parent.parent
    errors = []
    manifest = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    source_layout = manifest.get('name') == root.name
    installed_layout = (manifest.get('name') == root.parent.name
                        and manifest.get('version') == root.name)
    if not (source_layout or installed_layout) or manifest.get('skills') != './skills/':
        errors.append('플러그인 이름·스킬 경로가 실제 패키지와 일치하지 않습니다.')
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:\+codex\.[A-Za-z0-9.-]+)?', manifest.get('version', '')):
        errors.append('버전은 세 부분의 숫자와 선택적인 Codex 캐시 갱신 접미사 형식이어야 합니다.')
    paths = list((root / 'skills').glob('*/SKILL.md'))
    names = {path.parent.name for path in paths}
    if 'using-bl4ck-harness' not in names:
        errors.append('진입 스킬이 없습니다.')
    for path in paths:
        content = path.read_text(encoding='utf-8')
        if not content.startswith('---\n') or '\n---\n' not in content[4:]:
            errors.append(str(path) + ': 메타데이터가 없습니다.')
            continue
        front, body = content[4:].split('\n---\n', 1)
        values = dict(line.split(':', 1) for line in front.splitlines() if ':' in line)
        name = values.get('name', '').strip()
        if name != path.parent.name or (name != 'using-bl4ck-harness' and not name.startswith('bl4ck-harness-')):
            errors.append(str(path) + ': 스킬 이름이 일치하지 않습니다.')
        if not re.search('[가-힣]', values.get('description', '')):
            errors.append(str(path) + ': 한글 설명이 없습니다.')
        if name != 'using-bl4ck-harness' and '../using-bl4ck-harness/references/' not in body:
            errors.append(str(path) + ': 단독 호출용 공통 기준 참조가 없습니다.')
        for reference in re.findall(r'`((?:bl4ck-harness-[a-z-]+|using-bl4ck-harness))`', body):
            if reference not in names:
                errors.append(str(path) + ': 존재하지 않는 스킬 ' + reference)
    for path in root.rglob('*.md'):
        content = path.read_text(encoding='utf-8')
        for target in local_links(content):
            resolved = (path.parent / target).resolve()
            if not contained(root, resolved) or not resolved.exists():
                errors.append(str(path.relative_to(root)) + ': 잘못된 로컬 참조 ' + target)
        for line in content.splitlines():
            if re.match(r'^#{1,6} ', line) and not re.search('[가-힣]', line) and line != '# bl4ck-harness':
                errors.append(str(path.relative_to(root)) + ': 한글이 아닌 제목 ' + line)
        if '[TODO:' in content or 'superpowers:' in content or 'dmi-superpowers:' in content:
            errors.append(str(path.relative_to(root)) + ': 미완성 표식 또는 원본 호출이 남아 있습니다.')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('패키지 검사 통과: 스킬 ' + str(len(paths)) + '개, 메타데이터·참조·한글 제목·호출 이름 확인')
    return 0


if __name__ == '__main__':
    sys.exit(main())
