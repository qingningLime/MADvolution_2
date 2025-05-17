import os
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import ollama

class DeepseekRAG:
    def __init__(self, config):
        """初始化RAG系统"""
        self.embedding_model = "shaw/dmeta-embedding-zh"
        self.deepseek_client = OpenAI(
            api_key=config["ai_auto_processor"]["api_key"],
            base_url=config["ai_auto_processor"]["base_url"]
        )
        self.model = config["ai_auto_processor"]["model"]
        self.vector_db = self._init_vector_db()
        self.current_mode = config["rag"]["default_mode"]
        self.rag_config = config["rag"]
        
        # 初始化提示词缓存
        self.prompt_cache = {}
        if "mad_edit" in config["rag"]["modes"]:
            self._load_prompt_files(config["rag"]["modes"]["mad_edit"]["prompt_files"])
        
    def _init_vector_db(self):
        """初始化向量数据库"""
        client = chromadb.PersistentClient(path="vector_db")
        embedding_func = embedding_functions.OllamaEmbeddingFunction(
            model_name=self.embedding_model
        )
        return client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_func
        )
    
    def process_documents(self, doc_dir="ai分析数据"):
        """处理文档目录中的文件"""
        for filename in os.listdir(doc_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(doc_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 分割文档为段落
                paragraphs = [p for p in content.split("\n\n") if p.strip()]
                
                # 存储到向量数据库
                self.vector_db.add(
                    documents=paragraphs,
                    ids=[f"{filename}_{i}" for i in range(len(paragraphs))]
                )
    
    def set_mode(self, mode):
        """设置当前模式"""
        if mode in self.rag_config["modes"]:
            self.current_mode = mode
        else:
            raise ValueError(f"无效的模式: {mode}")

    def _load_prompt_files(self, prompt_files):
        """加载提示词文件到缓存"""
        for key, filepath in prompt_files.items():
            with open(filepath, "r", encoding="utf-8") as f:
                self.prompt_cache[key] = f.read()

    def query(self, question, top_k=3):
        """查询RAG系统"""
        # 检索相关文档
        results = self.vector_db.query(
            query_texts=[question],
            n_results=top_k
        )
        context = "\n\n".join(results["documents"][0])
        
        # 获取当前模式配置
        mode_config = self.rag_config["modes"][self.current_mode]
        
        # 构建系统消息
        if self.current_mode == "mad_edit":
            system_message = self.prompt_cache.get("system_prompt", "")
            processing_rules = self.prompt_cache.get("processing_rules", "")
            
            system_message += "\n\n处理规则：\n" + processing_rules
            system_message += "\n\n输出格式要求：\n| 时间段 | 歌词内容 | 集数+时间码 | 画面对应的内容|"
        else:
            system_message = mode_config["system_prompt"]
        
        # 调用Deepseek API
        response = self.deepseek_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": f"相关文档内容：\n{context}\n\n问题：{question}"
                }
            ],
            temperature=0.7,
            stream=False
        )
        return response.choices[0].message.content

if __name__ == "__main__":
    # 示例用法
    import json5
    with open("src/config.json", encoding="utf-8") as f:
        config = json5.load(f)
    
    rag = DeepseekRAG(config)
    rag.process_documents()
    
    # 模式选择
    print("请选择模式:")
    print("1. 问答模式")
    print("2. MAD剪辑指导模式")
    mode_choice = input("请输入模式编号(默认1): ").strip()
    if mode_choice == "2":
        rag.set_mode("mad_edit")
        print("已切换到MAD剪辑指导模式")
    else:
        print("使用默认问答模式")
    
    while True:
        question = input("\n请输入您的问题(输入q退出): ")
        if question.lower() == "q":
            break
        print(rag.query(question))
