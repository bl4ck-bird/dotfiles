# Review Prompt Selection

메인 에이전트가 현재 판단에 맞는 프롬프트만 선택해 리뷰어에게 실제 대상·요구·근거·검증 권한·보고 위치와 함께 전달한다. 공통 [리뷰 기준](contract.md)과 적용되는 품질·보안·테스트 참조를 명시하며 전체 설계 이력을 넘기지 않는다.

| Stage | Prompt |
| --- | --- |
| 문제 탐색 | [Discovery](prompts/discovery.md) |
| 시스템 설계 | [Design](prompts/design.md) |
| 성과·우선순위 | [Roadmap](prompts/roadmap.md) |
| 상세 명세 | [Specification](prompts/spec.md) |
| 구현 계획 | [Plan](prompts/plan.md) |
| 슬라이스 구현 결과 | [Implementation](prompts/implementation.md) |
| 이전 지적 사항의 수정 | [Re-review](prompts/re-review.md) |
| 별도로 요청한 최종 검토 | [Final](prompts/final.md) |

축약 명세·계획은 두 프롬프트의 관점을 한 배정에 결합할 수 있다. 파일 두 개가 호출 두 번을 요구하지 않는다. 검토 권한과 대상의 사용자 승인은 구분하며, 최종 프롬프트의 존재만으로 추가 리뷰를 만들지 않는다.
