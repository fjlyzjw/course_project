# Recipe QAKB 基于知识图谱的菜谱问答系统

本项目主要参考了刘焕勇老师[基于医药领域知识图谱的问答系统](https://github.com/liuhuanyong/QASystemOnMedicalKG)，在下厨房爬取的数据的基础上重新在neo4j上构建了一个新的知识图谱，并且实现了一个简单的自动问答系统。

## 项目最终效果

以下是实际问答运行过程中的截图：

![image](https://user-images.githubusercontent.com/31613437/114520598-31c3ff80-9c74-11eb-9bfe-74c4c0ea4bf0.png)

![image](https://user-images.githubusercontent.com/31613437/114520623-38eb0d80-9c74-11eb-92f6-d14d929d45db.png)

## 性能说明

由于本项目的数据规模十分小，且应用领域非常明确（针对菜谱进行问答），在图谱和问答系统完成后我们对该系统只进行了简单的测试，其回答的准确率大约在65%左右。该系统无法回答的问题举例：我想吃火锅；水煮鱼怎么做；有甜口味的菜吗；有没有胡萝卜的素菜吗；黑椒牛柳可以用白胡椒吗 等。

## 项目运行方式

1. 配置要求：要求配置neo4j数据库及相应的python依赖包。neo4j数据库用户名密码记住，并修改相应文件（build_recipegraph.py和answer_search.py）
2. 知识图谱数据导入：
```
python build_recipegraph.py
```
3. 启动问答：
```
python chatbot_graph.py
```

## 脚本目录
xml2json.py：将爬取到的xml文件进行数据清洗并转为json格式
build_recipegraph.py：知识图谱入库脚本
question_classifier.py：问句类型分类脚本
question_parser.py：问句解析脚本
answer_search.py：从图数据库中搜索相关实体
chatbot_graph.py：问答程序脚本


## 知识图谱的构建

数据来源：从[下厨房](http://www.xiachufang.com/)的‘家常菜’、‘快手菜’等类目中一共爬取1127个菜谱，经过数据筛选、去重、清洗过后，共留下1124条有效菜谱

知识图谱实体类型：

| 实体类型 |	中文含义	| 实体数量 |	举例 |
|---|---|---|---|
|dish|	菜名|	1124	|可乐鸡翅；家常豆腐|
|materials|	食材|	1823	|土豆；鸡胸肉|
|author|	作者|	640	|琉璃爱美食；老丁的私房菜|
|tags|	标签|	1554	|冰箱；减肥|
|total|	总计|	5141	|约五千个实体|


知识图谱实体关系类型：

|实体关系类型|	中文含义|	关系数量|	举例|
|---|---|---|---|
|food_mat|	所需食材|	7044|	<家常豆腐，需要，豆腐>|
|dish_author|	菜品作者|	1124|	<老丁的私房菜，做了，咕咾肉>|
|dish_tag|	菜的标签|	4743|	<家常豆腐，标签，素菜>|
|mate_same|	同种食材|	41|	<土豆，同义于，马铃薯>|
|mate_child|	下属食材|	234|	<鱼，包含了，鲫鱼>|
|total|	总计|	13186|	约一万三千条关系|


知识图谱属性类型

|属性类型|	中文含义|	举例|
|---|---|---|
|name	菜品名称|	可乐鸡翅|
|score|	菜品打分|	8.6|
|heat|	菜品热度|	6741|
|steps|	制作步骤|	将胡萝卜洗干净，切段。苹果洗净后先将胡萝卜榨汁再将苹果榨汁，去渣，混合，搅拌。|
|tips	|小贴士|	建议使用的酱油是金标生抽|
|weburl|	网页链接|	http://www.xiachufang.com/recipe/100451099/|
|qiantity|	食材数量|	50克|
