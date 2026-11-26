# 공개 페이지용 데이터 정리: 사내 시스템·테스트/QA/개발 서버 주소가 들어간 행을 뺍니다.
# 사용: python3 sanitize.py <CSV 폴더>   (폴더 안 CSV를 그 자리에서 고쳐 씁니다)
import csv, glob, re, sys, io
PAT = re.compile(r'(qawww\d*\.|lswww\.|gdev|gitlab|atlassian\.net|gcadmin|hr\.gabiacns|(^|[/.\s])dev\.|사내 시스템|테스트 서버|staging\.)', re.I)
for p in sorted(glob.glob(sys.argv[1].rstrip('/') + '/*.csv')):
    text = open(p, encoding='utf-8').read()
    rows = list(csv.reader(io.StringIO(text)))
    if not rows: continue
    keep = [rows[0]] + [r for r in rows[1:] if not any(PAT.search(c) for c in r)]
    if len(keep) != len(rows):
        with open(p, 'w', newline='', encoding='utf-8') as f: csv.writer(f, lineterminator='\n').writerows(keep)
    print(p.split('/')[-1], len(rows) - 1, '->', len(keep) - 1)
