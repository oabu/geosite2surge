# V2Ray Rules to Surge Ruleset Converter 🚀

[![CI](https://github.com/oabu/geosite2surge/actions/workflows/ci.yml/badge.svg)](https://github.com/oabu/geosite2surge/actions/workflows/ci.yml)
[![Auto Build](https://github.com/oabu/geosite2surge/actions/workflows/auto-build.yml/badge.svg)](https://github.com/oabu/geosite2surge/actions/workflows/auto-build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

将 [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) 中的 `geosite.dat` 和 `geoip.dat` 规则集合完整转换为适用于 [**Surge**](https://nssurge.com) 的规则集（`RULE-SET` / `DOMAIN-SET`）。

每个 GeoSite 类别与每个 GeoIP 国家/服务都会生成一个独立的 `.list` 规则文件，支持直接发布至 GitHub 并通过 GitHub Actions 每天北京时间 07:00 自动从上游同步更新！

---

## ✨ 项目特性

- **完整分类输出**：每个 GeoSite 分类（如 `apple`、`google`、`cn`、`category-ads-all` 等上千个分类）与 GeoIP 集合（如 `cn`、`us`、`telegram`、`cloudflare` 等）均独立输出为 `.list` 规则文件。
- **纯 Python 零依赖**：自研轻量高效的 Protobuf Wire Format 二进制流解码内核，无需安装 `protoc` 或第三方 Python 包，标准库开箱即用。
- **可视化 Web 导航站 (`index.html`)**：
  - 自动生成现代化单页导航站，内置 1,800+ 规则集的分类检索、卡片浏览与规则数量统计。
  - **动态基准 URL 切换**：页面顶部可自由输入云端/CDN/自建域名，所有规则的直达链接与复制内容秒级实时联动。
  - **本地收藏夹**：点击星标可收藏常用规则，数据持久化保存在浏览器 `localStorage` 中。
  - **一键复制**：支持一键复制完整 URL 或复制对应的 Surge 规则配置行（智能适配 DIRECT / PROXY / REJECT 策略）。
  - **直接上传云端**：将 `dist/` 目录直接推送到 GitHub Pages、Cloudflare Pages 或任何静态服务器即可立即拥有专属规则导航站！
- **Surge 格式严谨适配**：
  - `RootDomain` 自动映射为 `DOMAIN-SUFFIX,domain.com`
  - `Full` 自动映射为 `DOMAIN,domain.com`
  - `Plain` 自动映射为 `DOMAIN-KEYWORD,keyword`
  - `Regex` 自动映射为 `URL-REGEX,regex`
  - IPv4 映射为 `IP-CIDR,x.x.x.x/y,no-resolve`
  - IPv6 映射为 `IP-CIDR6,x:x::x/y,no-resolve`
- **去重与自然排序**：自动过滤重复规则，并对规则进行字母序与类型自然排序。
- **GitHub Actions 每日自动化**：北京时间每天早上 07:00 定时执行，自动推送到 `release` 分支与 GitHub Releases，避免仓库 Git 历史膨胀。

---

## 📦 规则订阅地址说明

本项目规则集已正式发布在 GitHub 的 `release` 分支中，提供以下三种可用订阅直链：

| 链接类型 | 订阅 URL 格式 | 说明 |
| :--- | :--- | :--- |
| **GitHub Pages** | `https://oabu.github.io/geosite2surge/geosite/<分类>.list` | 专属在线规则直链与导航中心 |
| **jsDelivr CDN** | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/<分类>.list` | 国内高速 CDN 加速，更新有数小时缓存延迟 |
| **GitHub Raw** | `https://raw.githubusercontent.com/oabu/geosite2surge/release/geosite/<分类>.list` | 官方原始直连，更新即时 |

> 🌐 **在线可视化规则导航站**：[https://oabu.github.io/geosite2surge/](https://oabu.github.io/geosite2surge/) (需在仓库 Settings -> Pages 开启 release 分支托管)

---

## 常用规则速查表

### 常用 GeoSite 规则列表

| 规则名称 | 适用场景 | 规则集订阅链接（以 jsDelivr 为例） |
| :--- | :--- | :--- |
| **cn** | 中国大陆常见域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/cn.list` |
| **geolocation-!cn** | 非中国大陆域名（代理） | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/geolocation-!cn.list` |
| **gfw** | GFWList 屏蔽域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/gfw.list` |
| **category-ads-all** | 广告与隐私追踪域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/category-ads-all.list` |
| **apple** | Apple 服务域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/apple.list` |
| **google** | Google 服务域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/google.list` |
| **telegram** | Telegram 域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/telegram.list` |
| **netflix** | Netflix 域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/netflix.list` |
| **spotify** | Spotify 域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/spotify.list` |
| **bilibili** | 哔哩哔哩域名 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/bilibili.list` |
| **steam** | Steam 游戏平台 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/steam.list` |

### 常用 GeoIP 规则列表

| 规则名称 | 适用场景 | 规则集订阅链接（以 jsDelivr 为例） |
| :--- | :--- | :--- |
| **cn** | 中国大陆 IP 地址段 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/cn.list` |
| **telegram** | Telegram 专用 IP 地址段 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/telegram.list` |
| **cloudflare** | Cloudflare CDN IP 段 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/cloudflare.list` |
| **private** | 局域网私有 IP 地址 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/private.list` |
| **us** | 美国 IP 地址段 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/us.list` |
| **hk** | 香港 IP 地址段 | `https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/hk.list` |

---

## 🛠 Surge 配置示例

在 Surge 的配置文件中，在 `[Rule]` 规则段下引用规则集：

### 白名单模式（推荐）

```ini
[Rule]
# 常见直连进程
PROCESS-NAME,v2ray,DIRECT
PROCESS-NAME,xray,DIRECT
PROCESS-NAME,clash,DIRECT

# 局域网与私网直接放行
RULE-SET,LAN,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/private.list,DIRECT

# 拦截广告
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/category-ads-all.list,REJECT

# Apple / Google 直连或按需走代理
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/apple.list,DIRECT

# 境外代理分流
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/geolocation-!cn.list,PROXY
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/telegram.list,PROXY

# 大陆直连分流
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geosite/cn.list,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/oabu/geosite2surge@release/geoip/cn.list,DIRECT

# 兜底规则（未命中任何规则走代理）
FINAL,PROXY,dns-failed
```

---

## 🚀 部署到 GitHub 自动化指南

1. **创建或推送本仓库至 GitHub**：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/oabu/geosite2surge.git
   git push -u origin main
   ```

2. **开启 GitHub Actions 写权限**：
   - 进入 GitHub 仓库页面。
   - 点击 **Settings** -> **Actions** -> **General**。
   - 滚动到 **Workflow permissions**，勾选 **Read and write permissions** 并点击 **Save**。

3. **手动测试构建**：
   - 点击 **Actions** 选项卡。
   - 选择 **Auto Build & Release Surge Rules**。
   - 点击 **Run workflow** 按钮即可手动触发一次转换与发布。
   - 之后 GitHub Actions 会在每天北京时间 07:00 自动同步并构建最新规则！

---

## 💻 本地运行与命令行使用

无需安装任何第三方库，系统自带 Python 3.8+ 即可直接运行：

### 1. 自动下载最新上游文件并转换

```bash
python3 convert.py --download --output-dir dist
```

执行后，生成的规则将存放在：
- `dist/geosite/`: 所有 GeoSite 分类规则（`.list`）
- `dist/geoip/`: 所有 GeoIP 分类规则（`.list`）

### 2. 使用本地已有 .dat 文件

```bash
python3 convert.py --geosite /path/to/geosite.dat --geoip /path/to/geoip.dat --output-dir dist
```

### 3. 高级命令行参数

```bash
python3 convert.py --help
```

| 参数 | 默认值 | 作用说明 |
| :--- | :--- | :--- |
| `--download` | 否 | 自动从 Loyalsoldier GitHub Release 下载最新的 `geosite.dat` 和 `geoip.dat` |
| `--geosite <path>` | 无 | 指定本地 `geosite.dat` 路径 |
| `--geoip <path>` | 无 | 指定本地 `geoip.dat` 路径 |
| `--output-dir <dir>` | `./dist` | 规则输出目录 |
| `--format <type>` | `ruleset` | 输出格式：`ruleset`（Surge RULE-SET）、`domainset`（DOMAIN-SET）或 `both` |
| `--no-resolve` | True | 在 IP-CIDR 规则后追加 `,no-resolve` 标记，避免触发本地 DNS 解析（推荐） |
| `--disable-no-resolve` | False | 关闭 `,no-resolve` 标记 |
| `--include <names>` | 全部 | 仅导出指定分类（英文逗号隔开，如 `google,apple,cn,netflix`） |
| `--exclude <names>` | 无 | 排除指定分类（英文逗号隔开） |
| `--extension <ext>` | `.list` | 输出文件后缀名（如 `.list` 或 `.txt`） |

---

## 🧪 运行单元测试

```bash
python3 -m unittest discover tests/ -v
```

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。

## 🙏 鸣谢与数据来源

- [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) - 优质的 V2Ray 路由规则增强数据集
- [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) - 社区域名列表数据源
- [v2fly/geoip](https://github.com/v2fly/geoip) - 社区 IP 数据源
- [Surge](https://nssurge.com) - 高性能的网络调试与代理工具
