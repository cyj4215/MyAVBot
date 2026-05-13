from __future__ import annotations


def format_actress_card(actress: dict) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━",
        f"  🎬 *{actress['name']}*",
        "━━━━━━━━━━━━━━━━━━━",
    ]
    had_data = False
    if actress.get("aliases"):
        aliases = actress["aliases"].strip("[]").replace('"', "")
        if aliases:
            lines.append(f"  🏷 别　　名: `{aliases[:60]}`")
            had_data = True
    if actress.get("birthday"):
        lines.append(f"  📅 生　　日: {actress['birthday']}")
        had_data = True
    if actress.get("country") or actress.get("birthplace"):
        loc = actress.get("country") or ""
        bp = actress.get("birthplace") or ""
        loc_text = f"{bp}, {loc}" if bp and loc else (bp or loc)
        lines.append(f"  🌍 国　　籍: {loc_text}")
        had_data = True
    if actress.get("height"):
        lines.append(f"  📏 身　　高: {actress['height']} cm")
        had_data = True
    if actress.get("measurements"):
        lines.append(f"  📐 三　　围: {actress['measurements']}")
        had_data = True
    if actress.get("bust"):
        lines.append(f"  🍒 罩　　杯: {actress['bust']}")
        had_data = True
        had_data = True
    if actress.get("career_start"):
        years_active = f"{actress['career_start']} — 至今"
        lines.append(f"  🎬 出道年份: {years_active}")
        had_data = True
    if actress.get("status"):
        if actress["status"] == "active":
            lines.append(f"  🟢 状　　态: `活跃中`")
        else:
            lines.append(f"  🔴 状　　态: `已退役`")
        had_data = True
    if had_data:
        lines.append("  ───────────────────")
    return "\n".join(lines)


def format_work_card(work: dict) -> str:
    lines = [f"🎬 *{work['title']}*"]
    if work.get("work_id"):
        lines.append(f"  🏷 {work['work_id']}")
    year_display = _format_year(work.get("release_date"))
    if year_display:
        tag = " 🔥《最新》" if year_display == "2026" else ""
        lines.append(f"  📅 {year_display}{tag}")
    if work.get("duration"):
        lines.append(f"  ⏱ {work['duration']}min")
    if work.get("rating"):
        rating = float(work["rating"])
        lines.append(f"  {'⭐' * int(rating)} {rating}")
    return "\n".join(lines)


def format_magnet_result(magnet: dict) -> str:
    size_str = format_size(magnet.get("file_size", 0))
    se = magnet.get("seeders", 0)
    le = magnet.get("leechers", 0)
    src = magnet.get("source_site", "?")
    hot = " 🔥" if se > 5 else ""
    return (
        f"📦 *{magnet['title'][:60]}*{hot}\n"
        f"  🔗 `{magnet['info_hash'][:20]}…`\n"
        f"  📊 {size_str}  ⬆{se}  ⬇{le}  🏷 {src}"
    )


def format_works_header(name: str, total: int, page: int, total_pages: int) -> str:
    line = f"🎬 *{name}* の 作品目录"
    line += f"\n📊 共 {total} 部 | 第 {page}/{total_pages} 页"
    line += f"\n`{'─'*20}`"
    return line


def format_magnet_header(keyword: str, total: int, page: int, total_pages: int) -> str:
    cat = "adult_eu"
    line = f"🔍 *“{keyword}”* 磁力搜索结果"
    line += f"\n📊 共 {total} 条 | 第 {page}/{total_pages} 页"
    line += f"\n`{'─'*20}`"
    return line


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}PB"


def _format_year(date_str: str | None) -> str:
    if not date_str:
        return ""
    return date_str[:4]
