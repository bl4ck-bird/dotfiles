"""상태 검사로 실제 완료 모순을 거부하고 기록을 보존하는지 확인한다."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/harness.py'
STATUS = '''# 폴더 가져오기

## 현재 상태
- 단계: 구현
- 상태: 진행 중

## 작업
| 작업 | 상태 |
| --- | --- |
| 폴더 읽기 | 완료 |
| 중복 처리 | 진행 중 |

## 확인할 실행
없음

## 차단 사항
없음

## 검증
폴더 읽기 테스트 통과. 중복 처리는 아직 검증하지 않음.

## 다음 행동
중복 처리 구현과 검증을 마무리한다.
'''

class StatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        result = self.run_tool('init')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.path = self.root / '.harness/changes/folder-import/status.md'
        self.path.parent.mkdir(parents=True)
        self.path.write_text(STATUS, encoding='utf-8')
        self.current = self.root / '.harness/CURRENT.md'
        self.current.write_text('# 현재 상태\n\n[폴더 가져오기](changes/folder-import/status.md)\n', encoding='utf-8')

    def run_tool(self, command):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), command, '--root', str(self.root)], capture_output=True, text=True)

    def check(self, content, expected):
        self.path.write_text(content, encoding='utf-8')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.run_tool('check')
        self.assertEqual(result.returncode, expected, result.stderr)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after, '검사가 기록을 변경했습니다.')
        return result

    def test_in_progress_accepts_unfinished_work_and_blocker(self):
        self.check(STATUS.replace('## 차단 사항\n없음', '## 차단 사항\n중복 정책에 대한 사용자 결정이 필요함'), 0)

    def test_completed_rejects_pending_task(self):
        result = self.check(STATUS.replace('- 상태: 진행 중', '- 상태: 완료'), 1)
        self.assertIn('미완료 작업', result.stderr)

    def test_completed_rejects_unknown_execution_and_blocker(self):
        completed = STATUS.replace('진행 중', '완료')
        for section, problem in [('확인할 실행', '검색 테스트 실행 ID 123의 종료 확인 필요'), ('차단 사항', '공유 권한 결정 필요')]:
            with self.subTest(section=section):
                result = self.check(completed.replace('## ' + section + '\n없음', '## ' + section + '\n' + problem), 1)
                self.assertIn(section, result.stderr)

    def test_completed_accepts_closed_work_without_current_link(self):
        self.current.write_text('# 현재 상태\n\n활성 변경 없음\n', encoding='utf-8')
        self.check(STATUS.replace('진행 중', '완료').replace('중복 처리는 아직 검증하지 않음.', '중복 처리 테스트 통과.'), 0)

    def test_active_change_requires_current_link(self):
        self.current.write_text('# 현재 상태\n\n폴더 가져오기를 진행 중\n', encoding='utf-8')
        result = self.check(STATUS, 1)
        self.assertIn('CURRENT.md', result.stderr)

    def test_nested_fenced_links_are_examples_but_real_links_are_checked(self):
        for marker in ('`', '~'):
            with self.subTest(marker=marker):
                example = marker * 4 + 'markdown\n' + marker * 3 + 'markdown\n[예시](missing.md)\n' + marker * 3 + '\n' + marker * 4 + '\n'
                active = '[폴더 가져오기](changes/folder-import/status.md)\n'
                self.current.write_text('# 현재 상태\n\n' + example + active, encoding='utf-8')
                self.check(STATUS, 0)
                self.current.write_text('# 현재 상태\n\n' + example + active + '[누락](missing.md)\n', encoding='utf-8')
                result = self.check(STATUS, 1)
                self.assertIn('missing.md', result.stderr)

    def test_reference_style_active_link_explains_supported_syntax(self):
        self.current.write_text('# 현재 상태\n\n[폴더 가져오기][active]\n\n[active]: changes/folder-import/status.md\n', encoding='utf-8')
        result = self.check(STATUS, 1)
        self.assertIn('[변경](changes/folder-import/status.md)', result.stderr)

    def test_missing_or_empty_required_section_is_rejected(self):
        for text in [STATUS.replace('## 다음 행동', '## 참고'), STATUS.replace('중복 처리 구현과 검증을 마무리한다.', '')]:
            with self.subTest(text=text):
                result = self.check(text, 1)
                self.assertIn('다음 행동', result.stderr)

    def test_conflicting_status_and_malformed_table_are_rejected(self):
        for text in [STATUS.replace('- 상태: 진행 중', '- 상태: 진행 중\n- 상태: 완료'), STATUS.replace('| 중복 처리 | 진행 중 |', '| 중복 처리 | 거의 완료 |'), STATUS.replace('| 중복 처리 | 진행 중 |', '| 폴더 읽기 | 완료 |'), STATUS.replace('| --- | --- |', '| --- |')]:
            with self.subTest(text=text):
                self.check(text, 1)

    def test_early_design_can_have_no_tasks(self):
        text = STATUS.replace('| 작업 | 상태 |\n| --- | --- |\n| 폴더 읽기 | 완료 |\n| 중복 처리 | 진행 중 |', '없음')
        self.check(text, 0)
        self.check(text.replace('- 상태: 진행 중', '- 상태: 완료'), 1)

    def test_fenced_example_cannot_supply_missing_sections(self):
        self.check('```markdown\n' + STATUS + '```\n', 1)
        self.check(STATUS + '\n```markdown\n' + STATUS + '```\n', 0)

    def test_old_snapshot_status_is_not_revalidated(self):
        old = self.path.parent / 'snapshots/previous/status.md'
        old.parent.mkdir(parents=True)
        old.write_text('# 이전 형식의 상태\n', encoding='utf-8')
        self.check(STATUS, 0)

    def test_unlinked_legacy_status_is_preserved_and_reported(self):
        old = self.root / '.harness/changes/previous/status.md'
        old.parent.mkdir(parents=True)
        old.write_text('# 이전 변경\n\n구현과 검증을 완료했다.\n', encoding='utf-8')
        result = self.check(STATUS, 0)
        self.assertIn('상태 형식 미검사', result.stdout)
        self.assertIn('1개', result.stdout)

    def test_current_linked_legacy_status_requires_current_format(self):
        result = self.check('# 재개할 변경\n\n구현을 이어가야 함\n', 1)
        self.assertIn('필수 항목', result.stderr)

if __name__ == '__main__':
    unittest.main()
