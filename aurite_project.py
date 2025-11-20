"""
Aurite MCP Project Configuration
"""
from aurite import Project, Server

# 创建Aurite项目
project = Project(
    name="csv-data-analysis-agent",
    description="AI Agent for CSV data analysis with natural language queries",
    version="1.0.0"
)

# 创建MCP服务器
server = Server(
    name="csv-analysis-server",
    description="Server for CSV data analysis operations"
)

# 导出项目配置
if __name__ == "__main__":
    print("Aurite Project initialized")
    print(f"Project: {project.name}")
    print(f"Server: {server.name}")





