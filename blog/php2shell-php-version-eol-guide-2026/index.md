---
title_zh: 'PHP2Shell 怎麼修？站長查版本步驟與 PHP 支援終止對照表'
title_en: 'PHP2Shell: A Website Owner Guide to Patching and PHP End-of-Life Dates'
date: 2026-10-25
category_zh: '站長工具'
category_en: 'Webmaster Tools'
readTime_zh: '9 分鐘'
readTime_en: '9 min'
summary_zh: 'PHP2Shell 修補不能只更新 WordPress。本文整理網站實際 PHP 版本的查法、8.2 至 8.5 的修補版本、5.4 至 8.1 的支援終止日期，以及共用主機該向業者確認的事項。另補 PHP 官方 10 月 23 日新增風險提醒，區分版本更新、套件回補與暫時緩解，附可直接貼給主機商的詢問清單。資料查核至 2026 年 10 月 25 日，台北時間。'
summary_en: 'Check the PHP version actually serving your website, compare PHP2Shell fixes and PHP support deadlines, and ask your host for evidence of patched packages and restarted workers. Includes the October 23 follow-up advisory and the limits of temporary mitigations. Verified October 25, 2026, Taipei time.'
cover: '/blog-images/php2shell-php-version-eol-guide-2026-cover.png'
image_credits:
  - { src: 'php2shell-php-version-eol-guide-2026-cover', source: 'PHP 維護概念插畫（AI 生成，非實際事件畫面）', license: 'self-owned' }
keywords: ['PHP2Shell', 'PHP 版本怎麼查', 'PHP EOL', 'PHP 支援終止', 'PHP 8.2 安全更新', 'WordPress PHP 更新', 'CVE-2026-109618', 'CVE-2026-109619', 'CVE-2026-115560']
tags: ['站長工具', '網站安全', 'PHP', 'WordPress']
author: 'TWTools 編輯部'
topic_ref: '2026-10-25:T1'
---

收到 PHP2Shell 警訊，進 WordPress 後台把外掛全部更新，這樣處理完了嗎？還要查網站底下的 PHP。它是執行網站程式的環境，通常由主機商或維運人員管理，更新 CMS 和外掛不會自動替它修補。

先做 3 件事：**查出這個網站實際使用的 PHP 完整版本、確認主機商的修補紀錄、核對更新後的服務確實已重新啟動。** 如果仍使用 PHP 8.1 或更舊分支，還要安排遷移。

> 本文查核至 2026 年 10 月 25 日（台北時間）。PHP 官方 10 月 23 日另有後續風險提醒，已列在第 4 節。表列版本針對 10 月 21 日的兩個漏洞，不代表網站所有安全問題都已排除；後續版本以原廠及套件供應商公告為準。

## 一、PHP2Shell 是什麼？哪些網站需要處理？

