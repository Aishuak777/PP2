import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def norm_amount(s: str) -> float:
    s = s.strip().replace(" ", "").replace("\u00A0", "").replace(",", ".")
    return float(s)


def find_datetime(text: str) -> Optional[str]:
    m = re.search(r"(?im)^\s*Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})\s*$", text)
    return m.group(1) if m else None


def find_total(text: str) -> Optional[float]:
    m = re.search(r"(?is)\bИТОГО:\s*[\r\n]+?\s*([0-9][0-9 \u00A0]*,\d{2})", text)
    return norm_amount(m.group(1)) if m else None


def find_payment_method(text: str) -> Optional[str]:
    if re.search(r"(?im)^\s*Банковская\s+карта\s*:", text):
        return "card"
    if re.search(r"(?im)^\s*Наличные\s*:", text):
        return "cash"
    if re.search(r"(?im)^\s*(Kaspi|Каспи)\s*:", text):
        return "kaspi"
    return None


def extract_all_prices(text: str) -> List[float]:
    matches = re.findall(r"([0-9][0-9 \u00A0]*,\d{2})", text)
    return [norm_amount(x) for x in matches]


def parse_items(text: str) -> List[Dict[str, Any]]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    item_start_re = re.compile(r"^\s*(\d+)\.\s*$")
    qty_price_re = re.compile(r"^\s*([0-9]+,[0-9]{3})\s*x\s*([0-9][0-9 \u00A0]*,\d{2})\s*$")
    amount_re = re.compile(r"^\s*([0-9][0-9 \u00A0]*,\d{2})\s*$")

    items: List[Dict[str, Any]] = []
    i = 0
    n = len(lines)

    while i < n:
        m_start = item_start_re.match(lines[i])
        if not m_start:
            i += 1
            continue

        item_no = int(m_start.group(1))
        i += 1

        name_parts: List[str] = []
        while i < n and not qty_price_re.match(lines[i]) and not item_start_re.match(lines[i]):
            if re.match(r"(?i)^\s*(Банковская\s+карта|ИТОГО|ФИСКАЛЬНЫЙ|Время)\b", lines[i]):
                break
            if lines[i].strip():
                name_parts.append(lines[i].strip())
            i += 1

        name = " ".join(name_parts).strip()
        qty = None
        unit_price = None
        line_total = None

        if i < n:
            m_qp = qty_price_re.match(lines[i])
            if m_qp:
                qty = float(m_qp.group(1).replace(",", "."))
                unit_price = norm_amount(m_qp.group(2))
                i += 1

        if i < n and amount_re.match(lines[i]):
            line_total = norm_amount(amount_re.match(lines[i]).group(1))
            i += 1

        if i < n and re.match(r"(?im)^\s*Стоимость\s*$", lines[i]):
            i += 1
            if i < n and amount_re.match(lines[i]):
                i += 1

        if name and (unit_price is not None or line_total is not None):
            items.append(
                {"no": item_no, "name": name, "qty": qty, "unit_price": unit_price, "line_total": line_total}
            )

    return items


def main() -> None:
    path = Path("raw.txt")
    if not path.exists():
        raise FileNotFoundError("raw.txt not found")

    text = path.read_text(encoding="utf-8", errors="replace")

    items = parse_items(text)
    all_prices = extract_all_prices(text)
    total = find_total(text)
    dt = find_datetime(text)
    pay = find_payment_method(text)

    if total is None:
        calc = sum(it["line_total"] for it in items if isinstance(it.get("line_total"), (int, float)))
        total = round(calc, 2) if calc else None

    result = {
        "datetime": dt,
        "payment_method": pay,
        "total": total,
        "items": items,
        "all_prices": all_prices,
        "item_names": [it["name"] for it in items],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
