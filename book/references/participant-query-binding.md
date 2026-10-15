# 参与者查询与跨域角色绑定

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

默认查询以 APP 主键唯一定位一个参与者。角色先读取角色自身记录，再沿 take 关系递归查询根角色或实体。跨域实体通过所属域提供的主键查询服务读取；所得事实按 take 映射补全角色，入口实例不替换。查询不产生业务返回值，未查到设置确认失败。循环扮演、歧义主键服务及不匹配的参数在生成期报错。

本域非主键查询由 APP repository 直接实现，现有 repository 条件声明作为可生成的 APP 查询实现保留，不另写 bind；本轮不引入完整 MyBatis SQL/XML 方言。

外域非主键查询用简洁目标绑定：

```app
bind importCatalogue to product.listCatalogue;
```

服务参数数量、集合维度和角色必须对应。相同的跨域 Reference 身份直接对应；不同参与者必须有显式 take 关系，使本地参与者扮演外域所需角色。参数转换调用生成的扮演映射，不按同名字段交集猜测。集合身份依据提供方 APP 主键；查询输出集合可以补入查询到的成员，已有成员及集合容器保持实例稳定。

Petstore 展示 Goods 扮演产品域 CatalogProduct、Buyer/Merchant 扮演客户域 CustomerSubject。原 positional facts/identity 块保留旧项目兼容，但演示改用简洁 bind。产品及客户域补充根实体表和主键查询，普通本域角色持久化同步保存其有表映射的本域实体；不会因为扮演外域实体自动执行跨域写入。实体更新沿可靠查询基线提交，量子事实不进入普通记录。

和传统方案相比，查询条件、SQL 与部署位于 APP/PHY；角色属性转换位于 SPP take；业务场景无需传技术主键、接收返回对象或编写 DTO 字段复制。代价是必须明确主键、扮演及提供方查询，歧义不能靠编译器猜测解决。

实施顺序：简洁绑定及严格参数校验 → 生成扮演适配 → 递归主键查询及本域实体持久化 → Petstore 样例 → 生成编译与静态检查。不运行回归测试、不连接数据库、不提交上传。
