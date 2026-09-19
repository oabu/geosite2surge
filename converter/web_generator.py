"""Web catalog generator for Surge rulesets.

Generates a modern, interactive, single-page web catalog (index.html)
for browsing, searching, and favoriting all GeoSite and GeoIP rulesets.
"""

import json
import os
import re
from typing import Any, Dict, List

# Common ISO 3166-1 alpha-2 country code to Chinese names
COUNTRY_NAMES = {
    "ad": "安道尔", "ae": "阿联酋", "af": "阿富汗", "ag": "安提瓜和巴布达", "ai": "安圭拉",
    "al": "阿尔巴尼亚", "am": "亚美尼亚", "ao": "安哥拉", "ar": "阿根廷", "at": "奥地利",
    "au": "澳大利亚", "az": "阿塞拜疆", "ba": "波黑", "bb": "巴巴多斯", "bd": "孟加拉国",
    "be": "比利时", "bf": "布基纳法索", "bg": "保加利亚", "bh": "巴林", "bi": "布隆迪",
    "bj": "贝宁", "bm": "百慕大", "bn": "文莱", "bo": "玻利维亚", "br": "巴西",
    "bs": "巴哈马", "bt": "不丹", "bw": "博茨瓦纳", "by": "白俄罗斯", "bz": "伯利兹",
    "ca": "加拿大", "cd": "刚果(金)", "cf": "中非", "cg": "刚果(布)", "ch": "瑞士",
    "ci": "科特迪瓦", "cl": "智利", "cm": "喀麦隆", "cn": "中国大陆", "co": "哥伦比亚",
    "cr": "哥斯达黎加", "cu": "古巴", "cv": "佛得角", "cy": "塞浦路斯", "cz": "捷克",
    "de": "德国", "dj": "吉布提", "dk": "丹麦", "dm": "多米尼克", "do": "多米尼加",
    "dz": "阿尔及利亚", "ec": "厄瓜多尔", "ee": "爱沙尼亚", "eg": "埃及", "es": "西班牙",
    "et": "埃塞俄比亚", "fi": "芬兰", "fj": "斐济", "fr": "法国", "ga": "加蓬",
    "gb": "英国", "gd": "格林纳达", "ge": "格鲁吉亚", "gh": "加纳", "gm": "冈比亚",
    "gn": "几内亚", "gr": "希腊", "gt": "危地马拉", "gy": "圭亚那", "hk": "中国香港",
    "hn": "洪都拉斯", "hr": "克罗地亚", "hu": "匈牙利", "id": "印度尼西亚", "ie": "爱尔兰",
    "il": "以色列", "in": "印度", "iq": "伊拉克", "ir": "伊朗", "is": "冰岛",
    "it": "意大利", "jm": "牙买加", "jo": "约旦", "jp": "日本", "ke": "肯尼亚",
    "kg": "吉尔吉斯斯坦", "kh": "柬埔寨", "kp": "朝鲜", "kr": "韩国", "kw": "科威特",
    "kz": "哈萨克斯坦", "la": "老挝", "lb": "黎巴嫩", "li": "列支敦士登", "lk": "斯里兰卡",
    "lr": "利比里亚", "ls": "莱索托", "lt": "立陶宛", "lu": "卢森堡", "lv": "拉脱维亚",
    "ly": "利比亚", "ma": "摩洛哥", "mc": "摩纳哥", "md": "摩尔多瓦", "me": "黑山",
    "mg": "马达加斯加", "mk": "北马其顿", "ml": "马里", "mm": "缅甸", "mn": "蒙古",
    "mo": "中国澳门", "mt": "马耳他", "mu": "毛里求斯", "mv": "马尔代夫", "mw": "马拉维",
    "mx": "墨西哥", "my": "马来西亚", "mz": "莫桑比克", "na": "纳米比亚", "ne": "尼日尔",
    "ng": "尼日利亚", "ni": "尼加拉瓜", "nl": "荷兰", "no": "挪威", "np": "尼泊尔",
    "nz": "新西兰", "om": "阿曼", "pa": "巴拿马", "pe": "秘鲁", "pg": "巴布亚新几内亚",
    "ph": "菲律宾", "pk": "巴基斯坦", "pl": "波兰", "pr": "波多黎各", "pt": "葡萄牙",
    "py": "巴拉圭", "qa": "卡塔尔", "ro": "罗马尼亚", "rs": "塞尔维亚", "ru": "俄罗斯",
    "rw": "卢旺达", "sa": "沙特阿拉伯", "sc": "塞舌尔", "sd": "苏丹", "se": "瑞典",
    "sg": "新加坡", "si": "斯洛文尼亚", "sk": "斯洛伐克", "sn": "塞内加尔", "so": "索马里",
    "sy": "叙利亚", "th": "泰国", "tj": "塔吉克斯坦", "tm": "土库曼斯坦", "tn": "突尼斯",
    "tr": "土耳其", "tw": "中国台湾", "tz": "坦桑尼亚", "ua": "乌克兰", "ug": "乌干达",
    "us": "美国", "uy": "乌拉圭", "uz": "乌兹别克斯坦", "va": "梵蒂冈", "ve": "委内瑞拉",
    "vn": "越南", "ye": "也门", "za": "南非", "zm": "赞比亚", "zw": "津巴布韦",
}

