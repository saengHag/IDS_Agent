import re

def parse_snort_log(line: str) -> dict:
    """Snort alert_full 로그 한 줄을 파싱"""
    try:
        alert = re.search(r'\[\*\*\] \[(.*?)\] (.*?) \[\*\*\]', line)
        priority = re.search(r'\[Priority: (\d+)\]', line)
        ip_info = re.search(r'\{(.*?)\}\s([\d\.]+):?(\d+)?\s->\s([\d\.]+):?(\d+)?', line)
        ttl = re.search(r'TTL:(\d+)', line)
        tos = re.search(r'TOS:0x([0-9A-Fa-f]+)', line)
        id_ = re.search(r'ID:(\d+)', line)
        seq = re.search(r'Seq:\s*0x([0-9A-Fa-f]+)', line)
        ack = re.search(r'Ack:\s*0x([0-9A-Fa-f]+)', line)

        return {
            "sid_gid_rev": alert.group(1) if alert else "",
            "message": alert.group(2) if alert else "",
            "priority": int(priority.group(1)) if priority else None,
            "protocol": ip_info.group(1) if ip_info else "",
            "src_ip": ip_info.group(2) if ip_info else "",
            "src_port": ip_info.group(3) if ip_info and ip_info.group(3) else "",
            "dst_ip": ip_info.group(4) if ip_info else "",
            "dst_port": ip_info.group(5) if ip_info and ip_info.group(5) else "",
            "ttl": int(ttl.group(1)) if ttl else None,
            "tos": tos.group(1) if tos else None,
            "id": id_.group(1) if id_ else None,
            "seq": seq.group(1) if seq else None,
            "ack": ack.group(1) if ack else None
        }
    except Exception as e:
        return {"error": str(e), "raw": line}
