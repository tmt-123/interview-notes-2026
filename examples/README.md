# 算法补充、代码与边界

[返回算法专题](../10-算法与手撕.md) · [返回总目录](../README.md)

算法专题为全部34个归并条目给出了思路、不变量、复杂度和口述方法；有的条目包含原帖的两道独立口述题。这里补充部分容易套错模板的实现。代码为本库独立编写，不是原面试者提交代码。

## 代码入口

| 文件 | 内容 | 验证状态 |
| --- | --- | --- |
| [interview_algorithms.cpp](interview_algorithms.cpp) | C++17：LRU、random5到random7、尾段也反转的K组链表、十六进制大数乘法、版本号比较、三线程有序执行；main含断言 | 已编写边界断言；本轮环境无g++/clang++/MSVC命令，未本地编译运行 |
| [algorithms.py](algorithms.py) | Python3：嵌套JSON合并、严格小于n的最大数、随机转换、十六进制乘法、三数和计数、最小去重子序列 | 已用确定性穷举/对照检查 |
| [check_algorithms.py](check_algorithms.py) | 对小范围输入做独立暴力基线对照，检查输入不变性、长数及拒绝采样路径 | 执行命令见下 |

```powershell
python examples/check_algorithms.py
```

有C++17编译器的环境可运行（不要定义NDEBUG，否则assert被关闭）：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -pthread examples/interview_algorithms.cpp -o interview_algorithms
./interview_algorithms
```

运行成功无输出。它们是教学实现，不含完整生产服务的并发容器、请求限额或运行时隔离；C++的LRU本身不是线程安全容器。随机转换要求独立、均匀的random5。有限测试不代替算法证明，未列出的题目不要误认为都经过了代码执行验证。

详细答案另有C++、SQL、Lua片段及伪代码用于解释机制，省略的头文件、辅助函数或驱动占位符会在上下文说明。它们按语义核对，未在本轮声称全部编译或连接真实MySQL/Redis运行；表格和数值样例也不代表真实项目压测。

## 六个必须先复述的题意

- **ALG-011**：参考解允许数字重复，不能有前导零，0可表示为单独的0，无解返回空值。原帖例`23121,{2,4,9} -> 22999`。若数字只能用一次，需改用剩余计数。
- **ALG-019**：输入是0..4，输出是0..6。`5*a+b`有25种等概率状态，只接受前21种，每个余数正好3种；剩余4种重采。
- **ALG-021**：布尔与数值分开判断；返回深拷贝的新结构，修改结果不能影响输入。不同类型冲突取第二值是本参考解明确采用的约定。
- **ALG-022**：5个节点、K=3，结果是`3,2,1,5,4`，不是`3,2,1,4,5`。
- **ALG-034**：计数是按下标选择三项，严格小于target；不是三角形问题，也不自动按值去重。
- **ALG-035**：只比较点分隔非负数字版本，不套用完整SemVer规则。去前导零后比长度与字典序，不将超长段转固定整数。

## SQL口述转成代码

“前五个不同工资档位并保留并列员工”（DB-030）：

```sql
WITH ranked AS (
  SELECT id, dept_id, salary,
         DENSE_RANK() OVER (
           PARTITION BY dept_id ORDER BY salary DESC
         ) AS salary_rank
  FROM employee
  WHERE salary IS NOT NULL
)
SELECT id, dept_id, salary
FROM ranked
WHERE salary_rank <= 5
ORDER BY dept_id, salary DESC, id;
```

若只要每部门五个人，应改用ROW_NUMBER并明确并列排序规则。这里假设NULL工资不参与排名，表与字段是说明用的示例名称。

“业务键去重并保留最新记录”（DB-029）：

```sql
WITH ranked AS (
  SELECT id, business_key, updated_at,
         ROW_NUMBER() OVER (
           PARTITION BY business_key ORDER BY updated_at DESC, id DESC
         ) AS rn
  FROM records
)
SELECT id, business_key, updated_at
FROM ranked
WHERE rn = 1;
```

这是查询示例，不直接删除生产数据；处理永久重复应补唯一约束与并发写入策略。SQL以MySQL8窗口函数语法为依据，本轮未连接真实MySQL执行。