# Curated descriptions for popular categories
CURATED_DESCRIPTIONS = {
    # Special & Common GeoSite
    "cn": "中国大陆主流域名（直连推荐）",
    "geolocation-!cn": "非中国大陆域名（代理推荐）",
    "gfw": "GFWList 审查屏蔽域名列表",
    "greatfire": "GreatFire 镜像域名列表",
    "tld-cn": "中国大陆顶级域名（.cn 等）",
    "tld-!cn": "非中国大陆顶级域名",
    "category-ads-all": "全网广告、弹窗与隐私追踪全能拦截规则",
    "category-ads": "常见广告联盟与推广追踪域名",
    "category-media": "常见流媒体影音播放域名",
    "category-games": "国际游戏平台与多人在线联机域名",
    "category-scholar-!cn": "国外学术论文、高校科研与期刊网站",
    "category-scholar-cn": "国内知网、万方等学术科研网站",
    "category-communication": "即时通讯、聊天与社交网络域名",
    "category-finance": "国际金融、银行、证券与理财网站",

    # Popular Brand Services
    "apple": "Apple 苹果全生态服务与网站",
    "apple-cn": "Apple 中国大陆本土化直连服务",
    "icloud": "Apple iCloud 云盘与数据同步服务",
    "google": "Google 谷歌全家桶服务与基础设施",
    "google-cn": "Google 中国大陆直连域名（地图、翻译等）",
    "youtube": "YouTube 视频流媒体与频道服务",
    "github": "GitHub 开源平台与开发者生态",
    "gitlab": "GitLab 代码托管服务",
    "telegram": "Telegram 电报官方服务与域名",
    "twitter": "X / Twitter 社交媒体网络",
    "facebook": "Meta / Facebook 社交网络服务",
    "instagram": "Instagram 图片与短视频社交平台",
    "whatsapp": "WhatsApp 即时通讯与语音视频",
    "netflix": "Netflix 奈飞高清流媒体视频",
    "disney": "Disney+ 迪士尼流媒体娱乐平台",
    "spotify": "Spotify 国际正版音乐流媒体",
    "steam": "Steam 游戏商店与社区网络",
    "epicgames": "Epic Games 游戏商城与客户端",
    "playstation": "Sony PlayStation 游戏主机网络",
    "xbox": "微软 Xbox 主机服务与 Xbox Live",
    "nintendo": "任天堂 Switch 网络与 eShop 商店",
    "amazon": "Amazon 亚马逊电商与云计算服务",
    "aws": "Amazon AWS 国际云计算平台",
    "cloudflare": "Cloudflare CDN、DNS 与安全网络",
    "microsoft": "微软官方网站与 Windows 服务",
    "windows": "Windows 操作系统联网组件",
    "onedrive": "微软 OneDrive 云盘存储与同步",
    "office": "微软 Office 365 办公协作套件",
    "openai": "OpenAI 与 ChatGPT 官方服务",
    "anthropic": "Claude / Anthropic AI 官方域名",
    "bing": "微软必应 Bing 搜索引擎",
    "bilibili": "哔哩哔哩（B站）视频与直播服务",
    "zhihu": "知乎问答与知识分享社区",
    "baidu": "百度搜索、网盘与旗下互联网产品",
    "tencent": "腾讯全家桶、QQ、微信与游戏网络",
    "alibaba": "阿里巴巴集团、淘宝、天猫与云计算",
    "bytedance": "字节跳动旗下抖音、今日头条等服务",
    "tiktok": "TikTok 国际版短视频平台",
    "jd": "京东商城与物流供应链系统",
    "netlease": "网易全家桶、网易云音乐与网易游戏",
    "speedtest": "Ookla Speedtest 网络测速平台",
    "fast": "Netflix Fast.com 宽带测速节点",
    "docker": "Docker 容器镜像与官方服务",

    # Windows Spy & Update
    "win-spy": "Windows 操作系统遥测与隐私数据收集",
    "win-update": "Windows 操作系统更新与补丁下载",
    "win-extra": "Windows 附加遥测与广告推广域名",

    # GeoIP specific
    "geoip:cn": "中国大陆 IP 地址段（IPv4/IPv6 直连推荐）",
    "geoip:telegram": "Telegram 官方数据中心通讯 IP 段",
    "geoip:cloudflare": "Cloudflare Anycast 全球 CDN 节点 IP",
    "geoip:cloudfront": "Amazon CloudFront 全球 CDN 节点 IP",
    "geoip:facebook": "Meta / Facebook 官方网络 IP 段",
    "geoip:fastly": "Fastly 全球 CDN 节点 IP",
    "geoip:google": "Google 谷歌全球骨干网与服务 IP 段",
    "geoip:netflix": "Netflix 奈飞自建 CDN 与流媒体服务 IP 段",
    "geoip:twitter": "X / Twitter 官方服务器 IP 段",
    "geoip:tor": "Tor 洋葱路由网络出口节点 IP",
    "geoip:private": "局域网私有保留 IP 地址段 (RFC 1918)",
}

