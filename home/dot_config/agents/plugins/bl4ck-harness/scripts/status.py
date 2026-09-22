"""상태 Markdown의 형식과 명백한 완료 모순만 확인한다."""

import re


STATES = {'미착수', '진행 중', '검토 중', '보류', '완료', '실행 확인 필요'}
SECTIONS = ('현재 상태', '작업', '확인할 실행', '차단 사항', '검증', '다음 행동')


def prose_lines(text):
    fence = None
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            if re.fullmatch(r'\s*' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*', line):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        yield line


def has_status_fields(text):
    current = False
    for line in prose_lines(text):
        heading = re.fullmatch(r'##\s+(.+?)\s*', line)
        if heading:
            current = heading.group(1) == '현재 상태'
        elif current and re.match(r'\s*-\s*상태\s*:', line):
            return True
    return False


def validate_status(text):
    """검사 실패는 ValueError, 성공은 전체 상태를 반환한다."""
    sections = {}
    active = None
    title = False
    for line in prose_lines(text):
        if re.match(r'^#\s+\S', line):
            title = True
        heading = re.fullmatch(r'##\s+(.+?)\s*', line)
        if heading:
            active = heading.group(1)
            if active in sections:
                raise ValueError('중복된 항목: ' + active)
            sections[active] = []
        elif active:
            sections[active].append(line)
    if not title:
        raise ValueError('변경을 설명하는 제목이 없습니다.')
    for name in SECTIONS:
        if not ''.join(sections.get(name, [])).strip():
            raise ValueError('필수 항목이 없거나 비어 있습니다: ' + name)
    fields = {}
    for line in sections['현재 상태']:
        match = re.fullmatch(r'\s*-\s*(단계|상태)\s*:\s*(.+?)\s*', line)
        if match:
            key, value = match.groups()
            if key in fields:
                raise ValueError('중복된 현재 상태 필드: ' + key)
            fields[key] = value
    if not fields.get('단계') or fields.get('상태') not in STATES:
        raise ValueError('현재 상태에 단계와 유효한 상태를 작성하세요.')
    tasks = [line.strip() for line in sections['작업'] if line.strip()]
    task_states = []
    if tasks != ['없음']:
        rows = []
        for line in tasks:
            row = [cell.strip() for cell in re.split(r'(?<!\\)\|', line.strip('|'))]
            if len(row) != 2:
                raise ValueError('작업 표는 작업·상태 두 열을 사용하세요.')
            rows.append(row)
        if (len(rows) < 3 or rows[0] != ['작업', '상태']
                or not all(re.fullmatch(r':?-{3,}:?', cell) for cell in rows[1])):
            raise ValueError('작업 표의 제목·구분선·작업 행을 확인하세요.')
        names = set()
        for name, state in rows[2:]:
            if not name or name in names or state not in STATES:
                raise ValueError('작업 이름의 누락·중복 또는 잘못된 상태가 있습니다.')
            names.add(name)
            task_states.append(state)
    if fields['상태'] == '완료':
        if not task_states or any(state != '완료' for state in task_states):
            raise ValueError('완료 상태에는 완료된 작업이 필요하며 미완료 작업을 남길 수 없습니다.')
        for name in ('확인할 실행', '차단 사항'):
            if '\n'.join(sections[name]).strip() != '없음':
                raise ValueError('완료 상태에 남은 항목이 있습니다: ' + name)
    return fields['상태']
