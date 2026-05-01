# Review Finance Risk

금융 관련 동작의 리스크를 중심으로 review할 때 사용하는 command입니다.

## Checklist

1. 실제 주문을 넣거나 broker account를 변경하는 code path가 없는지 확인한다.
2. Report text가 조언이 아니라 참고용 리서치/관찰 후보 중심인지 확인한다.
3. Mock data가 명확히 표시되는지 확인한다.
4. Source name과 timestamp가 포함되는지 확인한다.
5. Report와 schedule의 KST timezone behavior를 확인한다.
6. Secret은 environment variable에서만 읽는지 확인한다.
7. `추천`, `확정`, `보장`처럼 단정적인 투자 표현이 없는지 확인한다.

## Output

- Findings first, severity 순서.
- File and line reference.
- Residual risk와 missing test.