POPULAR_SET = {
    "cn", "geolocation-!cn", "gfw", "category-ads-all", "apple", "google",
    "youtube", "github", "telegram", "twitter", "facebook", "netflix",
    "spotify", "bilibili", "steam", "openai", "microsoft", "cloudflare"
}


def infer_description(key: str, item_type: str) -> str:
    """Infer a concise, friendly Chinese description for a ruleset."""
    lookup_key = f"{item_type}:{key}" if item_type == "geoip" else key
    if lookup_key in CURATED_DESCRIPTIONS:
        return CURATED_DESCRIPTIONS[lookup_key]
    if key in CURATED_DESCRIPTIONS:
        return CURATED_DESCRIPTIONS[key]

    # Country code check
    if key in COUNTRY_NAMES:
        cname = COUNTRY_NAMES[key]
        if item_type == "geoip":
            return f"{cname} IP 地址段"
        return f"{cname} 地区相关域名与服务"

    # Category prefixes
    if key.startswith("category-"):
        sub = key.replace("category-", "")
        return f"{sub.capitalize()} 类别相关域名集合"

    if key.startswith("tld-"):
        sub = key.replace("tld-", "")
        return f".{sub} 顶级域名集合"

    if item_type == "geoip":
        return f"{key.capitalize()} 专用 IP 地址段"

    return f"{key.capitalize()} 旗下相关域名与服务"


def count_rules_in_file(path: str) -> int:
    """Count non-comment rule lines in a file."""
    if not os.path.exists(path):
        return 0
    count = 0
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    count += 1
    except Exception:
        pass
    return count


def collect_rules_metadata(dist_dir: str) -> List[Dict[str, Any]]:
    """Scan dist_dir and build metadata for all rules."""
    items = []

    # 1. GeoSite
    geosite_dir = os.path.join(dist_dir, "geosite")
    if os.path.exists(geosite_dir):
        for fname in sorted(os.listdir(geosite_dir)):
            if fname.endswith(".list"):
                name = fname[:-5]
                fpath = os.path.join(geosite_dir, fname)
                count = count_rules_in_file(fpath)
                desc = infer_description(name, "geosite")
                is_popular = name in POPULAR_SET
                items.append({
                    "id": f"geosite:{name}",
                    "type": "geosite",
                    "name": name,
                    "file": f"geosite/{fname}",
                    "rules": count,
                    "desc": desc,
                    "popular": is_popular,
                })

    # 2. GeoIP
    geoip_dir = os.path.join(dist_dir, "geoip")
    if os.path.exists(geoip_dir):
        for fname in sorted(os.listdir(geoip_dir)):
            if fname.endswith(".list"):
                name = fname[:-5]
                fpath = os.path.join(geoip_dir, fname)
                count = count_rules_in_file(fpath)
                desc = infer_description(name, "geoip")
                is_popular = name in ("cn", "telegram", "cloudflare", "private", "us", "hk")
                items.append({
                    "id": f"geoip:{name}",
                    "type": "geoip",
                    "name": name,
                    "file": f"geoip/{fname}",
                    "rules": count,
                    "desc": desc,
                    "popular": is_popular,
                })

    return items


