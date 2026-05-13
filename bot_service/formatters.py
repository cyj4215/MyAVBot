def format_actress_card(actress: dict) -> str:
    lines = [f"👩 *{actress['name']}*"]
    if actress.get("birthday"):
        lines.append(f"📅 生日: {actress['birthday']}")
    if actress.get("country"):
        lines.append(f"🌍 国籍: {actress['country']}")
    if actress.get("height"):
        lines.append(f"📏 身高: {actress['height']}cm")
    if actress.get("measurements"):
        lines.append(f"📐 三围: {actress['measurements']}")
    if actress.get("career_start"):
        lines.append(f"🎬 出道: {actress['career_start']}")
    if actress.get("status"):
        status_emoji = "🟢" if actress["status"] == "active" else "🔴"
        lines.append(f"{status_emoji} 状态: {'活跃' if actress['status'] == 'active' else '退役'}")
    return "\n".join(lines)


def format_work_card(work: dict) -> str:
    lines = [f"🎥 *{work['title']}*"]
    if work.get("work_id"):
        lines.append(f"🏷 编号: {work['work_id']}")
    if work.get("release_date"):
        lines.append(f"📅 发行: {work['release_date']}")
    if work.get("duration"):
        lines.append(f"⏱ 时长: {work['duration']}min")
    if work.get("rating"):
        stars = "⭐" * int(float(work["rating"]))
        lines.append(f"评分: {stars} ({work['rating']})")
    return "\n".join(lines)


def format_magnet_result(magnet: dict) -> str:
    size_str = format_size(magnet.get("file_size", 0))
    return (
        f"🔗 `{magnet['info_hash']}`\n"
        f"📄 {magnet['title'][:80]}\n"
        f"📦 {size_str} | ⬆ {magnet.get('seeders', 0)} | ⬇ {magnet.get('leechers', 0)}\n"
        f"🏷 {magnet.get('source_site', 'unknown')}"
    )


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}PB"
