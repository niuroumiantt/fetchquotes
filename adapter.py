"""Lambda 1x H100 SXM native JSON island table; no browser/model needed."""
import json
import re
from helpers import html, candidate, date


def extract(data, source, original, sampled_at):
    text = data.decode('utf-8')
    found = []
    for match in re.finditer(r'var newIslands\s*=\s*', text):
        islands, _ = json.JSONDecoder().raw_decode(text[match.end():])
        for island in islands:
            for tab in island.get('props', {}).get('tabs', []):
                if tab.get('label') != '1x':
                    continue
                p = html(tab['contentHtml'].encode())
                if 'PRICE/GPU/HR*' not in p.text or 'plus applicable sales tax/VAT/GST' not in p.text:
                    raise ValueError('pricing conditions/header changed')
                for row in p.rows:
                    if len(row) == 6 and row[0] == 'NVIDIA H100 SXM':
                        if not re.fullmatch(r'\$\d+\.\d{2}', row[5]):
                            raise ValueError('price format changed')
                        result = candidate('product', 'Lambda 1x NVIDIA H100 SXM instance',
                            {'provider': 'Lambda', 'model': row[0], 'gpu_count': 1, 'vram': row[1], 'vcpus': row[2],
                             'ram': row[3], 'storage': row[4], 'market': None, 'currency': None},
                            'quote.price', float(row[5][1:]), '$/GPU-hour',
                            'Public list offer; 1 GPU instance; ' + ' | '.join(row[:5]) +
                            '; regional availability unspecified; currency symbol $ only (currency code not confirmed); plus sales tax/VAT/GST; no inventory or transaction guarantee',
                            'offer', 'script var newIslands native JSON / props/tabs[label=1x]/contentHtml; NVIDIA H100 SXM row',
                            row[5], p.text,
                            date(sampled_at, 'datetime', 'public offer observed at acquisition/reuse; not publisher effective date'))
                        found.append(result)
    if len(found) != 1:
        raise ValueError('1x H100 quote missing or ambiguous')
    return found
