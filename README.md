# antifraud-rag

**反欺诈 RAG 系统** - 基于 BM25 + 向量搜索 + RRF 融合的 Python 库

## 简介

`antifraud-rag` 是一个专注于欺诈信息识别的 RAG（Retrieval-Augmented Generation）Python 库。通过混合检索策略（BM25 精确匹配 + 向量语义搜索 + RRF 融合排序），结合历史案例库和反诈知识库，输出风险评估分析。

核心特性：
- **混合检索**: BM25 + 向量搜索 + RRF 融合（k=60）
- **双库设计**: 案例库（历史诈骗案件）+ 知识库（反诈技巧文档）
- **PostgreSQL/pgvector**: 高效向量存储和全文搜索
- **异步支持**: SQLAlchemy asyncpg 驱动
- **阈值判定**: RRF score > 0.85 直接返回高危告警

## 安装

```bash
pip install antifraud-rag
```

或使用 `uv`:

```bash
uv pip install antifraud-rag
```

开发安装:

```bash
git clone https://github.com/your-org/antifraud-rag.git
cd antifraud-rag
make install
```

## 环境配置

必需环境变量:

```bash
EMBEDDING_MODEL_URL=https://your-embedding-api.com/v1/embeddings
EMBEDDING_MODEL_API_KEY=your-api-key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

可选配置:

```bash
EMBEDDING_MODEL_NAME=text-embedding-ada-002  # 模型名称
EMBEDDING_DIMENSION=1536                     # 向量维度
HIGH_RISK_THRESHOLD=0.85                     # 高危阈值 (0-1)
```

## 快速开始

### 1. 初始化数据库

```bash
docker-compose up -d
python scripts/init_db.py
```

### 2. 使用 AntiFraudRAG

```python
from antifraud_rag import AntiFraudRAG, Settings
from antifraud_rag.db.session import init_engine, get_session

# 初始化配置
settings = Settings(
    EMBEDDING_MODEL_URL="https://api.example.com/v1/embeddings",
    EMBEDDING_MODEL_API_KEY="your-key",
    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/antifraud"
)

# 初始化数据库引擎
init_engine(settings)

# 创建 RAG 实例
async with get_session() as db:
    rag = AntiFraudRAG(db, settings=settings)
    
    # 分析可疑文本
    result = await rag.analyze("对方声称是公安局，说我涉嫌洗钱...")
    
    # 添加案例到知识库
    case = await rag.add_case(
        description="冒充客服诈骗：对方声称支付宝客服...",
        fraud_type="冒充客服",
        amount=50000,
        keywords=["客服", "退款", "银行卡"]
    )
    
    # 添加反诈知识
    tip = await rag.add_tip(
        title="如何识别冒充公检法诈骗",
        content="公检法机关不会通过电话办案...",
        category="防骗指南",
        keywords=["公检法", "电话办案"]
    )
```

### 3. 检索示例

```python
# 向量搜索
similar_cases = await rag.search_similar_cases(
    query="对方让我转账到安全账户",
    limit=5
)

# 混合搜索（BM25 + 向量 + RRF）
results = await rag.hybrid_search(
    query="可疑的电话诈骗",
    limit=10
)
```

## API 文档

### `AntiFraudRAG` 类

#### `analyze(text: str) -> AnalysisResponse`

分析文本的欺诈风险。

返回类型:
- **Direct_Hit**: 高风险（RRF score ≥ 0.85），直接命中已知案例
- **RAG_Prompt**: 中低风险，返回 RAG prompt 供 LLM 分析

```python
result = await rag.analyze("可疑文本...")
# result.result_type: "Direct_Hit" 或 "RAG_Prompt"
# result.data: DirectHitData 或 RAGPromptData
```

#### `add_case(description, fraud_type=None, amount=None, keywords=None) -> Case`

添加案例到知识库。

```python
case = await rag.add_case(
    description="案例描述",
    fraud_type="电信诈骗",
    amount=10000,
    keywords=["关键词1", "关键词2"]
)
```

#### `add_tip(title, content, category=None, keywords=None) -> Tip`

添加反诈知识。

```python
tip = await rag.add_tip(
    title="标题",
    content="知识内容",
    category="分类",
    keywords=["关键词"]
)
```

#### `search_similar_cases(query, limit=5) -> List[Dict]`

向量搜索相似案例。

#### `hybrid_search(query, limit=10) -> List[Dict]`

混合搜索（BM25 + 向量 + RRF 融合）。

## 架构说明

### 混合检索机制

1. **BM25 检索**: PostgreSQL `tsvector` 全文搜索，精确关键词匹配
2. **向量检索**: pgvector 余弦相似度搜索，语义理解
3. **RRF 融合**: `score = Σ(1/(k+rank))`, k=60

### 数据库设计

**cases_table** (案例库):
- `description`: 案例描述全文
- `fraud_type`: 诈骗类型
- `amount`: 涉案金额
- `embedding`: 1536 维向量
- `content_tsv`: 全文搜索索引

**tips_table** (知识库):
- `title`: 知识标题
- `content`: 知识内容
- `embedding`: 1536 维向量（基于 `title + content`）
- `content_tsv`: 全文搜索索引

### 关键实现

- **Tip embedding**: 使用 `title + " " + content`（与 Case 不同）
- **索引**: IVFFlat (lists=100 for cases, 50 for tips) + GIN
- **分词**: 英文 tokenizer (`to_tsvector('english', ...)`)

## 开发

### 测试

```bash
make test          # 运行 pytest
make test-cov      # 覆盖率报告
make lint          # ruff 检查
make fmt           # 格式化代码
make ci            # lint + test
```

### 项目结构

```
antifraud_rag/
├── main.py              # AntiFraudRAG 核心类
├── schemas.py           # Pydantic 响应模型
├── core/config.py       # Settings 配置
├── db/
│   ├── models.py        # Case, Tip SQLAlchemy 模型
│   └── session.py       # 异步会话管理
└── services/
    ├── retrieval.py     # BM25, 向量搜索, RRF 融合
    ├── embedding.py     # Embedding API 客户端
    └── prompts.py       # Prompt 构建辅助
```

## 依赖

核心依赖:
- `sqlalchemy[asyncio]>=2.0.35`
- `asyncpg>=0.30.0`
- `pgvector==0.2.5`
- `pydantic-settings==2.2.1`
- `httpx==0.27.0`

可选依赖:
- FastAPI: `pip install antifraud-rag[fastapi]`
- 开发工具: `pip install antifraud-rag[dev]`

## 许可证

MIT License

## 参考

- [pgvector](https://github.com/pgvector/pgvector)
- [RRF 融合算法](https://plg.uwaterloo.ca/~gvcormac/cormack-rrf.pdf)