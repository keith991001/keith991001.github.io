---
title: "Software Architecture Design"
date: 2026-05-21
category: Computer
cover: /assets/images/posts/software-architecture-design/cover.png
---

> 核心思想：用**分层的方式**把软件系统从"宏观到微观"逐步拆解，让不同角色（开发、产品、运维）都能看懂系统结构。

## C4 model

C4 把系统按颗粒度从大到小分四层：Context → Container → Component → Code。

### 1. Context（系统上下文图）

描述"系统在整个环境中的位置"。

- 系统和外部用户/系统的关系
- 回答：这个系统是给谁用的？和哪些外部系统交互？

**画什么**：终端用户、外部系统（API / DB / SaaS）、系统本体（作为一个黑盒）  
**数量**：整个系统只画一张

![C4 Context diagram](/assets/images/posts/software-architecture-design/image1.png)

### 2. Container（容器图）

这里的"容器"不是 Docker，而是"可运行的应用单元"。

- Web 前端
- 后端 API
- 数据库
- 微服务
- 回答：系统由哪些主要部分组成

**画什么**：进程（Next dev、Rails app 等）、数据存储（PostgreSQL、Redis 等）、container 之间的通信协议（HTTP / WS 等）  
**数量**：整个系统只画一张

![C4 Container diagram](/assets/images/posts/software-architecture-design/image2.png)

### 3. Component（组件图）

把某一个容器继续拆分成内部模块。

- 用户服务
- 订单服务
- 支付模块
- 推荐模块
- 回答：每个应用内部怎么组织

**画什么**：主要的模块、service、controller，按职责分组，模块间的依赖方向  
**数量**：按需要画

![C4 Component diagram](/assets/images/posts/software-architecture-design/image3.png)

### 4. Code（代码级图）

最细粒度，通常是类 / 接口级别设计。一般只有在需要详细设计时才画。

### 和 UML 的关系

C4 和 UML 都是建模方法。UML 更严谨复杂，适合详细设计；C4 更简单清晰，适合架构沟通。

> 大多数 team 只画 Context + Container，Component 偶尔出现，Code 几乎不画。

## Sequence Diagram

时序图是 UML 中常用的一种图，用来描述：多个对象/参与者之间，按时间顺序发生的交互过程。属于 UML 的行为图。

### 重点回答

- 谁参与了这个过程？
- 这些参与者之间发了什么消息？
- 这些消息发生的时间顺序是什么？

简单说：**系统是怎么一步一步执行的**。

### 核心元素

- **参与者（Actor / Object）**：通常画在顶部，比如用户、前端、后端服务、DB
- **生命线（Lifeline）**：一条竖直虚线，表示对象存在的时间线
- **消息（Message）**：对象之间的箭头
  - 实线箭头：调用方法 / 请求
  - 虚线箭头：返回结果
- **激活条（Activation）**：细长矩形，表示对象正在执行操作

### 一个典型流程：登录系统

1. 用户输入账号密码
2. 前端发送请求给后端
3. 后端查询数据库
4. 数据库返回结果
5. 后端返回登录结果给前端
6. 前端显示结果

用时序图表示就是一条"从上到下的交互链"。

### 高级元素：alt / opt / loop / par

只画一条直线流程不够——真实系统有分支、循环、并行。这就是 fragments（断片）出场的地方。

![Sequence diagram with alt / opt / loop / par fragments](/assets/images/posts/software-architecture-design/image4.png)

## State Transition Diagram

状态迁移图是 UML 中的一种行为建模图，用来描述：一个对象在生命周期中，如何在不同状态之间切换。

### 重点回答

- 对象有哪些"状态"？
- 什么事件会触发状态变化？
- 状态之间如何切换？

简单说：**系统 / 对象在不同情况下会变成什么样**。

### 核心元素

- **State（状态）**：对象在某一时刻的情况，例如已创建、待支付、已发货、已完成。状态通常是"静态的描述"
- **Event（事件）**：触发状态变化的动作，比如用户支付成功、管理员取消订单、超时未支付
- **Transition（转移）**：状态之间的箭头
- **Action（动作）**：状态变化时执行的操作，例如发货、发通知、更新库存
- **初始 / 终止状态**：初始状态用黑点表示，结束状态用双圈表示

![State transition diagram](/assets/images/posts/software-architecture-design/image5.png)

## Data Flow Diagram

DFD（Data Flow Diagram，数据流图）是一种用于描述系统中数据如何流动和被处理的建模工具，常用于系统分析与需求分析阶段，属于结构分析方法的一部分。

> DFD 回答的核心问题：**数据从哪里来？经过哪些处理？最终去哪里？**

### 四个基本元素

- **External Entity（外部实体）**：系统外部的"数据来源或去向"，例如用户、银行、第三方系统
- **Process（处理过程）**：对数据进行加工或转换，例如登录验证、订单计算、支付处理
- **Data Flow（数据流）**：数据在系统中的流动方向
- **Data Store（数据存储）**：数据保存的地方

### 分层结构

- **0 层（上下文图）**：整个系统作为一个黑盒，只展示系统与外部实体的关系
- **1 层**：拆分系统主要功能模块
- **2 层及以下**：进一步细化每个处理过程

![DFD level 0 (context)](/assets/images/posts/software-architecture-design/image6.png)

![DFD level 1 (decomposed)](/assets/images/posts/software-architecture-design/image7.png)

## Entity-Relationship Diagram

ER 图（实体关系图）是一种用于描述数据结构与数据之间关系的建模工具，常用于数据库设计阶段。ER 图用来回答系统里有哪些数据实体、它们之间是什么关系。

> 简单说：**用图来设计数据库结构**。

### 三大核心元素

- **Entity（实体）**：通常用矩形表示。表示现实中的概念或对象，比如 User、Order、Product
- **Attribute（属性）**：通常用椭圆表示。描述实体的特征，例如用户的用户名、手机号、邮箱；商品的名称、价格、库存
- **Relationship（关系）**：表示实体之间的联系，例如用户"下单"订单、订单"包含"商品

### 关系类型

- **一对一（1:1）**：一个用户对应一个身份证信息
- **一对多（1:N）**：一个用户可以有多个订单（最常见）
- **多对多（M:N）**：一个订单可以包含多个商品；一个商品也可以出现在多个订单中

> 多对多通常会拆成中间表。

![ER diagram example](/assets/images/posts/software-architecture-design/image8.png)