PHP2Shell 指的是 **CVE-2026-109618、CVE-2026-109619** 這組 PHP 核心漏洞，兩者的 CVSS v4.0 分數均為 9.2。問題涉及記憶體不足處理與跨請求殘留狀態，可能讓未登入的攻擊者在伺服器上執行程式碼。[TWCERT/CC 已於 10 月 22 日發布通報。](https://www.twcert.org.tw/tw/cp-169-11303-1d68a-1.html)

風險落在 PHP 執行環境。WordPress、Drupal、Joomla 或自行開發的 PHP 網站，都應盤點；沒有安裝特定外掛，不能據此排除。Wiz 研究指出，受影響範圍可回溯到 PHP 5.4，但不同版本、架構與設定可走的攻擊路徑有差異，不能理解成每個網站都能被同一招成功入侵。[Wiz 原始研究](https://www.wiz.io/blog/php2shell-php-rce)

PHP 官方要求盤點的架構包括 PHP-FPM、Apache mod_php、php-cgi、FrankenPHP 與 LiteSpeed。**只要主機仍接受網頁請求並執行 PHP，就應確認修補狀態。** 這也包含平常少用的舊站與子網域。純靜態 HTML 本身沒有 PHP 執行層；但同一主機是否另有 PHP 服務，仍須確認。[PHP 安全公告](https://www.php.net/archive/2026.php#2026-10-21-5)

## 二、PHP 版本怎麼查？先看網站正在跑哪一版

### WordPress：從網站狀態查看

以管理員身分登入後台，依序開啟：

**工具（Tools）→網站狀態（Site Health）→資訊（Info）→伺服器（Server）→PHP 版本（PHP version）。**

介面譯名可能隨語系略有差異。記下完整版本，例如 `8.3.36`，不要只記「PHP 8」或「8.3」。[WordPress 官方文件](https://wordpress.org/documentation/article/site-health-screen/)

### 共用主機：查指定網域的設定

進主機管理面板的 PHP 設定頁，選到要查的網域。面板列出的「可選版本」和網站「目前採用版本」要分開看；有多個網域時，請逐站確認。如果只顯示 8.3 這類分支名稱，向主機商索取完整套件版本及本次修補紀錄。

### 有 SSH：`php -v` 只能作交叉檢查

```bash
php -v
```

這個指令顯示命令列介面（CLI）所用的 PHP。網站可能由另一套 PHP-FPM 或 Apache 模組處理，兩者可以不同。請維運人員核對實際接收網站流量的服務；不要看到 SSH 顯示新版本，就替所有網域打勾。[PHP CLI 文件](https://www.php.net/manual/en/features.commandline.options.php)

`phpinfo()` 也能顯示網頁執行環境，但會揭露設定、路徑及部分環境資訊。一般站長優先使用後台或請主機商確認。確有除錯需要時，僅在有存取控制的環境使用，查完移除；難猜的檔名不構成存取控制。[PHP 手冊](https://www.php.net/manual/en/function.phpinfo.php)

## 三、PHP 修補版本與支援終止日期對照

以下支援期限指 **PHP 專案的上游支援**。Linux 發行版或商業長期支援（LTS）可能有自己的合約與回補政策，須另外確認。

### 目前受支援的 4 個分支

| PHP 分支 | 10/25 維護狀態 | 安全支援結束日期 | 10/21 兩個 CVE 修補版 |
|---|---|---|---|
| 8.5 | 一般維護 | 2029-12-31 | 8.5.12 |
| 8.4 | 一般維護 | 2028-12-31 | 8.4.27 |
| 8.3 | 僅安全修補 | 2027-12-31 | 8.3.36 |
| 8.2 | 僅安全修補 | 2026-12-31 | 8.2.35 |

一般維護包含錯誤與安全修正；轉為安全維護後，主要處理重大安全問題。8.4 的一般維護到 2026-12-31，8.5 到 2027-12-31。[PHP 官方支援表](https://www.php.net/supported-versions.php)

表列四版是 10 月 21 日兩個 CVE 的正式修補版本。使用上游版本者，應安裝該分支已發布的最新修正版；若主機商有套件回補，判定方式見下一段。8.2 雖有本次修正，安全支援將於今年底結束，修補後仍要規劃遷移。[PHP 安全公告](https://www.php.net/archive/2026.php#2026-10-21-5)

PHP 8.6 目前是候選測試版，不應拿來當正式站的升級捷徑。[PHP 8.6 RC4 發布說明](https://www.php.net/archive/2026.php#2026-10-21-6)

### 已終止支援（EOL）的舊分支

| PHP 分支 | 上游支援終止日期 |
|---|---|
| 8.1 | 2025-12-31 |
| 8.0 | 2023-11-26 |
| 7.4 | 2022-11-28 |
| 7.3 | 2021-12-06 |
| 7.2 | 2020-11-30 |
| 7.1 | 2019-12-01 |
| 7.0 | 2019-01-10 |
| 5.6 | 2018-12-31 |
| 5.5 | 2016-07-21 |
| 5.4 | 2015-09-03 |

資料來源：[PHP 已終止支援分支表](https://www.php.net/eol.php)。日期採官方列值，不另推算成台北某個時刻突然停止運作；EOL 代表上游停止支援，程式不會因此自動關機。

本次有一項例外：PHP 安全團隊為 **7.4、8.0、8.1** 提供最小原始碼回補，協助自行編譯或沒有 LTS 供應商的使用者。這沒有恢復這 3 個分支的正常支援，也不能延伸成「8.1 以下都有補丁」。小站長應請主機商處理，不建議照網路片段自行編譯正式主機。[原廠回補說明](https://www.php.net/archive/2026.php#2026-10-21-5)

### 版號比較舊，也可能已回補

回補（backport）是把安全修正放進供應商維護的既有套件，未必把上游版本號改成表列四版。**完整套件版本、供應商安全公告與這兩個 CVE 的修補狀態，要一起看。** 主機商若只回覆「已開 WAF」或「WordPress 已更新」，仍未回答 PHP 是否修補。[Red Hat 本次安全指引](https://access.redhat.com/security/vulnerabilities/RHSB-2026-013)

## 四、10 月 23 日又有提醒：升級後仍要核對設定

PHP 官方另公告 **CVE-2026-115560** 的少見風險組合：`session.serialize_handler` 原設定為 `php_binary` 或 `php_serialize`，程式在執行時以 `ini_set()` 切換成 `php`，之後呼叫 `session_start()`，且 Session 上傳進度功能仍啟用。

官方建議，在下一次例行錯誤修正版發布前，設定：

```ini
session.upload_progress.enabled=0
```

依官方說明，從未在執行時切換上述序列化處理方式的應用，可保留此功能。本篇建議先完成 10 月 21 日修補，再由管理者判斷是否適用。**先前已停用者，應維持停用；尚未修補者不要因這段例外而重新開啟。** 無法判斷自己的程式是否符合條件時，請主機商或開發者確認。本次查核未見官方已發布這個後續問題的正式修補版公告。[10 月 23 日原廠提醒](https://www.php.net/archive/2026.php#2026-10-23-1)

這項設定要由管理者在請求解析前套用，並重啟所有 PHP 工作程序（worker）。把 `ini_set()` 寫在首頁，或只修改 FPM 的 `.user.ini`，不能當成等效處理。[官方技術公告](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp)

要分清楚兩件事：10 月 21 日的版本更新處理原本兩個漏洞；關閉上傳進度只能阻擋特定 Session 路徑。**尚未安裝原本修補的主機，仍須更新。** WAF 或關閉上傳功能，都不能替代 PHP 本體修正。

官方也列出 `memory_limit=-1` 作為無法立即更新時的緩解之一，但它並不完整，取消 PHP 記憶體上限還會帶來資源耗盡風險。這須由管理者配合容器或 cgroup 等外部資源限制評估，站長不要當成一鍵解法自行套用。[OOM 技術公告與緩解限制](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w)

## 五、共用主機問什麼？自管主機怎麼驗收？

如果主機交給業者維護，可以直接傳下面這段，填入自己的網域：

> 請協助確認此網域實際處理網頁請求的 PHP 完整版本與套件版本，並提供 CVE-2026-109618、CVE-2026-109619 的修補公告或回補依據。更新是否已套用至所有服務節點，所有 PHP worker 是否已重新啟動？另外，請確認 PHP 10 月 23 日 CVE-2026-115560 提醒是否適用，以及上傳進度設定的處置。若目前分支已 EOL，請提供升級選項、相容性測試與完成時間。

自管主機則由維運人員負責安裝更新、套用設定及重啟；容器環境要確認實際服務已換成修補後的映像。只下載新套件、只重建映像但沒替換正在跑的容器，都還沒做完。Red Hat 特別提醒要重啟每個 worker，不能只靠 reload。[供應商維運說明](https://access.redhat.com/security/vulnerabilities/RHSB-2026-013)

跨分支升級前，依 [WordPress 官方指引](https://wordpress.org/support/update-php/) 備份網站、更新核心、佈景主題及外掛。本篇建議確認備份包含網站檔案與資料庫，並先在測試環境驗相容性，按網站實際功能檢查登入、表單、圖片上傳、結帳及排程。這份長青指引的版本建議不能取代本次漏洞的修補版對照。

**同分支修補通常較容易安排；跨分支遷移能取得較長的支援時間，但有相容性成本。** 若舊外掛暫時卡住遷移，先向供應商取得現分支可用的修補方案與期限。無法及時修補的對外服務，應由維運人員評估限制存取或暫停服務；不要讓未修補 PHP 無限期留在線上。

## 六、修完之後，還要留意哪些異常？

更新可以封堵漏洞，先前是否已遭入侵仍要另查。建議請維運或資安人員核對更新前後的存取及錯誤紀錄、非預期檔案異動、陌生管理員、異常工作程序或對外連線。發現異常先保留紀錄、時間與檔案證據，再依事件處理程序處置。

PHP 崩潰或記憶體不足訊息都可能有正常原因，單一異常不能直接判定入侵；反過來，**沒有錯誤紀錄也不能證明安全**，官方指出某些路徑可能在寫入日誌前就失敗。[官方診斷限制](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp)

完成這次處置後，把「網站／主機商／PHP 分支／修補依據／下次 EOL」記成維護表，比下次收到警訊再重新找人省事。網站對外內容與搜尋呈現可另用 [TWTools 三軸掃描器](/seo/) 檢查；它不做 PHP 漏洞偵測，也不能替這次修補驗收。

## 常見問題（FAQ）

### WordPress 與外掛都更新了，還要更新 PHP 嗎？

要確認 PHP 本體。PHP2Shell 的兩個原始漏洞在 PHP 執行環境，CMS 與外掛更新不能替代 PHP 修補。共用主機請業者提供完整套件版本與這兩個 CVE 的修補依據。

### PHP 8.3 還在支援期間，為什麼仍要更新？

受支援代表該分支仍會收到修補，不代表所有舊修訂版都安全。10 月 21 日兩個 CVE 的 8.3 分支修補版是 8.3.36；供應商回補套件則依其安全公告判定。還要核對 10 月 23 日的後續設定提醒。

### PHP 8.1 有補丁，是不是可以繼續用？

PHP 8.1 已於 2025-12-31 終止上游支援。本次最小原始碼回補沒有恢復上游支援（含持續安全修補）；商業 LTS 也須確認涵蓋範圍與期限。先修補眼前風險，仍應安排遷移。

### 關閉 Session 上傳進度就能解決 PHP2Shell 嗎？

不能取代 PHP 更新。它能阻擋特定 Session 攻擊路徑，也是 10 月 23 日後續提醒的處理方式，但不涵蓋原本所有漏洞路徑。設定須在請求解析前生效，並重啟所有 worker。

### php -v 顯示修補版，網站就已經修好了嗎？

還不能據此判定。php -v 顯示命令列 PHP，網站可能由另一版本處理。應再核對網站實際服務、所有節點及 worker 已更新，並取得供應商修補紀錄。

---

**主要資料來源**：本文依 [PHP 10/21 安全公告](https://www.php.net/archive/2026.php#2026-10-21-5)、[10/23 後續提醒](https://www.php.net/archive/2026.php#2026-10-23-1)、[支援版本表](https://www.php.net/supported-versions.php)、[EOL 表](https://www.php.net/eol.php)、[TWCERT/CC 通報](https://www.twcert.org.tw/tw/cp-169-11303-1d68a-1.html)、[Wiz 研究](https://www.wiz.io/blog/php2shell-php-rce)、[Red Hat 指引](https://access.redhat.com/security/vulnerabilities/RHSB-2026-013)及 WordPress 官方文件綜整。修補狀態會變更，請以原廠及實際套件供應商的最新公告為準。