def generate_html_catalog(dist_dir: str, output_html_path: str) -> str:
    """Generate the complete self-contained index.html catalog."""
    items = collect_rules_metadata(dist_dir)
    items_json = json.dumps(items, ensure_ascii=False, separators=(',', ':'))

    total_geosite = sum(1 for x in items if x["type"] == "geosite")
    total_geoip = sum(1 for x in items if x["type"] == "geoip")
    total_rules = sum(x["rules"] for x in items)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Surge 规则集导航与订阅中心</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
  <style>
    :root {{
      --bg-main: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-hover: #f1f5f9;
      --text-main: #0f172a;
      --text-sub: #64748b;
      --border-color: #e2e8f0;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --accent: #f59e0b;
      --accent-star: #eab308;
      --tag-geosite: #8b5cf6;
      --tag-geoip: #06b6d4;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.08);
      --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg-main: #0b1120;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        --text-main: #f8fafc;
        --text-sub: #94a3b8;
        --border-color: #334155;
        --primary: #3b82f6;
        --primary-hover: #60a5fa;
        --primary-light: #1e3a8a40;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
      }}
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-main);
      min-height: 100vh;
      padding-bottom: 60px;
    }}

    header {{
      background-color: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(8px);
      box-shadow: var(--shadow-sm);
    }}

    .header-container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 16px 20px;
    }}

    .title-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .title-group {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .logo-icon {{
      font-size: 28px;
    }}

    h1 {{
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}

    .stats-badge {{
      font-size: 13px;
      color: var(--text-sub);
      background: var(--bg-main);
      border: 1px solid var(--border-color);
      padding: 4px 10px;
      border-radius: 20px;
    }}

    .base-url-card {{
      background-color: var(--primary-light);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      margin-bottom: 14px;
    }}

    .base-url-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--primary);
    }}

    .presets-row {{
      display: flex;
      gap: 6px;
      font-size: 12px;
    }}

    .preset-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      border-radius: var(--radius-sm);
      padding: 2px 8px;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .preset-btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
    }}

    .base-url-input-group {{
      display: flex;
      gap: 8px;
    }}

    .base-url-input {{
      flex: 1;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
      padding: 8px 12px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background-color: var(--bg-card);
      color: var(--text-main);
      outline: none;
      transition: border-color 0.2s;
    }}

    .base-url-input:focus {{
      border-color: var(--primary);
    }}

    .reset-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-sub);
      padding: 0 12px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 12px;
    }}

    .controls-row {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
    }}

    .tabs-group {{
      display: flex;
      gap: 6px;
      background-color: var(--bg-main);
      padding: 4px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
    }}

    .tab-btn {{
      background: transparent;
      border: none;
      padding: 6px 14px;
      border-radius: var(--radius-sm);
      color: var(--text-sub);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .tab-btn.active {{
      background-color: var(--bg-card);
      color: var(--primary);
      box-shadow: var(--shadow-sm);
    }}

    .tab-count {{
      font-size: 11px;
      background: var(--border-color);
      padding: 2px 6px;
      border-radius: 10px;
    }}

    .search-sort-group {{
      display: flex;
      gap: 8px;
      flex: 1;
      max-width: 500px;
    }}

    .search-input-wrapper {{
      position: relative;
      flex: 1;
    }}

    .search-input {{
      width: 100%;
      padding: 8px 12px 8px 34px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background-color: var(--bg-card);
      color: var(--text-main);
      font-size: 13px;
      outline: none;
    }}

    .search-input:focus {{
      border-color: var(--primary);
    }}

    .search-icon {{
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 14px;
      color: var(--text-sub);
    }}

    .sort-select {{
      padding: 0 10px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background-color: var(--bg-card);
      color: var(--text-main);
      font-size: 13px;
      outline: none;
      cursor: pointer;
    }}

    main {{
      max-width: 1200px;
      margin: 20px auto 0;
      padding: 0 20px;
    }}

    .rules-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .rule-row {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 10px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      transition: all 0.15s ease;
      box-shadow: var(--shadow-sm);
    }}

    .rule-row:hover {{
      background-color: var(--bg-card-hover);
      border-color: var(--primary);
      box-shadow: var(--shadow-md);
    }}

    .row-left {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      min-width: 0;
    }}

    .row-info {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
      flex: 1;
    }}

    .row-top-line {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .row-title {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text-main);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}

    .row-desc {{
      font-size: 13px;
      color: var(--text-sub);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 480px;
    }}

    .row-bottom-line {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .row-url {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      color: var(--primary);
      text-decoration: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 650px;
      background: var(--bg-main);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      user-select: all;
    }}

    .badge {{
      font-size: 11px;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      flex-shrink: 0;
    }}

    .badge-geosite {{
      background-color: rgba(139, 92, 246, 0.15);
      color: #8b5cf6;
    }}

    .badge-geoip {{
      background-color: rgba(6, 182, 212, 0.15);
      color: #06b6d4;
    }}

    .badge-rules {{
      background-color: var(--border-color);
      color: var(--text-sub);
      flex-shrink: 0;
    }}

    .star-btn {{
      background: none;
      border: none;
      cursor: pointer;
      font-size: 18px;
      color: #cbd5e1;
      transition: color 0.15s, transform 0.1s;
      flex-shrink: 0;
      padding: 2px;
    }}

    .star-btn:hover {{
      transform: scale(1.15);
    }}

    .star-btn.active {{
      color: var(--accent-star);
    }}

    .row-actions {{
      display: flex;
      gap: 8px;
      flex-shrink: 0;
      align-items: center;
    }}

    @media (max-width: 960px) {{
      .rule-row {{
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
      }}
      .row-left {{
        width: 100%;
      }}
      .row-actions {{
        width: 100%;
      }}
      .row-desc {{
        max-width: 100%;
        white-space: normal;
      }}
      .row-url {{
        max-width: 100%;
      }}
    }}

    .action-btn {{
      flex: 1;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 600;
      border-radius: var(--radius-sm);
      cursor: pointer;
      border: 1px solid var(--border-color);
      background-color: var(--bg-card);
      color: var(--text-main);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      transition: all 0.15s;
    }}

    .action-btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
      background-color: var(--primary-light);
    }}

    .action-btn-primary {{
      background-color: var(--primary);
      border-color: var(--primary);
      color: #ffffff;
    }}

    .action-btn-primary:hover {{
      background-color: var(--primary-hover);
      color: #ffffff;
    }}

    .pagination {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
      margin-top: 30px;
    }}

    .page-btn {{
      padding: 6px 14px;
      font-size: 13px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background-color: var(--bg-card);
      color: var(--text-main);
      cursor: pointer;
    }}

    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .page-info {{
      font-size: 13px;
      color: var(--text-sub);
    }}

    .empty-state {{
      text-align: center;
      padding: 60px 20px;
      color: var(--text-sub);
      grid-column: 1 / -1;
    }}

    .empty-icon {{
      font-size: 40px;
      margin-bottom: 10px;
    }}

    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(15, 23, 42, 0.9);
      color: #fff;
      padding: 10px 18px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 500;
      box-shadow: var(--shadow-lg);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 1000;
      pointer-events: none;
    }}

    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}

    .github-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 5px 12px;
      border-radius: 20px;
      text-decoration: none;
      transition: all 0.15s ease;
    }}

    .github-btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
      background: var(--primary-light);
    }}

    footer {{
      margin-top: 50px;
      padding: 30px 20px;
      border-top: 1px solid var(--border-color);
      background: var(--bg-card);
      text-align: center;
      font-size: 13px;
      color: var(--text-sub);
    }}

    footer a {{
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
    }}

    footer a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-container">
      <div class="title-row">
        <div class="title-group">
          <span class="logo-icon">⚡</span>
          <div>
            <h1>Surge 规则集导航中心</h1>
            <div style="font-size: 12px; color: var(--text-sub); margin-top: 2px;">
              由 <a href="https://github.com/oabu" target="_blank" style="color: var(--primary); text-decoration: none; font-weight: 600;">@oabu</a> 维护构建
            </div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
          <div class="stats-badge">
            GeoSite: <strong>{total_geosite}</strong> | GeoIP: <strong>{total_geoip}</strong> | 规则总量: <strong>{total_rules:,}</strong>
          </div>
          <a href="https://github.com/oabu/geosite2surge" target="_blank" class="github-btn" title="查看 GitHub 开源仓库">
            <svg height="15" width="15" viewBox="0 0 16 16" fill="currentColor" style="vertical-align: text-bottom;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
            GitHub
          </a>
        </div>
      </div>

      <!-- Base URL Configuration -->
      <div class="base-url-card">
        <div class="base-url-header">
          <span>🌐 订阅基准 URL (默认读取当前浏览器访问地址)</span>
          <div class="presets-row">
            <button class="preset-btn" onclick="applyPreset('current')">当前访问地址</button>
            <button class="preset-btn" onclick="applyPreset('pages')">GitHub Pages</button>
            <button class="preset-btn" onclick="applyPreset('jsdelivr')">jsDelivr CDN</button>
            <button class="preset-btn" onclick="applyPreset('raw')">GitHub Raw</button>
          </div>
        </div>
        <div class="base-url-input-group">
          <input type="text" id="baseUrlInput" class="base-url-input" placeholder="默认自动读取当前访问地址，亦可输入自定义云端域名...">
          <button class="reset-btn" onclick="resetBaseUrl()">恢复当前地址</button>
        </div>
      </div>

      <!-- Controls Row: Tabs, Search, Sort -->
      <div class="controls-row">
        <div class="tabs-group">
          <button class="tab-btn active" data-tab="geosite" onclick="setTab('geosite')">GeoSite <span class="tab-count" id="countGeosite">0</span></button>
          <button class="tab-btn" data-tab="geoip" onclick="setTab('geoip')">GeoIP <span class="tab-count" id="countGeoip">0</span></button>
          <button class="tab-btn" data-tab="all" onclick="setTab('all')">全部 <span class="tab-count" id="countAll">0</span></button>
          <button class="tab-btn" data-tab="favorites" onclick="setTab('favorites')">⭐ 收藏 <span class="tab-count" id="countFav">0</span></button>
        </div>

        <div class="search-sort-group">
          <div class="search-input-wrapper">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-input" placeholder="搜索规则名称、描述或关键词..." oninput="onSearchChange()">
          </div>
          <select id="sortSelect" class="sort-select" onchange="onSortChange()">
            <option value="popular">推荐排序</option>
            <option value="name_asc">名称 (A-Z)</option>
            <option value="name_desc">名称 (Z-A)</option>
            <option value="rules_desc">规则数量 (多到少)</option>
            <option value="rules_asc">规则数量 (少到多)</option>
          </select>
        </div>
      </div>
    </div>
  </header>

  <main>
    <div id="rulesList" class="rules-list"></div>
    <div class="pagination" id="pagination">
      <button class="page-btn" id="prevPageBtn" onclick="changePage(-1)">上一页</button>
      <span class="page-info" id="pageInfo">第 1 / 1 页</span>
      <button class="page-btn" id="nextPageBtn" onclick="changePage(1)">下一页</button>
    </div>
  </main>

  <footer>
    <p>
      Surge 规则集导航中心 · 规则源自 <a href="https://github.com/Loyalsoldier/v2ray-rules-dat" target="_blank" rel="noopener noreferrer">Loyalsoldier/v2ray-rules-dat</a>
    </p>
    <p style="margin-top: 6px;">
      维护者: <a href="https://github.com/oabu" target="_blank" rel="noopener noreferrer">@oabu</a> ·
      开源仓库: <a href="https://github.com/oabu/geosite2surge" target="_blank" rel="noopener noreferrer">oabu/geosite2surge</a> ·
      每日 GitHub Actions 自动更新部署
    </p>
  </footer>

  <div id="toast" class="toast">已成功复制到剪贴板</div>

  <script>
    // Embedded metadata directly generated from build
    const RAW_RULES = {items_json};

    const PAGE_SIZE = 80;
    let currentTab = 'geosite';
    let currentQuery = '';
    let currentSort = 'popular';
    let currentPage = 1;
    let favorites = new Set();

    // 1. Initialize Favorites
    try {{
      const stored = localStorage.getItem('surge_rules_favorites');
      if (stored) {{
        favorites = new Set(JSON.parse(stored));
      }}
    }} catch (e) {{}}

    // 2. Base URL Management: Always read current browser URL by default
    function computeDefaultBaseUrl() {{
      try {{
        // Extract current location path without query params or hash
        let raw = window.location.href.split('?')[0].split('#')[0];
        // Strip off index.html / index.htm or filename if present
        if (raw.endsWith('.html') || raw.endsWith('.htm')) {{
          const lastSlash = raw.lastIndexOf('/');
          if (lastSlash !== -1) {{
            raw = raw.substring(0, lastSlash + 1);
          }}
        }}
        if (!raw.endsWith('/')) {{
          raw += '/';
        }}
        return raw;
      }} catch (e) {{
        return window.location.origin ? (window.location.origin + '/') : './';
      }}
    }}

    const baseUrlInput = document.getElementById('baseUrlInput');
    let savedBaseUrl = localStorage.getItem('surge_rules_base_url');
    // If no saved URL or if it contains placeholder / old github raw URL, default to current browser URL
    if (!savedBaseUrl || savedBaseUrl.includes('<username>') || savedBaseUrl.includes('raw.githubusercontent.com')) {{
      savedBaseUrl = computeDefaultBaseUrl();
    }}
    baseUrlInput.value = savedBaseUrl;

    baseUrlInput.addEventListener('input', () => {{
      let val = baseUrlInput.value.trim();
      if (val && !val.endsWith('/')) {{
        val += '/';
      }}
      localStorage.setItem('surge_rules_base_url', val);
      renderGrid();
    }});

    function getBaseUrl() {{
      let val = baseUrlInput.value.trim();
      if (val && !val.endsWith('/')) {{
        val += '/';
      }}
      return val || './';
    }}

    function applyPreset(type) {{
      if (type === 'current') {{
        baseUrlInput.value = computeDefaultBaseUrl();
        showToast('已恢复为当前访问地址');
      }} else if (type === 'pages') {{
        baseUrlInput.value = 'https://oabu.github.io/geosite2surge/';
        showToast('已应用 GitHub Pages 基准 URL');
      }} else if (type === 'jsdelivr') {{
        baseUrlInput.value = 'https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/';
        showToast('已应用 jsDelivr CDN 基准 URL');
      }} else if (type === 'raw') {{
        baseUrlInput.value = 'https://raw.githubusercontent.com/oabu/geosite2surge/release/';
        showToast('已应用 GitHub Raw 基准 URL');
      }}
      localStorage.setItem('surge_rules_base_url', baseUrlInput.value);
      renderGrid();
    }}

    function resetBaseUrl() {{
      baseUrlInput.value = computeDefaultBaseUrl();
      localStorage.setItem('surge_rules_base_url', baseUrlInput.value);
      showToast('已重置为当前网页基准 URL');
      renderGrid();
    }}

    // 3. Filtering & Sorting
    function getFilteredList() {{
      const q = currentQuery.toLowerCase().trim();
      let list = RAW_RULES.filter(item => {{
        if (currentTab === 'geosite' && item.type !== 'geosite') return false;
        if (currentTab === 'geoip' && item.type !== 'geoip') return false;
        if (currentTab === 'favorites' && !favorites.has(item.id)) return false;

        if (!q) return true;
        return (
          item.name.toLowerCase().includes(q) ||
          item.desc.toLowerCase().includes(q) ||
          item.id.toLowerCase().includes(q)
        );
      }});

      list.sort((a, b) => {{
        if (currentSort === 'popular') {{
          if (a.popular !== b.popular) return b.popular ? 1 : -1;
          return a.name.localeCompare(b.name);
        }}
        if (currentSort === 'name_asc') return a.name.localeCompare(b.name);
        if (currentSort === 'name_desc') return b.name.localeCompare(a.name);
        if (currentSort === 'rules_desc') return b.rules - a.rules;
        if (currentSort === 'rules_asc') return a.rules - b.rules;
        return 0;
      }});

      return list;
    }}

    function updateCounts() {{
      document.getElementById('countAll').textContent = RAW_RULES.length;
      document.getElementById('countGeosite').textContent = RAW_RULES.filter(x => x.type === 'geosite').length;
      document.getElementById('countGeoip').textContent = RAW_RULES.filter(x => x.type === 'geoip').length;
      document.getElementById('countFav').textContent = favorites.size;
    }}

    // 4. Render Grid
    function renderGrid() {{
      const container = document.getElementById('rulesList');
      const filtered = getFilteredList();
      const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));

      if (currentPage > totalPages) currentPage = totalPages;
      const startIdx = (currentPage - 1) * PAGE_SIZE;
      const pageItems = filtered.slice(startIdx, startIdx + PAGE_SIZE);

      updateCounts();

      if (pageItems.length === 0) {{
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">📂</div>
            <h3>没有找到符合条件的规则集</h3>
            <p style="margin-top: 6px; font-size: 13px;">请尝试更换关键词，或者切换其他分类查看。</p>
          </div>
        `;
        document.getElementById('pageInfo').textContent = '第 0 / 0 页';
        document.getElementById('prevPageBtn').disabled = true;
        document.getElementById('nextPageBtn').disabled = true;
        return;
      }}

      const base = getBaseUrl();

      container.innerHTML = pageItems.map(item => {{
        const isFav = favorites.has(item.id);
        const fullUrl = base + item.file;
        const typeBadge = item.type === 'geosite'
          ? '<span class="badge badge-geosite">GeoSite</span>'
          : '<span class="badge badge-geoip">GeoIP</span>';

        return `
          <div class="rule-row" data-id="${{item.id}}">
            <div class="row-left">
              <button class="star-btn ${{isFav ? 'active' : ''}}" onclick="toggleFavorite('${{item.id}}')" title="收藏/取消收藏">
                ${{isFav ? '★' : '☆'}}
              </button>
              <div class="row-info">
                <div class="row-top-line">
                  <span class="row-title">${{item.name}}.list</span>
                  ${{typeBadge}}
                  <span class="badge badge-rules">${{item.rules.toLocaleString()}} 规则</span>
                  <span class="row-desc" title="${{item.desc}}">${{item.desc}}</span>
                </div>
                <div class="row-bottom-line">
                  <span class="row-url" title="访问直达 URL">${{fullUrl}}</span>
                </div>
              </div>
            </div>

            <div class="row-actions">
              <button class="action-btn" onclick="copyText('${{fullUrl}}', '已复制规则集 URL')">
                📋 复制 URL
              </button>
              <button class="action-btn action-btn-primary" onclick="copySurgeRule('${{fullUrl}}')">
                ⚡ 复制 Surge 规则
              </button>
              <a href="${{fullUrl}}" target="_blank" class="action-btn" style="flex: 0 0 36px; padding: 6px;" title="在新标签页中打开">
                ↗️
              </a>
            </div>
          </div>
        `;
      }}).join('');

      document.getElementById('pageInfo').textContent = `第 ${{currentPage}} / ${{totalPages}} 页 (共 ${{filtered.length}} 项)`;
      document.getElementById('prevPageBtn').disabled = currentPage <= 1;
      document.getElementById('nextPageBtn').disabled = currentPage >= totalPages;
    }}

    // 5. User Interaction Functions
    function setTab(tab) {{
      currentTab = tab;
      currentPage = 1;
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.tab === tab);
      }});
      renderGrid();
    }}

    function onSearchChange() {{
      currentQuery = document.getElementById('searchInput').value;
      currentPage = 1;
      renderGrid();
    }}

    function onSortChange() {{
      currentSort = document.getElementById('sortSelect').value;
      currentPage = 1;
      renderGrid();
    }}

    function changePage(delta) {{
      currentPage += delta;
      renderGrid();
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function toggleFavorite(id) {{
      if (favorites.has(id)) {{
        favorites.delete(id);
        showToast('已取消收藏');
      }} else {{
        favorites.add(id);
        showToast('已添加至收藏');
      }}
      try {{
        localStorage.setItem('surge_rules_favorites', JSON.stringify(Array.from(favorites)));
      }} catch(e) {{}}
      renderGrid();
    }}

    function copySurgeRule(url) {{
      const policy = url.includes('geoip/cn') || url.includes('geosite/cn') ? 'DIRECT' : (url.includes('ads') ? 'REJECT' : 'PROXY');
      const surgeSnippet = `RULE-SET,${{url}},${{policy}}`;
      copyText(surgeSnippet, `已复制 Surge 规则 (默认策略: ${{policy}})`);
    }}

    function copyText(text, msg) {{
      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(text).then(() => showToast(msg)).catch(() => fallbackCopy(text, msg));
      }} else {{
        fallbackCopy(text, msg);
      }}
    }}

    function fallbackCopy(text, msg) {{
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.left = "-999999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {{
        document.execCommand('copy');
        showToast(msg);
      }} catch (err) {{
        showToast('复制失败，请手动选择复制');
      }}
      document.body.removeChild(textArea);
    }}

    let toastTimer = null;
    function showToast(msg) {{
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {{
        t.classList.remove('show');
      }}, 2200);
    }}

    // Initial render
    renderGrid();
  </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[✓] Generated interactive web catalog: {output_html_path} ({len(items)} items)")
    return output_html_path
