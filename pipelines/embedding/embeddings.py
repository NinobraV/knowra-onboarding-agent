import os
from openai import OpenAI
from typing import List, Dict

# Thiết lập Client (Thay thế <OPENAI_API_KEY> bằng khóa API thực tế của bạn)
# Bạn nên sử dụng biến môi trường để bảo mật khóa API
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<OPENAI_API_KEY_HERE>")) 

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Tạo embeddings cho một danh sách các chuỗi văn bản bằng mô hình text-embedding-3-small.
    """
    try:
        # Tên mô hình được đề xuất trong các nguồn
        model_name = "text-embedding-3-small"
        
        # Gửi yêu cầu tạo embeddings
        # Việc gửi danh sách các chuỗi (batching) hiệu quả hơn là gửi từng chuỗi một [5]
        response = client.embeddings.create(
            model=model_name,
            input=texts
        )
        
        response_dict = response.model_dump()
        
        # Trích xuất các vector embedding từ phản hồi
        # Cấu trúc phản hồi bao gồm 'data', và mỗi phần tử data có khóa 'embedding' [11]
        return [data['embedding'] for data in response_dict['data']]
        
    except Exception as e:
        print(f"Lỗi khi tạo embeddings: {e}")
        return []

# Cần cài đặt chromadb: pip install chromadb
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
# Lưu ý: Client cần được thiết lập đúng với API key của OpenAI

# 1. Kết nối hoặc tạo Persistent Client
# Dữ liệu sẽ được lưu trữ cục bộ trên đĩa [7]
client = chromadb.PersistentClient(path="./vector_db_storage") 

# 2. Định nghĩa Embedding Function
# Phải sử dụng cùng một hàm embedding khi tạo collection và khi truy vấn [20]
embedding_function = OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small", 
    api_key=os.environ.get("OPENAI_API_KEY", "<OPENAI_API_KEY_HERE>")
)

# 3. Tạo Collection (tương tự như Table) [7]
collection = client.get_or_create_collection(
    name="ai_agent_data",
    embedding_function=embedding_function
)

# 4. Thêm tài liệu (ChromaDB sẽ tự động tạo embeddings) [14]
# Giả định chúng ta đã chia file PDF thành 3 chunks
document_chunks = [
    "Đây là đoạn 1 về cách tối ưu hóa embedding.",
    "Đoạn 2 nói về việc sử dụng ChromaDB để lưu trữ vector.",
    "Đoạn 3 bàn luận về các chiến lược làm giàu ngữ cảnh."
]

# Thêm IDs (bắt buộc) [14] và metadata (nếu có) [19]
collection.add(
    ids=["doc1-chunk1", "doc1-chunk2", "doc1-chunk3"],
    documents=document_chunks,
    metadatas=[
        {"source_file": "report.pdf", "page": 1, "topic": "optimization"},
        {"source_file": "report.pdf", "page": 2, "topic": "database"},
        {"source_file": "report.pdf", "page": 3, "topic": "quality"}
    ]
)

print(f"\nSố lượng documents đã lưu: {collection.count()}") # [21]

# 5. Truy vấn dữ liệu (Semantic Search)
query_result = collection.query(
    query_texts=["làm thế nào để cải thiện độ chính xác của tìm kiếm?"], # Văn bản truy vấn
    n_results=1, # Số lượng kết quả gần nhất muốn trả về
    # Có thể lọc bằng metadata [22]
    where={"topic": "quality"} 
)

print("\n--- KẾT QUẢ TRUY VẤN TƯƠNG ĐỒNG NHẤT ---")
# Kết quả trả về một dictionary bao gồm documents, ids, và distances [23, 24]
print(query_result['documents'])
print(f"Khoảng cách (Distance): {query_result['distances']}") 